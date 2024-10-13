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

    // ... (keep other helper functions like extractFilenameAndParentFolder, convertToJstreeFormat, formatNodeText, etc.)

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
