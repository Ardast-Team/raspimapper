from django.shortcuts import render
from .models import GrammarNode
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import ast
from django.conf import settings

def tree_view(request):
    nodes = GrammarNode.objects.all()
    return render(request, 'grammar/tree_view.html', {'nodes': nodes})

def create_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        parent_id = data.get('parent_id')
        
        if name:
            parent = None
            if parent_id:
                parent = GrammarNode.objects.filter(id=parent_id).first()
            
            new_node = GrammarNode.objects.create(name=name, parent=parent)
            return JsonResponse({'status': 'success', 'id': new_node.id, 'name': new_node.name})
        else:
            return JsonResponse({'status': 'error', 'message': 'Node name is required'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def import_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        # Logic to parse the file and create Grammar nodes
        # For example, assuming the file is a simple text file with node names
        for line in file:
            node_name = line.decode('utf-8').strip()
            GrammarNode.objects.create(name=node_name)
        
        return JsonResponse({'status': 'success', 'message': 'File imported successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def export_grammar(request):
    nodes = GrammarNode.objects.all()
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="grammar_file.txt"'
    
    for node in nodes:
        response.write(f"{node.name}\n")  # Customize the format as needed
    
    return response

def list_grammar_files(request):
    grammar_root = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars')
    grammar_tree = build_grammar_tree(grammar_root)
    context = {
        'grammar_tree': json.dumps(grammar_tree),
    }
    return render(request, 'grammar/list_grammars.html', context)

def build_grammar_tree(path):
    tree = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            children = build_grammar_tree(item_path)
            if children:  # Only add non-empty folders
                tree.append({
                    'text': item,
                    'type': 'folder',
                    'children': children,
                    'id': item_path,
                    'li_attr': {'type': 'folder'},  # Add this line
                    'a_attr': {'type': 'folder'}    # Add this line
                })
        elif item.endswith('.py'):
            tree.append({
                'text': item,
                'type': 'file',
                'icon': 'jstree-file',
                'id': item_path,
                'li_attr': {'type': 'file'},  # Add this line
                'a_attr': {'type': 'file'}    # Add this line
            })
    return tree

def import_grammar(request, file_path):
    full_path = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r') as file:
                file_content = file.read()
                tree = ast.parse(file_content)
                structure = extract_structure(tree)
                if structure:
                    return JsonResponse({'status': 'success', 'grammar_structure': structure})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No structure found in the file'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)

def extract_structure(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'structure':
                    return ast_to_dict(node.value)
    return None

def ast_to_dict(node):
    if isinstance(node, ast.Dict):
        return {ast_to_dict(key): ast_to_dict(value) for key, value in zip(node.keys, node.values)}
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.List):
        return [ast_to_dict(elem) for elem in node.elts]
    elif isinstance(node, ast.Name):
        return node.id
    else:
        return str(node)

@csrf_exempt
def save_grammar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_path = data.get('file_path')
        grammar_structure = data.get('grammar_structure')

        if not file_path or not grammar_structure:
            return JsonResponse({'status': 'error', 'message': 'Missing file path or grammar structure'}, status=400)

        full_path = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', file_path)

        try:
            with open(full_path, 'r') as file:
                content = file.read()

            # Find the start and end of the structure object
            start = content.index('structure = ')
            end = content.index('\n', start)
            while content[end-1] == '\\':
                end = content.index('\n', end+1)

            # Replace the structure object
            new_content = (
                content[:start] +
                f"structure = {json.dumps(grammar_structure, indent=4)}" +
                content[end:]
            )

            with open(full_path, 'w') as file:
                file.write(new_content)

            return JsonResponse({'status': 'success', 'message': 'Grammar saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)