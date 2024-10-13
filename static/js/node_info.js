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
                        type: 'field',
                        text: field[0] + ' (field, ' + field[1] + ', ' + field[2] + ', ' + field[3] + ')',
                        name: field[0],
                        conditionality: field[1],
                        dimensions: field[2],
                        dataType: field[3]
                    });
                } else if (field.length === 3) {
                    // Composite field
                    var compositeNode = {
                        id: 'composite_' + index,
                        type: 'composite',
                        text: field[0] + ' (composite, ' + field[1] + ')',
                        name: field[0],
                        conditionality: field[1],
                        children: []
                    };
                    field[2].forEach(function(subfield, subIndex) {
                        compositeNode.children.push({
                            id: 'subfield_' + index + '_' + subIndex,
                            type: 'subfield',
                            text: subfield[0] + ' (subfield, ' + subfield[1] + ', ' + subfield[2] + ', ' + subfield[3] + ')',
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
            //console.log('Node Obj double-clicked:', nodeObj);
            editNodeInfoField(nodeObj,false);
        });

        nodeInfo.append('<button id="saveNodeInfo" class="btn btn-primary mt-3">Save Changes</button>');

        $('#saveNodeInfo').on('click', function() {
            var tree = $('#node-info-tree').jstree(true);
            var updatedTreeData = tree.get_json('#', {flat: false});
            //var updatedRecorddefs = jstreeToRecorddefs(updatedTreeData);
            var updatedRecorddefs = nodeInfoTreeToRecorddef(updatedTreeData);

            window.grammarRecorddefs[node.data.ID] = updatedRecorddefs[Object.keys(updatedRecorddefs)[0]];

            saveRecorddefs(window.grammarRecorddefs);
        });
    } else {
        nodeInfo.append('<p>No detailed information available for this node (ID: ' + (node.data ? node.data.ID : 'unknown') + ').</p>');
    }
}

function editNodeInfoField(node, isNew) {
    var nodeData = parseNodeText(node.text);
    var isField = node.type === 'field';
    var isComposite = node.type === 'composite';
    var isSubfield = node.type === 'subfield';

    // Log node attributes to console
    console.log('Node double-clicked:', nodeData);

    var modalContent = `
        <div class="modal fade" id="editNodeInfoModal" tabindex="-1" aria-labelledby="editNodeInfoModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editNodeInfoModalLabel">${isNew ? 'Create' : 'Edit'} ${isComposite ? 'Composite Field' : 'Field'}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editNodeInfoForm">
                            <div class="mb-3">
                                <label for="fieldType" class="form-label">Node Type</label>
                                <select class="form-select" id="fieldType" disabled>
                                    <option value="field" ${nodeData.type === 'field' ? 'selected' : ''}>field</option>
                                    <option value="composite" ${nodeData.type === 'composite' ? 'selected' : ''}>composite</option>
                                    <option value="subfield" ${nodeData.type === 'subfield' ? 'selected' : ''}>subfield</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="fieldName" class="form-label">Field Name</label>
                                <input type="text" class="form-control" id="fieldName" value="${nodeData.name}">
                            </div>
                            <div class="mb-3" id="conditionalityContainer">
                                <label for="fieldConditionality" class="form-label">Conditionality</label>
                                <input type="text" class="form-control" id="fieldConditionality" value="${nodeData.conditionality}">
                            </div>
                            <div class="mb-3" id="dimensionsContainer">
                                <label for="fieldDimensions" class="form-label">Dimensions</label>
                                <input type="text" class="form-control" id="fieldDimensions" value="${nodeData.dimensions}">
                            </div>
                            <div class="mb-3" id="dataTypeContainer">
                                <label for="fieldDataType" class="form-label">Data Type</label>
                                <select class="form-select" id="fieldDataType">
                                    <option value="AN" ${nodeData.dataType === 'AN' ? 'selected' : ''}>AN</option>
                                    <option value="N" ${nodeData.dataType === 'N' ? 'selected' : ''}>N</option>
                                    <option value="DT" ${nodeData.dataType === 'DT' ? 'selected' : ''}>DT</option>
                                    <option value="ID" ${nodeData.dataType === 'ID' ? 'selected' : ''}>ID</option>
                                    <option value="X" ${nodeData.dataType === 'X' ? 'selected' : ''}>X</option>
                                    <!-- Add more options as needed -->
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="closeModalButton" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="saveNodeInfoChanges">Save changes</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('body').append(modalContent);
    var modal = new bootstrap.Modal(document.getElementById('editNodeInfoModal'));
    modal.show();

    // Event listener for the dropdown to toggle visibility of dimensions and data type
    $('#fieldType').on('change', function() {
        var selectedType = $(this).val();
        if (selectedType === 'composite') {
            $('#dimensionsContainer').hide();
            $('#dataTypeContainer').hide();
            isComposite = true;
            isField = false;
            isSubfield = false;
        } else if (selectedType === 'field') {
            $('#dimensionsContainer').show();
            $('#dataTypeContainer').show();
            isComposite = false;
            
        }
    });

    // Trigger change event to set initial visibility based on the current type
    $('#fieldType').trigger('change');

    $('#saveNodeInfoChanges').on('click', function() {
        var newName = $('#fieldName').val().trim() || 'NewName'; // Trim whitespace
        var newConditionality = $('#fieldConditionality').val().trim() || 'C';
        if (isField || isSubfield) {
            var newDimensions = $('#fieldDimensions').val().trim() || '1';
            var newDataType = $('#fieldDataType').val().trim() || 'AN';
        }
        
        // Validation checks
        if (!newName) {
            alert('Field Name is required.');
            return; // Stop execution if validation fails
        }

        if (newName.length > 50) {
            alert('Field Name cannot exceed 50 characters.');
            return; // Stop execution if validation fails
        }

        if (isField && (!newDimensions || isNaN(newDimensions))) {
            alert('Dimensions must be a valid number.');
            return; // Stop execution if validation fails
        }

        if (isField && (!newDataType || newDataType.length > 2)) {
            alert('Data Type cannot exceed 2 characters.');
            return; // Stop execution if validation fails
        }

        // Check for unique name within the parent node
        var tree = $('#node-info-tree').jstree(true);
        var parentNode = tree.get_node(node.parent);
        var existingNames = parentNode.children.map(childId => {
            if (childId !== node.id) {
                var childNode = tree.get_node(childId);
                return childNode.text.split(' (')[0]; // Get the name part before any additional info
            }
        });

        if (existingNames.includes(newName)) {
            alert('Field Name must be unique within this context.');
            return; // Stop execution if validation fails
        }

        var newText = newName;

        if (isComposite) {
            var newType = $('#fieldType').val() || 'composite';
            newText += ` (${newType}, ${newConditionality})`;
        } else if (isField) {
            var newType = $('#fieldType').val() || 'field';
            newText += ` (${newType}, ${newConditionality}, ${newDimensions}, ${newDataType})`;
        } else if (isSubfield) {
            var newType = $('#fieldType').val() || 'subfield';
            newText += ` (${newType}, ${newConditionality}, ${newDimensions}, ${newDataType})`;
        }

        var tree = $('#node-info-tree').jstree(true);
        tree.rename_node(node, newText);

        updateRecorddefs(tree);

        modal.hide();
        $('#editNodeInfoModal').remove();

        // Log the updated recorddefs to the console
        //console.log('Updated recorddefs:', window.grammarRecorddefs);

        // Here you can update your data structure or send an update to the server
        console.log('Node updated:', node.id, 'New text:', newText);
    });

    $('#editNodeInfoModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });

    // Attach click event to the Close button
    $('#closeModalButton').on('click', function() {
        if (isNew) {
            var tree = $('#node-info-tree').jstree(true);
            tree.delete_node(node);
        }
    });
}

function parseNodeText(text) {
    var match = text.match(/^(.+?) \((.+?), (.+?), (.+?), (.+?)\)$/);
    if (match) {
        return {
            name: match[1],
            type: match[2],
            conditionality: match[3],
            dimensions: match[4],
            dataType: match[5]
        };
    }

    // Handle composite fields
    var compositeMatch = text.match(/^(.+?) \((.+?), (.+?)\)$/);
    if (compositeMatch) {
        return {
            name: compositeMatch[1],
            type: compositeMatch[2],
            conditionality: compositeMatch[3],
            dimensions: '',
            dataType: ''
        };
    }

    // Default case if no match is found
    return {
        name: text,
        type: '',
        conditionality: '',
        dimensions: '',
        dataType: ''
    };
}

function saveRecorddefs(recorddefs) {
    var originalFilePath = $('#grammar-tree-view').data('original-file-path');
    $.ajax({
        url: '/grammar/save_recorddefs/',
        method: 'POST',
        data: JSON.stringify({
            file_path: originalFilePath,
            recorddefs: recorddefs
        }),
        contentType: 'application/json',
        success: function(data) {
            if (data.status === 'success') {
                alert('Recorddefs saved successfully');
            } else {
                alert('Error saving recorddefs: ' + data.message);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Error saving recorddefs:", jqXHR.responseText);
            alert('Error saving recorddefs: ' + textStatus);
        }
    });
}

// Add this new function to log updated recorddefs
function logUpdatedRecorddefs(treeInstance) {
    updateRecorddefs(treeInstance);
}

function updateRecorddefs(treeInstance) {
    var updatedTreeData = treeInstance.get_json('#', {flat: false});
    var currentNodeId = $('#grammar-tree-view').jstree(true).get_selected()[0];
    var currentNode = $('#grammar-tree-view').jstree(true).get_node(currentNodeId);
    var recordId = currentNode.data.ID;
    
    // Get the node-info-tree data
    var nodeInfoTreeData = $('#node-info-tree').jstree(true).get_json('#', {flat: false});
    
    // Convert the node-info-tree data to recorddefs format
    var updatedRecorddef = nodeInfoTreeToRecorddef(nodeInfoTreeData);
    //console.log('Updated element in recorddefs:', updatedRecorddef);

    // Update the specific record in the global recorddefs object
    window.grammarRecorddefs[recordId] = updatedRecorddef;

    // Log the updated recorddefs to the console
    console.log('Updated recorddefs:', window.grammarRecorddefs);
    
}

function nodeInfoTreeToRecorddef(treeData) {
    let result = [];
    treeData.forEach(node => {
        let nodeData = parseNodeText(node.text);
        if (node.type === 'field' || node.type === 'subfield') {
            result.push([nodeData.name, nodeData.conditionality, nodeData.dimensions, nodeData.dataType]);
        } else if (node.type === 'composite') {
            let subfields = node.children.map(child => {
                let subfieldData = parseNodeText(child.text);
                return [subfieldData.name, subfieldData.conditionality, subfieldData.dimensions, subfieldData.dataType];
            });
            result.push([nodeData.name, nodeData.conditionality, subfields]);
        }
    });
    return result;
}

function nodeInfoContextMenu(node) {
    var items = {}
                        
    switch(node.type) {
        case 'field':
        case 'composite':
            items.createNormal = {
                'label': 'Create Normal Field',
                'action': function(data) {
                    var inst = $.jstree.reference(data.reference);
                    var obj = inst.get_node(node.id);
                    var position = getNodePosition(node.id);
                    //console.log("Referenced Obj:", data.reference, inst, obj, node, position);
                    inst.create_node(obj.parent, { type: 'field', text: '', conditionality: 'C', dimensions: '1', dataType: 'AN' }, position + 1, function(new_node) {
                        setTimeout(function() { 
                            new_node.text = 'NewField (field, C, 1, AN)';
                            console.log("New Node:", new_node);
                            editNodeInfoField(new_node, true);
                            logUpdatedRecorddefs(inst);
                        }, 0);
                    });
                }
            };
            items.createComposite = {
                'label': 'Create Composite Field',
                'action': function(data) {
                    var inst = $.jstree.reference(data.reference);
                    var obj = inst.get_node(node.id);
                    var position = getNodePosition(node.id);
                    inst.create_node(obj.parent, { type: 'composite', text: '', conditionality: 'C' }, position + 1, function(new_node) {
                        setTimeout(function() { 
                            new_node.text = 'NewComposite (composite, C)';
                            console.log("New Node:", new_node);
                            editNodeInfoField(new_node, true);
                            logUpdatedRecorddefs(inst);
                        }, 0);
                    });
                }
            };
            if (node.type === 'composite') {
                items.createSubfield = {
                    'label': 'Create Subfield Inside',
                    'action': function(data) {
                        var inst = $.jstree.reference(data.reference);
                        var obj = inst.get_node(node.id);
                        var position = getNodePosition(node.id);
                        inst.create_node(obj, { type: 'subfield', text: '', conditionality: 'C', dimensions: '1', dataType: 'AN' }, 'last', function(new_node) {
                            setTimeout(function() { 
                                new_node.text = 'NewSubfield (subfield, C, 1, AN)';
                                console.log("New Node:", new_node);
                                editNodeInfoField(new_node, true);
                                logUpdatedRecorddefs(inst);
                            }, 0);
                        });
                    }
                };
            }
            break;
        case 'subfield':
            items.createSubfield = {
                'label': 'Create Subfield',
                'action': function(data) {
                    var inst = $.jstree.reference(data.reference);
                    var obj = inst.get_node(node.id);
                    var position = getNodePosition(node.id);
                    inst.create_node(obj.parent, { type: 'subfield', text: '', conditionality: 'C', dimensions: '1', dataType: 'AN' }, position + 1, function(new_node) {
                        setTimeout(function() { 
                            new_node.text = 'NewSubfield (subfield, C, 1, AN)';
                            new_node.type = 'subfield';
                            new_node.conditionality = 'C';
                            new_node.dimensions = '1';
                            new_node.dataType = 'AN';
                            console.log("New Node:", new_node);
                            editNodeInfoField(new_node, true);
                            logUpdatedRecorddefs(inst);
                        }, 0);
                    });
                }
            };
            break;
    }
    
    items.delete = {
        'label': 'Delete',
        'action': function(data) {
            var inst = $.jstree.reference(data.reference);
            var obj = inst.get_node(data.reference);
            if (confirm('Are you sure you want to delete this node?')) {
                inst.delete_node(obj);
            }
        }
    };
    
    return items;
}

// Function to get the position of a node
function getNodePosition(nodeId) {
    var tree = $('#node-info-tree').jstree(true); // Get the jsTree instance
    var node = tree.get_node(nodeId); // Get the node by ID

    if (node) {
        var parentNode = tree.get_node(node.parent); // Get the parent node
        if (parentNode) {
            // Find the index of the node among its siblings
            var position = parentNode.children.indexOf(node.id);
            console.log("Node ID:", node.id);
            console.log("Node Position:", position); // Log the position
            return position; // Return the position
        } else {
            console.error("Parent node not found for:", nodeId);
            return null; // Return null if the parent node is not found
        }
    } else {
        console.error("Node not found:", nodeId);
        return null; // Return null if the node is not found
    }
}
