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
            dataType: 'json',
            success: function(data) {
                console.log("Import success:", data);
                if (data.status === 'success') {
                    console.log("Structure object:", data.grammar_structure);
                    console.log("Recorddefs object:", data.recorddefs);
                    
                    // Store the recorddefs data
                    //$('#grammar-tree-view').data('recorddefs', data.recorddefs);
                    // Store the recorddefs data as a global variable
                    window.grammarRecorddefs = data.recorddefs;
                    
                    var convertedData = convertToJstreeFormat(data.grammar_structure);
                    console.log("Converted data:", convertedData);
                    // Function to extract the filename and its parent folder


                    // Example usage
                    const relativepath = extractFilenameAndParentFolder(file_path);
                    console.log(relativepath); // Output: { relativepath: 'edifact\DESADVD96AUNEAN005.py'}
                    
                    $('#grammar-view').html('<h4>Imported Grammar: ' + relativepath + '</h4><div id="grammar-tree-view"></div>');
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
                    }).on('select_node.jstree', function (e, data) {
                        displayNodeInfo(data.node);
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

    function extractFilenameAndParentFolder(path) {
        const segments = path.split('\\'); // Split the path by backslashes
        const filename = segments.pop(); // Get the last segment (filename)
        const parentFolder = segments.pop(); // Get the second last segment (parent folder)
        
        return parentFolder+"\\"+filename;
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
                if (node.data.MAX === undefined) node.data.MAX = '1';
                if (node.data.MIN === undefined) node.data.MIN = '0';

                if (key === 'LEVEL' || value.LEVEL) {
                    node.type = 'record';
                    node.children = convertToJstreeFormat(value.LEVEL || value, node.id);
                    if (value.LEVEL) {
                        delete node.data.LEVEL;
                    }
                }

                // Handle QUERIES and SUBTRANSLATION
                if (value.QUERIES) {
                    node.data.QUERIES = value.QUERIES;
                }
                if (value.SUBTRANSLATION) {
                    node.data.SUBTRANSLATION = value.SUBTRANSLATION;
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
        if (node.data.QUERIES) text += ` | QUERIES: ${JSON.stringify(node.data.QUERIES).substring(0, 20)}...`;
        if (node.data.SUBTRANSLATION) text += ` | SUBTRANSLATION: ${JSON.stringify(node.data.SUBTRANSLATION).substring(0, 20)}...`;
        return text;
    }

    function editNode(node) {
        let modalHtml = `
        <div class="modal fade" id="editNodeModal" tabindex="-1" aria-labelledby="editNodeModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editNodeModalLabel">Edit Node</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editNodeForm">
                            <div class="mb-3">
                                <label for="nodeType" class="form-label">Type:</label>
                                <select class="form-select" id="nodeType" name="type">
                                    <option value="field">Field</option>
                                    <option value="record">Record</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="nodeId" class="form-label">ID:</label>
                                <input type="text" class="form-control" id="nodeId" name="ID" value="${node.data.ID}">
                            </div>
                            <div class="mb-3">
                                <label for="nodeMax" class="form-label">MAX:</label>
                                <input type="text" class="form-control" id="nodeMax" name="MAX" value="${node.data.MAX}">
                            </div>
                            <div class="mb-3">
                                <label for="nodeMin" class="form-label">MIN:</label>
                                <input type="text" class="form-control" id="nodeMin" name="MIN" value="${node.data.MIN}">
                            </div>
                            <div class="mb-3">
                                <label for="nodeQueries" class="form-label">QUERIES:</label>
                                <textarea class="form-control" id="nodeQueries" name="QUERIES" rows="3">${JSON.stringify(node.data.QUERIES || {}, null, 2)}</textarea>
                            </div>
                            <div class="mb-3">
                                <label for="nodeSubtranslation" class="form-label">SUBTRANSLATION:</label>
                                <textarea class="form-control" id="nodeSubtranslation" name="SUBTRANSLATION" rows="3">${JSON.stringify(node.data.SUBTRANSLATION || [], null, 2)}</textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveNodeBtn">Save</button>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Append modal to body
        $('body').append(modalHtml);

        // Set initial values
        $('#nodeType').val(node.type);

        // Add other attributes dynamically
        for (let key in node.data) {
            if (!['ID', 'MAX', 'MIN', 'QUERIES', 'SUBTRANSLATION', 'LEVEL'].includes(key)) {
                $('#editNodeForm').append(`
                    <div class="mb-3">
                        <label for="node${key}" class="form-label">${key}:</label>
                        <input type="text" class="form-control" id="node${key}" name="${key}" value="${node.data[key]}">
                    </div>
                `);
            }
        }

        if (node.type === 'record' && node.data.LEVEL !== undefined) {
            $('#editNodeForm').append(`
                <div class="mb-3">
                    <label for="nodeLevel" class="form-label">LEVEL:</label>
                    <textarea class="form-control" id="nodeLevel" name="LEVEL" rows="3">${JSON.stringify(node.data.LEVEL, null, 2)}</textarea>
                </div>
            `);
        }

        // Show modal
        let modal = new bootstrap.Modal(document.getElementById('editNodeModal'));
        modal.show();

        // Handle save button click
        $('#saveNodeBtn').click(function() {
            let formData = $('#editNodeForm').serializeArray();
            let updatedData = {...node.data};
            let newType = '';
            formData.forEach(item => {
                if (item.name === 'type') {
                    newType = item.value;
                } else if (item.name === 'QUERIES' || item.name === 'SUBTRANSLATION') {
                    try {
                        updatedData[item.name] = JSON.parse(item.value);
                        // Convert string 'null' to actual null
                        if (updatedData[item.name] === 'null') {
                            updatedData[item.name] = null;
                        }
                    } catch (e) {
                        console.error(`Invalid JSON for ${item.name}:`, e);
                        updatedData[item.name] = item.value;
                    }
                } else {
                    if (item.name === 'MIN' || item.name === 'MAX') {
                        updatedData[item.name] = parseInt(item.value);
                    } else if (item.value === 'null' || item.value === '') {
                        updatedData[item.name] = null;
                    } else {
                        updatedData[item.name] = item.value;
                    }
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
            modal.hide();
            $('#editNodeModal').remove();
        });

        // Remove modal from DOM when hidden
        $('#editNodeModal').on('hidden.bs.modal', function () {
            $(this).remove();
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
            // Ensure QUERIES and SUBTRANSLATION are properly handled
            if (nodeData.QUERIES && typeof nodeData.QUERIES === 'string') {
                try {
                    nodeData.QUERIES = JSON.parse(nodeData.QUERIES);
                } catch (e) {
                    console.error("Error parsing QUERIES:", e);
                }
            }
            if (nodeData.SUBTRANSLATION && typeof nodeData.SUBTRANSLATION === 'string') {
                try {
                    nodeData.SUBTRANSLATION = JSON.parse(nodeData.SUBTRANSLATION);
                } catch (e) {
                    console.error("Error parsing SUBTRANSLATION:", e);
                }
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

    function displayNodeInfo(node) {
        var recorddefs = window.grammarRecorddefs;
        var nodeInfo = $('#node-info');
        nodeInfo.empty();

        console.log("Selected node:", node);
        console.log("Recorddefs:", recorddefs);

        if (recorddefs && node.data && node.data.ID && recorddefs[node.data.ID]) {
            var recordDef = recorddefs[node.data.ID];
            nodeInfo.append('<h4>Record: ' + node.data.ID + '</h4>');
            nodeInfo.append('<table class="table table-bordered"><thead><tr><th>Field Name</th><th>Conditionality</th><th>Dimensions</th><th>Data Type</th><th>Actions</th></tr></thead><tbody></tbody></table>');
            var tbody = nodeInfo.find('tbody');

            recordDef.forEach(function(field, index) {
                if (Array.isArray(field)) {
                    if (field.length === 4) {
                        // Normal field
                        tbody.append(createEditableRow(field, index, false));
                    } else if (field.length === 3) {
                        // Composite field
                        tbody.append('<tr><td colspan="5"><strong>Composite Field: ' + field[0] + '</strong></td></tr>');
                        field.slice(2)[0].forEach(function(subfield, subIndex) {
                            tbody.append(createEditableRow(subfield, index + '-' + subIndex, true));
                        });
                    }
                }
            });

            nodeInfo.append('<button class="btn btn-primary mt-3" id="saveNodeInfo">Save Changes</button>');

            $('#saveNodeInfo').on('click', function() {
                saveNodeInfo(node.data.ID, recordDef);
            });
        } else {
            nodeInfo.append('<p>No detailed information available for this node (ID: ' + (node.data ? node.data.ID : 'unknown') + ').</p>');
        }
    }

    function createEditableRow(field, index, isSubfield) {
        var row = '<tr data-index="' + index + '">' +
            '<td><input type="text" class="form-control" value="' + field[0] + '" data-field="0"></td>' +
            '<td><input type="text" class="form-control" value="' + field[1] + '" data-field="1"></td>' +
            '<td><input type="text" class="form-control" value="' + field[2] + '" data-field="2"></td>' +
            '<td><input type="text" class="form-control" value="' + field[3] + '" data-field="3"></td>' +
            '<td><button class="btn btn-sm btn-danger deleteField">Delete</button></td>' +
            '</tr>';
        return row;
    }

    function saveNodeInfo(nodeId, recordDef) {
        var updatedRecordDef = [];
        $('#node-info tbody tr').each(function() {
            var $row = $(this);
            var index = $row.data('index');
            if (index !== undefined) {
                var field = [];
                $row.find('input').each(function() {
                    field.push($(this).val());
                });
                if (index.toString().includes('-')) {
                    // This is a subfield of a composite field
                    var [parentIndex, subIndex] = index.split('-');
                    if (!updatedRecordDef[parentIndex]) {
                        updatedRecordDef[parentIndex] = [recordDef[parentIndex][0], recordDef[parentIndex][1], []];
                    }
                    updatedRecordDef[parentIndex][2][0][subIndex] = field;
                } else {
                    updatedRecordDef[index] = field;
                }
            }
        });

        // Update the recorddefs
        window.grammarRecorddefs[nodeId] = updatedRecordDef;

        // TODO: Send the updated recorddefs to the server
        console.log("Updated recorddefs:", window.grammarRecorddefs);
        alert("Changes saved locally. Remember to save the grammar file to persist changes.");
    }

    // Add event delegation for delete buttons
    $('#node-info').on('click', '.deleteField', function() {
        $(this).closest('tr').remove();
    });

    // Make sure this event handler is properly set up
    $('#grammar-tree-view').on('select_node.jstree', function (e, data) {
        displayNodeInfo(data.node);
    });
});