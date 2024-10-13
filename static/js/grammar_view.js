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
                    
                    window.grammarRecorddefs = data.recorddefs;
                    
                    var convertedData = convertToJstreeFormat(data.grammar_structure);
                    console.log("Converted data:", convertedData);

                    const relativepath = extractFilenameAndParentFolder(file_path);
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

    function customMenu(node) {
        var items = {
            'Create': {
                'separator_before': false,
                'separator_after': true,
                'label': 'Create',
                'action': function (obj) {
                    var newNodeName = prompt('Enter the name of the new node:');
                    if (newNodeName) {
                        var newNode = {
                            text: newNodeName,
                            type: 'field',
                            data: {ID: newNodeName, MAX: '1', MIN: '0'}
                        };
                        var tree = $('#grammar-tree-view').jstree(true);
                        var newNodeId = tree.create_node(node, newNode);
                        if (newNodeId) {
                            tree.edit(newNodeId);
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

        if (node.type === 'field') {
            delete items.Create;
        }

        return items;
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
            modal.hide();
            $('#editNodeModal').remove();
        });

        $('#editNodeModal').on('hidden.bs.modal', function () {
            $(this).remove();
        });
    }
});
