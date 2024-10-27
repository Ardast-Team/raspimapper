// Add this at the beginning of the file, after jQuery is loaded
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up CSRF token for all AJAX requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(document).ready(function() {
    console.log("Document ready, initializing jstree");
    console.log("Tree data:", treeData);

    $('#grammar-tree').jstree({
        'core': {
            'data': treeData,
            'themes': {
                'name': 'default',
                'responsive': true
            },
            'check_callback': true  // Add this to allow modifications
        },
        'plugins': ['types', 'contextmenu'],  // Add contextmenu plugin
        'types': {
            'folder': {
                'icon': 'jstree-folder'
            },
            'file': {
                'icon': 'jstree-file'
            }
        },
        'contextmenu': {  // Add contextmenu configuration
            'items': customMenu_repository
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

    function customMenu_repository(node) {
        var items = {
            'NewGrammar': {
                'separator_before': false,
                    'separator_after': false,
                    'label': 'New Grammar',
                    'action': function (obj) {
                        var file_path = node.id;
                        if (node.type === 'folder') {
                            createNewGrammar(file_path);
                        }
                }
            },
            'Import': {
                'separator_before': true,
                    'separator_after': false,
                    'label': 'Import Grammar',
                    'action': function (obj) {
                        var file_path = node.id;
                        if (node.type === 'file') {
                            importGrammar(file_path);
                        }
                    }
                }
        };

        if (node.type === 'file') {
            delete items.NewGrammar;
        }
        if (node.type === 'folder') {
            delete items.Import;
        }
        return items;
    }

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
                    window.grammarStructure = data.grammar_structure;
                    window.grammarRecorddefs = data.recorddefs;
                    
                    var convertedData = convertToJstreeFormat(data.grammar_structure);
                    console.log("Converted data:", convertedData);

                    const relativepath = extractFilenameAndParentFolder(file_path);
                    window.grammarRelativePath = relativepath;
                    console.log(relativepath);
                    
                    $('#grammar-view').html('<h4>Imported Grammar: ' + relativepath + '</h4><div id="grammar-tree-view"></div>');
                    $('#grammar-tree-view').jstree({
                        'core': {
                            'data': convertedData,
                            'check_callback': true,
                            'themes': {
                                'name': 'default',
                                'responsive': true
                            }
                        },
                        'plugins': ['dnd', 'contextmenu', 'wholerow', 'types'],
                        'contextmenu': {
                            'items': customMenu_grammartree
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
        
        return parentFolder + "\\" + filename;
    }

    function convertToJstreeFormat(data, parentKey = 'root') {
        let result = [];
        if (typeof data === 'object' && data !== null) {
            for (let key in data) {
                let value = data[key];
                let node = {
                    text: key,
                    id: `${parentKey}_${key}`,
                    type: 'record',
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

    function customMenu_grammartree(node) {
        var items = {
            'Create': {
                'separator_before': false,
                'separator_after': true,
                'label': 'Create',
                'submenu': {
                    
                    'CreateRecord': {
                        'label': 'Create Record',
                        'action': function (obj) {
                            var tree = $('#grammar-tree-view').jstree(true);
                            var selectedNode = tree.get_node(obj.reference);
                            
                            // Create modal for new record
                            var modalContent = `
                                <div class="modal fade" id="createRecordModal" tabindex="-1">
                                    <div class="modal-dialog">
                                        <div class="modal-content">
                                            <div class="modal-header">
                                                <h5 class="modal-title">Create New Record</h5>
                                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                            </div>
                                            <div class="modal-body">
                                                <form id="createRecordForm">
                                                    <div class="mb-3">
                                                        <label for="recordName" class="form-label">Record Name:</label>
                                                        <input type="text" class="form-control" id="recordName" required>
                                                    </div>
                                                    <div class="mb-3">
                                                        <label for="recordMin" class="form-label">MIN:</label>
                                                        <input type="text" class="form-control" id="recordMin" value="0">
                                                    </div>
                                                    <div class="mb-3">
                                                        <label for="recordMax" class="form-label">MAX:</label>
                                                        <input type="text" class="form-control" id="recordMax" value="1">
                                                    </div>
                                                </form>
                                            </div>
                                            <div class="modal-footer">
                                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                                <button type="button" class="btn btn-primary" id="saveRecordBtn">Create</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;

                            $('body').append(modalContent);
                            var modal = new bootstrap.Modal(document.getElementById('createRecordModal'));
                            modal.show();

                            $('#saveRecordBtn').click(function() {
                                var recordName = $('#recordName').val().trim();
                                var recordMin = $('#recordMin').val().trim();
                                var recordMax = $('#recordMax').val().trim();

                                if (recordName) {
                                    var newNode = {
                                        text: recordName,
                                        type: 'record',
                                        data: {
                                            ID: recordName,
                                            MIN: recordMin,
                                            MAX: recordMax,
                                            LEVEL: []
                                        }
                                    };

                                    var tree = $('#grammar-tree-view').jstree(true);
                                    var newNodeId = tree.create_node(selectedNode, newNode);
                                    
                                    if (newNodeId) {
                                        newNode.text = formatNodeText(newNode);
                                        tree.rename_node(newNodeId, newNode.text);
                                        
                                        // Update grammar structure
                                        if (!selectedNode.data.LEVEL) {
                                            selectedNode.data.LEVEL = [];
                                        }
                                        selectedNode.data.LEVEL.push({
                                            ID: recordName,
                                            MIN: recordMin,
                                            MAX: recordMax,
                                            LEVEL: []
                                        });
                                        
                                        updateGrammarStructure(tree);
                                    }

                                    modal.hide();
                                    $('#createRecordModal').remove();
                                } else {
                                    alert('Record Name is required');
                                }
                            });

                            $('#createRecordModal').on('hidden.bs.modal', function () {
                                $(this).remove();
                            });
                        }
                    },
                    'CreateRecorddef': {
                        'label': 'Create Node Information',
                        'action': function (obj) {
                            var tree = $('#grammar-tree-view').jstree(true);
                            var selectedNode = tree.get_node(obj.reference);
                            
                            if (!window.grammarRecorddefs) {
                                window.grammarRecorddefs = {};
                            }
                            
                            if (!window.grammarRecorddefs[selectedNode.data.ID]) {
                                window.grammarRecorddefs[selectedNode.data.ID] = [
                                    ['NewField', 'C', '1', 'AN']
                                ];
                                displayNodeInfo(selectedNode);
                            } else {
                                alert('Node Information already exists for this node');
                            }
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
                    }
                }
            }
        };


        return items;
    }

    // Add this new function to handle creating a new Grammar
    function createNewGrammar(file_path) {
        console.log("Creating new grammar in:", file_path);
        var grammarName = prompt('Enter a name for the new Grammar (without extension):');
        if (grammarName) {
            // Clean the grammar name and ensure it's valid
            grammarName = grammarName.trim();
            
            // Add .py extension if not present
            var fullFileName = grammarName.toLowerCase().endsWith('.py') ? grammarName : grammarName + '.py';
            var baseName = grammarName.replace(/\.py$/i, '');
            
            // Create the initial grammar structure
            var newGrammarStructure = {};
            newGrammarStructure[baseName] = {
                ID: baseName,
                MIN: '1',
                MAX: '1',
                LEVEL: []
            };

            // Set up global variables
            window.grammarStructure = newGrammarStructure;
            window.grammarRecorddefs = {};
            
            // Construct paths
            const parentFolder = file_path.split('\\').pop();
            window.grammarRelativePath = parentFolder + "\\" + fullFileName;
            window.grammarFilepath = file_path + '\\' + fullFileName;
            
            console.log("Grammar Name:", baseName);
            console.log("Grammar Structure:", newGrammarStructure);
            console.log("Grammar Relative Path:", window.grammarRelativePath);
            console.log("Grammar File Path:", window.grammarFilepath);
            
            // Initialize the grammar view
            $('#grammar-view').html('<h4>New Grammar: ' + window.grammarRelativePath + '</h4><div id="grammar-tree-view"></div>');
            
            // Convert and display the structure
            var convertedData = convertToJstreeFormat(newGrammarStructure);
            initializeGrammarTree(convertedData);
            
            // Save the new grammar
            saveNewGrammar(window.grammarFilepath, baseName, newGrammarStructure);
        }
    }

    function saveNewGrammar(file_path, baseName, grammar_structure) {
        // Generate Python code content
        var grammarContent = 'structure = ' + JSON.stringify(grammar_structure, null, 4) + '\n\n';
        grammarContent += 'recorddefs = {}';
        
        // Prepare the save data with explicit node_name
        var saveData = {
            file_path: file_path,
            node_name: baseName,  // Ensure this is set
            grammar_structure: grammar_structure,
            file_content: grammarContent,
            create_new: true,
            root_node: {  // Add explicit root node information
                name: baseName,
                structure: grammar_structure[baseName]
            }
        };

        console.log('Saving new grammar:', saveData);

        $.ajax({
            url: '/grammar/grammar/create/',  // Updated URL to match new path
            method: 'POST',
            data: JSON.stringify(saveData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(data) {
                if (data.status === 'success') {
                    alert('Grammar created successfully');
                    $('#grammar-tree-view').data('original-file-path', file_path);
                    refreshGrammarTree();
                } else {
                    console.error('Creation error:', data);
                    alert('Error creating grammar: ' + (data.message || 'Unknown error'));
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error creating grammar:", jqXHR.responseText);
                try {
                    var errorData = JSON.parse(jqXHR.responseText);
                    alert('Error creating grammar: ' + errorData.message + '\n\nTraceback: ' + errorData.traceback);
                } catch (e) {
                    alert('Error creating grammar: ' + textStatus + ', ' + errorThrown);
                }
            }
        });
    }

    function initializeGrammarTree(convertedData) {
        $('#grammar-tree-view').jstree({
            'core': {
                'data': convertedData,
                'check_callback': true,
                'themes': {
                    'name': 'default',
                    'responsive': true
                }
            },
            'plugins': ['dnd', 'contextmenu', 'wholerow', 'types'],
            'contextmenu': {
                'items': customMenu_grammartree
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
            editNode(nodeObj);
        });
    }

    $('#save-grammar').click(function() {
        var treeData = $('#grammar-tree-view').jstree(true).get_json('#', {flat: false});
        var grammar_structure = window.grammarStructure;
        //var grammar_structure = convertFromJstreeFormat(treeData);
        var recorddefs = window.grammarRecorddefs;

        var original_file_path = $('#grammar-tree-view').data('original-file-path');

        var save_option = confirm('Do you want to overwrite the existing grammar?\nClick OK to overwrite, or Cancel to save as a new file.');

        if (save_option) {
            // Overwrite existing grammar
            try {
                saveGrammar(original_file_path, grammar_structure, recorddefs);
            } catch (e) {
                console.error("Error saving grammar:", e);
            }
        } else {
            // Save as new file
            var new_file_name = prompt('Enter a new name for the grammar file:', 'new_grammar.py');
            if (new_file_name) {
                saveGrammar(new_file_name, grammar_structure, recorddefs);
            }
        }
    });

    function convertFromJstreeFormat(data) {
        var result = [];
        data.forEach(function(node) {
            //var nodeData = {...node.data};
            // Create a new object to ensure the order of properties
            var nodeData = {
                ID: node.data.ID,
                MIN: parseInt(node.data.MIN),
                MAX: parseInt(node.data.MAX),
                QUERIES: node.data.QUERIES,
                SUBTRANSLATION: node.data.SUBTRANSLATION,
                LEVEL: [] // Initialize LEVEL as an empty array
            };
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

    function saveGrammar(file_path, grammar_structure, recorddefs) {
        var original_file_path = $('#grammar-tree-view').data('original-file-path');
        
        // Ensure file has .py extension
        if (!file_path.toLowerCase().endsWith('.py')) {
            file_path += '.py';
        }
        
        // Get the base name from the file path (handle both / and \ separators)
        var baseName = file_path.split(/[/\\]/).pop().replace('.py', '');
        
        // Generate Python code content for the new grammar file
        var grammarContent = 'structure = ' + JSON.stringify(grammar_structure, null, 4) + '\n\n';
        grammarContent += 'recorddefs = ' + JSON.stringify(recorddefs || {}, null, 4);
        
        // Ensure we have a valid structure with the base name as the root node
        var structureWithRoot = {};
        if (!grammar_structure[baseName]) {
            // If the base name is not the root, create a new root structure
            structureWithRoot = {
                [baseName]: {
                    ID: baseName,
                    MIN: '1',
                    MAX: '1',
                    LEVEL: []
                }
            };
            // If there's existing structure, add it to the LEVEL
            if (Object.keys(grammar_structure).length > 0) {
                structureWithRoot[baseName].LEVEL = grammar_structure;
            }
        } else {
            // If the base name is already the root, use the existing structure
            structureWithRoot = grammar_structure;
        }
        
        console.log('Saving grammar to:', file_path);
        console.log('Original file path:', original_file_path);
        console.log('Base name:', baseName);
        console.log('Structure with root:', structureWithRoot);
        
        // Prepare the save data
        var saveData = {
            file_path: file_path,
            grammar_structure: structureWithRoot,
            original_file_path: original_file_path,
            is_new: !original_file_path || original_file_path === file_path,
            recorddefs: recorddefs || {},
            file_content: grammarContent,
            create_new: true,
            node_name: baseName,  // This is the key field that was causing the error
            root_node: {  // Add explicit root node information
                name: baseName,
                structure: structureWithRoot[baseName]
            }
        };

        console.log('Save data:', saveData);

        // Use a different endpoint for new grammars
        var endpoint = saveData.is_new ? '/grammar/grammar/create/' : '/grammar/save/';  // Updated URL

        $.ajax({
            url: endpoint,
            method: 'POST',
            data: JSON.stringify(saveData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(data) {
                if (data.status === 'success') {
                    alert('Grammar saved successfully');
                    $('#grammar-tree-view').data('original-file-path', data.new_path || file_path);
                    var headerText = data.new_path || window.grammarRelativePath;
                    $('h4').text('Imported Grammar: ' + headerText);
                    refreshGrammarTree();
                } else {
                    console.error('Save error:', data);
                    alert('Error saving grammar: ' + (data.message || 'Unknown error'));
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

    function editNode(node) {
        var modalContent = `
            <div class="modal fade" id="editNodeModal" tabindex="-1" aria-labelledby="editNodeModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="editNodeModalLabel">Edit Node</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editNodeForm">
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

        $('body').append(modalContent);

        let modal = new bootstrap.Modal(document.getElementById('editNodeModal'));
        modal.show();

        $('#saveNodeBtn').click(function() {
            let formData = $('#editNodeForm').serializeArray();
            let updatedData = {...node.data};
            formData.forEach(item => {
                if (item.name === 'QUERIES' || item.name === 'SUBTRANSLATION') {
                    try {
                        updatedData[item.name] = JSON.parse(item.value);
                    } catch (e) {
                        console.error(`Invalid JSON for ${item.name}:`, e);
                        updatedData[item.name] = item.value;
                    }
                } else {
                    updatedData[item.name] = item.value;
                }
            });

            let tree = $('#grammar-tree-view').jstree(true);
            node.data = updatedData;
            node.text = formatNodeText(node);
            tree.rename_node(node, node.text);
            tree.redraw_node(node.id);
            updateGrammarStructure(tree);
            modal.hide();
            $('#editNodeModal').remove();
        });

        $('#editNodeModal').on('hidden.bs.modal', function () {
            $(this).remove();
        });
    }

    function updateGrammarStructure(tree) {  
        var grammar_structure = convertFromJstreeFormat(tree.get_json('#', {flat: false}));
        window.grammarStructure = grammar_structure;
        console.log('Updated grammarStructure:', window.grammarStructure);
    }
});

