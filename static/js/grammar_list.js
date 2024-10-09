$(document).ready(function() {
    console.log("Document ready, initializing jstree");
    console.log("Tree data:", treeData);

    $('#grammar-tree').jstree({
        'core': {
            'data': treeData,
            'themes': {
                'name': 'default',
                'responsive': true
            }
        },
        'plugins': ['types'],
        'types': {
            'folder': {
                'icon': 'jstree-folder'
            },
            'file': {
                'icon': 'jstree-file'
            }
        }
    }).on('ready.jstree', function() {
        console.log("jstree is ready");
    }).on('dblclick.jstree', function (e, data) {
        console.log("Double-click event triggered");
        var node = $.jstree.reference(this).get_node($(e.target).closest('.jstree-node'));
        console.log("Node:", node);

        var file_path = node.id;
        var node_type = node.type || (node.original && node.original.type);
        
        console.log("File path:", file_path);
        console.log("Node type:", node_type);
        console.log("Node original data:", node.original);
        
        if (node_type === 'file') {
            importGrammar(file_path);
        }
    });

    function importGrammar(file_path) {
        console.log("Importing grammar:", file_path);
        $.ajax({
            url: '/grammar/import/' + encodeURIComponent(file_path) + '/',
            method: 'GET',
            success: function(data) {
                console.log("Import success:", data);
                if (data.status === 'success') {
                    console.log("Structure object:", data.grammar_structure);
                    var convertedData = convertToJstreeFormat(data.grammar_structure);
                    console.log("Converted data:", convertedData);
                    $('#grammar-view').html('<h3>Imported Grammar: ' + file_path + '</h3><div id="grammar-tree-view"></div>');
                    $('#grammar-tree-view').jstree({
                        'core': {
                            'data': convertedData,
                            'check_callback': function (operation, node, parent, position, more) {
                                if (operation === "create_node") {
                                    console.log("Create node check:", {operation, node, parent, position, more});
                                    return true;  // Allow node creation
                                }
                                return true;  // Allow all other operations
                            },
                            'themes': {
                                'name': 'default',
                                'responsive': true
                            }
                        },
                        'plugins': ['dnd', 'contextmenu', 'wholerow', 'types'],
                        'contextmenu': {
                            'items': customMenu
                        },
                        'types': {
                            'default': {
                                'valid_children': ['default']
                            },
                            'record': {
                                'icon': 'jstree-folder',
                                'valid_children': ['record', 'field']
                            },
                            'field': {
                                'icon': 'jstree-file',
                                'valid_children': []
                            }
                        }
                    }).on('create_node.jstree', function(e, data) {
                        console.log("Node created event:", data);
                    }).on('dblclick.jstree', function (e) {
                        var node = $(e.target).closest('li');
                        var tree = $('#grammar-tree-view').jstree(true);
                        var nodeObj = tree.get_node(node);
                        console.log("Double-clicked node:", nodeObj.text);
                        console.log("Node attributes:", nodeObj.data);
                        editNode(nodeObj);
                    });
                    
                    // Store the original file path
                    $('#grammar-tree-view').data('original-file-path', file_path);
                } else {
                    console.error("Import error:", data.message);
                    alert('Error importing grammar: ' + data.message);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("AJAX error:", textStatus, errorThrown);
                alert('Error importing grammar');
            }
        });
    }

    function convertToJstreeFormat(data, parentKey = 'root') {
        let result = [];
         if (typeof data === 'object' && data !== null) {
            for (let key in data) {
                let value = data[key];
                let node = {
                    text: key,
                    id: `${parentKey}_${key}`,
                    type: 'field',
                    data: {...value}
                };
                
                // Ensure minimum attributes
                if (!node.data.ID) node.data.ID = key;
                if (node.data.MAX === undefined) node.data.MAX = '0';
                if (node.data.MIN === undefined) node.data.MIN = '0';

                if (key === 'LEVEL') {
                    node.type = 'record';
                    node.children = convertToJstreeFormat(value, node.id);
                } else if (value.LEVEL) {
                    node.type = 'record';
                    node.children = convertToJstreeFormat(value.LEVEL, node.id);
                    delete node.data.LEVEL; // Remove LEVEL from data to avoid duplication
                }

                node.text = formatNodeText(node);
                result.push(node);
            }
        }
        return result;
    }

    function formatNodeText(node) {
        let text = ``;
        if (node.data.ID !== undefined) text += `ID: ${node.data.ID}`;
        text += ` (${node.type})`;
        if (node.data.MAX !== undefined) text += ` | MAX: ${node.data.MAX}`;
        if (node.data.MIN !== undefined) text += ` | MIN: ${node.data.MIN}`;
        return text;
    }

    function editNode(node) {
        let form = $('<form>').append(
            $('<label>').text('Type:'),
            $('<select>').attr({name: 'type'}).append(
                $('<option>').attr('value', 'field').text('Field'),
                $('<option>').attr('value', 'record').text('Record')
            ),
            $('<br>'),
            $('<label>').text('ID:'),
            $('<input>').attr({type: 'text', name: 'ID', value: node.data.ID}),
            $('<br>'),
            $('<label>').text('MAX:'),
            $('<input>').attr({type: 'text', name: 'MAX', value: node.data.MAX}),
            $('<br>'),
            $('<label>').text('MIN:'),
            $('<input>').attr({type: 'text', name: 'MIN', value: node.data.MIN})
        );

        // Set the initial value of the type dropdown
        form.find('select[name="type"]').val(node.type);

        // Add other attributes dynamically
        for (let key in node.data) {
            if (!['ID', 'MAX', 'MIN', 'LEVEL'].includes(key)) {
                form.append(
                    $('<br>'),
                    $('<label>').text(key + ':'),
                    $('<input>').attr({type: 'text', name: key, value: node.data[key]})
                );
            }
        }

        if (node.type === 'record' && node.data.LEVEL !== undefined) {
            form.append(
                $('<br>'),
                $('<label>').text('LEVEL:'),
                $('<input>').attr({type: 'text', name: 'LEVEL', value: JSON.stringify(node.data.LEVEL)})
            );
        }

        let dialog = $('<div>').append(form).dialog({
            title: 'Edit Node',
            modal: true,
            width: 350,
            buttons: {
                "Save": function() {
                    let formData = form.serializeArray();
                    let updatedData = {...node.data};
                    let newType = '';
                    formData.forEach(item => {
                        if (item.name === 'type') {
                            newType = item.value;
                        } else if (item.name === 'LEVEL') {
                            try {
                                updatedData[item.name] = JSON.parse(item.value);
                            } catch (e) {
                                console.error("Invalid JSON for LEVEL:", e);
                                updatedData[item.name] = item.value;
                            }
                        } else {
                            updatedData[item.name] = item.value;
                        }
                    });
                    let tree = $('#grammar-tree-view').jstree(true);
                    node.data = updatedData;
                    node.type = newType;
                    node.text = formatNodeText({data: updatedData, type: newType});
                    tree.set_type(node, newType);
                    tree.rename_node(node, node.text);
                    
                    // Update the icon based on the new type
                    if (newType === 'record') {
                        tree.set_icon(node, 'jstree-folder');
                    } else {
                        tree.set_icon(node, 'jstree-file');
                    }
                    
                    tree.redraw_node(node.id);
                    dialog.dialog('close');
                },
                "Cancel": function() {
                    dialog.dialog('close');
                }
            },
            close: function() {
                $(this).dialog('destroy').remove();
            }
        });
    }

    function customMenu(node) {
        var items = {
            'Create': {
                'separator_before': false,
                'separator_after': true,
                'label': 'Create',
                'action': function (obj) {
                    console.log("Create action triggered");
                    console.log("Parent node:", node);
                    var newNodeName = prompt('Enter the name of the new node:');
                    if (newNodeName) {
                        console.log("New node name:", newNodeName);
                        var newNode = {
                            text: newNodeName,
                            type: 'field',
                            data: {ID: newNodeName, MAX: '1', MIN: '0'}
                        };
                        console.log("New node object:", newNode);
                        var tree = $('#grammar-tree-view').jstree(true);
                        try {
                            var newNodeId = tree.create_node(node, newNode);
                            console.log("create_node result:", newNodeId);
                            if (newNodeId) {
                                console.log("Node created with ID:", newNodeId);
                                tree.redraw(true);
                                tree.open_node(node);
                                tree.select_node(newNodeId);
                                setTimeout(function() {
                                    console.log("Editing new node");
                                    editNode(tree.get_node(newNodeId));
                                }, 100);
                            } else {
                                console.error("Failed to create new node: create_node returned", newNodeId);
                                alert("Failed to create new node. Please check the console for more information.");
                            }
                        } catch (error) {
                            console.error("Error creating new node:", error);
                            alert("Error creating new node: " + error.message);
                        }
                    }
                }
            },
            'Edit': {
                'separator_before': false,
                'separator_after': false,
                'label': 'Edit',
                'action': function (obj) {
                    var tree = $('#grammar-tree-view').jstree(true);
                    editNode(tree.get_node(obj.reference));
                }
            },
            'Delete': {
                'separator_before': false,
                'separator_after': false,
                'label': 'Delete',
                'action': function (obj) {
                    if (confirm('Are you sure you want to delete this node?')) {
                        $('#grammar-tree-view').jstree('delete_node', node);
                        $('#grammar-tree-view').jstree(true).redraw(true);
                    }
                }
            }
        };

        if (node.type === 'field') {
            delete items.Create;
        }

        return items;
    }

    $('#save-grammar').click(function() {
        var treeData = $('#grammar-tree-view').jstree(true).get_json('#', {flat: false});
        var grammar_structure = convertFromJstreeFormat(treeData);
        var original_file_path = $('#grammar-tree-view').data('original-file-path');

        var save_option = confirm('Do you want to overwrite the existing grammar?\nClick OK to overwrite, or Cancel to save as a new file.');

        if (save_option) {
            // Overwrite existing grammar
            saveGrammar(original_file_path, grammar_structure);
        } else {
            // Save as new file
            var new_file_name = prompt('Enter a new name for the grammar file:', 'new_grammar.py');
            if (new_file_name) {
                saveGrammar(new_file_name, grammar_structure);
            }
        }
    });

    function convertFromJstreeFormat(data) {
        var result = [];
        data.forEach(function(node) {
            var nodeData = {...node.data};
            if (node.children && node.children.length > 0) {
                nodeData.LEVEL = convertFromJstreeFormat(node.children);
            }
            result.push(nodeData);
        });
        return result;
    }

    function saveGrammar(file_path, grammar_structure) {
        var original_file_path = $('#grammar-tree-view').data('original-file-path');
        $.ajax({
            url: '/grammar/save/',
            method: 'POST',
            data: JSON.stringify({
                file_path: file_path,
                grammar_structure: grammar_structure,
                original_file_path: original_file_path
            }),
            contentType: 'application/json',
            success: function(data) {
                if (data.status === 'success') {
                    alert('Grammar saved successfully');
                    // Update the original file path with the new path
                    $('#grammar-tree-view').data('original-file-path', data.new_path);
                    // Optionally, update the displayed file name
                    $('h3:contains("Imported Grammar:")').text('Imported Grammar: ' + data.new_path);
                    // Refresh the grammar tree
                    refreshGrammarTree();
                } else {
                    alert('Error saving grammar: ' + data.message);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error saving grammar:", jqXHR.responseText);
                try {
                    var errorData = JSON.parse(jqXHR.responseText);
                    alert('Error saving grammar: ' + errorData.message + '\n\nTraceback: ' + errorData.traceback);
                } catch (e) {
                    alert('Error saving grammar: ' + textStatus + ', ' + errorThrown);
                }
            }
        });
    }

    function refreshGrammarTree() {
        $.ajax({
            url: '/grammar/list/',
            method: 'GET',
            success: function(data) {
                var newTreeData = JSON.parse(data.grammar_tree);
                $('#grammar-tree').jstree(true).settings.core.data = newTreeData;
                $('#grammar-tree').jstree(true).refresh();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error refreshing grammar tree:", textStatus, errorThrown);
            }
        });
    }
});