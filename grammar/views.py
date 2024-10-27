from django.shortcuts import render
from .models import GrammarNode
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from types import SimpleNamespace
import os
import ast
import shutil
import importlib.util
from django.conf import settings
from pprint import pformat
import json
import traceback

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
    try:
        full_path = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', file_path)
        
        # Load the module
        spec = importlib.util.spec_from_file_location("grammar_module", full_path)
        grammar_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(grammar_module)

        # Extract the structure
        with open(full_path, 'r') as file:
            tree = ast.parse(file.read())
        
        grammar_structure = extract_structure(tree)
        
        # Extract recorddefs
        recorddefs = {}
        if hasattr(grammar_module, 'recorddefs'):
            recorddefs = grammar_module.recorddefs

        return JsonResponse({
            'status': 'success',
            'grammar_structure': grammar_structure,
            'recorddefs': recorddefs
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def extract_recorddefs_from_grammar(grammar_module):
    if hasattr(grammar_module, 'recorddefs'):
        return grammar_module.recorddefs
    return {}

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
    elif isinstance(node, ast.Constant):
        if node.value is None:
            return None  
        elif isinstance(node.value, int):
            return int(node.value)        
        else:
            return str(node.value)
    else:
        return str(node)

@csrf_exempt
def save_grammar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_path = data.get('file_path')
            grammar_structure = data.get('grammar_structure')
            original_file_path = data.get('original_file_path')

            if not file_path or not grammar_structure or not original_file_path:
                return JsonResponse({'status': 'error', 'message': 'Missing file path, grammar structure, or original file path'}, status=400)

            # Get the directory of the original file
            original_dir = os.path.dirname(os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', original_file_path))
            
            # Construct the new file path in the same directory as the original
            new_file_name = os.path.basename(file_path)
            full_path = os.path.join(original_dir, new_file_name)

            # If saving to a new file, copy the original file first
            if file_path != original_file_path:
                shutil.copy2(os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', original_file_path), full_path)

            # Now update the structure in the file
            with open(full_path, 'r') as file:
                content = file.read()

            # Find the start of the structure object
            start = content.index('structure = ')
            
            # Find the end of the structure object
            end = start
            brackets = 0
            in_structure = False
            for i, char in enumerate(content[start:], start):
                if char == '[':
                    brackets += 1
                    in_structure = True
                elif char == ']':
                    brackets -= 1
                if in_structure and brackets == 0:
                    end = i + 1
                    break

            # Convert JSON null to Python None
            def format_structure_as_python_object(structure, indent_level=0):
                """
                Format a given structure as a Python object string with auto-indentation.

                Parameters:
                structure (list): The structure to format (list of dictionaries).
                indent_level (int): The current level of indentation.

                Returns:
                str: The formatted string representation of the structure.
                """
                indent_space = '    '  # Define the indentation space (4 spaces)
                
                def format_item(item, level):
                    formatted_lines = ["{"]
                    for key, value in item.items():
                        # Create the indentation for the current level
                        current_indent = indent_space * (level + 1)
                        if isinstance(value, dict):
                            if key == 'QUERIES':
                                value_str = f"{key}: {{\n" + ",\n".join(f"{current_indent}'{k}': {repr(v)}" for k, v in value.items()) + f"\n{current_indent}}}"
                            else:
                                value_str = f"'{key}': {{\n" + ",\n".join(f"{current_indent}'{k}': {repr(v)}" for k, v in value.items()) + f"\n{current_indent}}}"
                        elif isinstance(value, list):
                            if key in ('SUBTRANSLATION', 'LEVEL'):
                                value_str = f"{key}: [\n" + ",\n".join(f"{current_indent}{format_item(sub_item, level + 1)}" for sub_item in value) + f"\n{current_indent}]"
                            else:
                                value_str = f"'{key}': [\n" + ",\n".join(f"{current_indent}{format_item(sub_item, level + 1)}" for sub_item in value) + f"\n{current_indent}]"
                        else:
                            if key in ('ID', 'MIN', 'MAX'):
                                value_str = f"{key}: {repr(value)}"
                            else:
                                value_str = f"'{key}': {repr(value)}"
                        formatted_lines.append(f"{current_indent}{value_str},")
                    formatted_lines.append(f"{indent_space * level}}}")
                    return "\n".join(formatted_lines)

                formatted_lines = ["["]
                for item in structure:
                    formatted_lines.append(format_item(item, indent_level))
                formatted_lines.append("]")
                return "\n".join(formatted_lines)

            #print(json.dumps(grammar_structure))
            # Parse JSON into an object with attributes corresponding to dict keys.
            #grammar_structure = json.loads(json.dumps(grammar_structure))
            grammar_structure = format_structure_as_python_object(grammar_structure)
            # Format the grammar structure with proper indentation
            #formatted_structure = pformat(grammar_structure, indent=4, width=120)

            # Ensure the structure is on a new line and indented
            structure_str = 'structure = \\\n' + '\n'.join('    ' + line for line in grammar_structure.split('\n'))

            # Replace the entire structure object with the new content
            new_content = content[:start] + structure_str + content[end:]

            with open(full_path, 'w') as file:
                file.write(new_content)

            return JsonResponse({'status': 'success', 'message': 'Grammar saved successfully', 'new_path': os.path.relpath(full_path, os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars'))})
        except Exception as e:
            import traceback
            return JsonResponse({'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def list_grammar_files_ajax(request):
    grammar_root = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars')
    grammar_tree = build_grammar_tree(grammar_root)
    return JsonResponse({'grammar_tree': json.dumps(grammar_tree)})

@csrf_exempt
def save_recorddefs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_path = data.get('file_path')
            relativePath = data.get('relativePath')
            recorddefs = data.get('recorddefs')

            if not file_path or recorddefs is None:
                return JsonResponse({'status': 'error', 'message': 'Missing file path or recorddefs'}, status=400)

            full_path = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', file_path)

            # Read the current file content
            with open(full_path, 'r') as file:
                content = file.read()

                        # Check if the recorddefs variable exists in the current file
            if 'recorddefs = ' not in content:
                # Logic to handle the case where recorddefs is not found
                # You can return a response indicating that the user needs to make a choice
                return JsonResponse({
                    'status': 'prompt',
                    'message': 'The recorddefs variable is not found in the current file (' + relativePath + '). Do you want to: ',
                    'options': [
                        {'action': 'update_path', 'description': 'Update the file path to the original file'},
                        {'action': 'save_here', 'description': 'Save the recorddefs in the current file'}
                    ]
                })
            
            # Find the start and end of the recorddefs object
            start = content.index('recorddefs = ')
            # Find the end of the recorddefs object
            end = start
            brackets = 0
            in_structure = False
            for i, char in enumerate(content[start:], start):
                if char == '{':
                    brackets += 1
                    in_structure = True
                elif char == '}':
                    brackets -= 1
                if in_structure and brackets == 0:
                    end = i + 1
                    break

            # Convert JSON null to Python None
            def json_to_python(obj):
                if isinstance(obj, dict):
                    return {k: json_to_python(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [json_to_python(item) for item in obj]
                elif obj is None:
                    return None
                else:
                    return obj

            recorddefs = json_to_python(recorddefs)

            # Format the new recorddefs
            formatted_recorddefs = pformat(recorddefs, indent=4, width=120)
            new_recorddefs = f"recorddefs = \\\n{formatted_recorddefs}\n"

            # Replace the old recorddefs with the new one
            new_content = content[:start] + new_recorddefs + content[end:]

            # Write the updated content back to the file
            with open(full_path, 'w') as file:
                file.write(new_content)

            return JsonResponse({'status': 'success', 'message': 'Recorddefs saved successfully'})
        except Exception as e:
            import traceback
            return JsonResponse({'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# Don't forget to add this view to your urls.py file

@csrf_exempt
def save_recorddefs_in_current_file(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_path = data.get('file_path')
            relativePath = data.get('relativePath')
            recorddefs = data.get('recorddefs')
            print(relativePath)
            print(recorddefs)
            if not file_path:
                return JsonResponse({'status': 'error', 'message': 'Missing file path'}, status=400)

            full_path = os.path.join(settings.BASE_DIR, 'bots', 'usersys', 'grammars', file_path)

            # Read the current file content
            with open(full_path, 'r') as file:
                content = file.read()
            
            # Convert JSON null to Python None
            def json_to_python(obj):
                if isinstance(obj, dict):
                    return {k: json_to_python(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [json_to_python(item) for item in obj]
                elif obj is None:
                    return None
                else:
                    return obj

            recorddefs = json_to_python(recorddefs)
            
            # Format the new recorddefs
            formatted_recorddefs = pformat(recorddefs, indent=4, width=120)
            new_recorddefs = f"\nrecorddefs = \\\n{formatted_recorddefs}\n\n"

            # Replace the old recorddefs with the new one
            new_content = content + new_recorddefs

            # Write the updated content back to the file
            with open(full_path, 'w') as file:
                file.write(new_content)

            return JsonResponse({'status': 'success', 'message': 'Recorddefs saved successfully'})
        except Exception as e:
            import traceback
            return JsonResponse({'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def create_grammar(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from request
            data = json.loads(request.body)
            
            # Extract required fields
            file_path = data.get('file_path')
            node_name = data.get('node_name')
            grammar_structure = data.get('grammar_structure')
            file_content = data.get('file_content')
            
            # Validate required fields
            if not node_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Node name is required'
                })
            
            if not file_path:
                return JsonResponse({
                    'status': 'error',
                    'message': 'File path is required'
                })
            
            # Ensure the file path is absolute
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.BASE_DIR, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the new grammar file
            with open(file_path, 'w') as f:
                f.write(file_content)
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'Grammar created successfully',
                'new_path': file_path
            })
            
        except Exception as e:
            # Return error response with traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
    
    # Return error for non-POST requests
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    })
