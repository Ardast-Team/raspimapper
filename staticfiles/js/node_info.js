function displayNodeInfo(node) {
    var recorddefs = window.grammarRecorddefs;
    var nodeInfo = $('#node-info');
    nodeInfo.empty();

    console.log("Selected node:", node);
    console.log("Recorddefs:", recorddefs);

    if (recorddefs && node.data && node.data.ID && recorddefs[node.data.ID]) {
        var recordDef = recorddefs[node.data.ID];
        nodeInfo.append('<h4>Record: ' + node.data.ID + '</h4><div id="node-info-tree"></div>');
        
        var treeData = [];
        recordDef.forEach(function(field, index) {
            if (Array.isArray(field)) {
                if (field.length === 4) {
                    // Normal field
                    treeData.push({
                        id: 'field_' + index,
                        text: field[0] + ' (Field, ' + field[1] + ', ' + field[2] + ', ' + field[3] + ')',
                        type: 'field',
                        name: field[0],
                        conditionality: field[1],
                        dimensions: field[2],
                        dataType: field[3]
                    });
                } else if (field.length === 3) {
                    // Composite field
                    var compositeNode = {
                        id: 'composite_' + index,
                        text: field[0] + ' (Composite, ' + field[1] + ')',
                        type: 'composite',
                        name: field[0],
                        conditionality: field[1],
                        children: []
                    };
                    field[2].forEach(function(subfield, subIndex) {
                        compositeNode.children.push({
                            id: 'subfield_' + index + '_' + subIndex,
                            text: subfield[0] + ' (Subfield, ' + subfield[1] + ', ' + subfield[2] + ', ' + subfield[3] + ')',
                            type: 'subfield',
                            name: subfield[0],
                            conditionality: subfield[1],
                            dimensions: subfield[2],
                            dataType: subfield[3]
                        });
                    });
                    treeData.push(compositeNode);
                }
            }
        });

        $('#node-info-tree').jstree({
            'core': {
                'data': treeData,
                'check_callback': true,
                'themes': {
                    'name': 'default',
                    'responsive': true
                }
            },
            'plugins': ['dnd', 'types', 'contextmenu'],
            'types': {
                'field': {
                    'icon': 'jstree-file'
                },
                'composite': {
                    'icon': 'jstree-folder'
                },
                'subfield': {
                    'icon': 'jstree-file'
                }
            },
            'contextmenu': {
                'items': nodeInfoContextMenu
            }
        }).on('move_node.jstree rename_node.jstree create_node.jstree delete_node.jstree', function (e, data) {
            console.log('Tree changed:', e.type, data);
            updateRecorddefs(data.instance);
        }).on('dblclick.jstree', function (e) {
            var node = $(e.target).closest('li');
            var tree = $('#node-info-tree').jstree(true);
            var nodeObj = tree.get_node(node);
            console.log('Node Obj double-clicked:', nodeObj);
            editNodeInfoField(nodeObj);
        });

        nodeInfo.append('<button id="saveNodeInfo" class="btn btn-primary mt-3">Save Changes</button>');

        $('#saveNodeInfo').on('click', function() {
            var tree = $('#node-info-tree').jstree(true);
            var updatedTreeData = tree.get_json('#', {flat: false});
            var updatedRecorddefs = jstreeToRecorddefs(updatedTreeData);
            
            window.grammarRecorddefs[node.data.ID] = updatedRecorddefs[Object.keys(updatedRecorddefs)[0]];

            saveRecorddefs(window.grammarRecorddefs);
        });
    } else {
        nodeInfo.append('<p>No detailed information available for this node (ID: ' + (node.data ? node.data.ID : 'unknown') + ').</p>');
    }
}

function editNodeInfoField(node, isNew = false) {
    // ... (keep the existing editNodeInfoField function)
}

function parseNodeText(text) {
    var match = text.match(/^(.+?) \((.+?), (.+?), (.+?)\)$/);
    if (match) {
        return {
            name: match[1],
            conditionality: match[2],
            dimensions: match[3],
            dataType: match[4]
        };
    }
    // Handle composite fields
    var compositeMatch = text.match(/^(.+?) \(Composite\)$/);
    if (compositeMatch) {
        return {
            name: compositeMatch[1],
            conditionality: 'C',
            dimensions: '',
            dataType: ''
        };
    }
    // Default case if no match is found
    return {
        name: text,
        conditionality: '',
        dimensions: '',
        dataType: ''
    };
}

function saveRecorddefs(recorddefs) {
    // ... (keep the existing saveRecorddefs function)
}

function updateRecorddefs(treeInstance) {
    // ... (keep the existing updateRecorddefs function)
}

function nodeInfoTreeToRecorddef(treeData) {
    // ... (keep the existing nodeInfoTreeToRecorddef function)
}

function nodeInfoContextMenu(node) {
    // ... (implement the context menu for node info tree)
}

// Add any other helper functions needed for node info handling
