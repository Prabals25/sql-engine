let schemaData = null;
let selectedTable = null;
let uniqueValues = {};

$(document).ready(function() {
    loadSchema();
    loadUniqueValues();
    setupEventListeners();
    setupSubmitButton();  // New function to handle form submission
});

function setupSubmitButton() {
    $('#submit-btn').click(function() {
        console.log("Submit button clicked!");
        
        // Create the data object for the selected columns and their values
        let selectedColumns = [];
        let selectedValues = {};
        let userQuery = $('#user-query').val().trim();  // Get the user query/instructions

        // Collect values from the checked checkboxes
        $('#column-checkboxes input:checked').each(function() {
            let columnName = $(this).attr('id').replace('col-', '');
            let isCategorical = $(this).attr('data-type') === 'categorical';
            
            console.log("Processing column:", columnName, "isCategorical:", isCategorical);
            
            selectedColumns.push(columnName);
            
            // Handle categorical columns (dropdowns)
            if (isCategorical) {
                let dropdownValues = [];
                // Get selected values from the dropdown
                $(`#value-dropdown-${columnName} select option:selected`).each(function() {
                    dropdownValues.push($(this).val());
                });
                if (dropdownValues.length > 0) {
                    selectedValues[columnName] = dropdownValues;
                }

            } 
            // Handle non-categorical columns (text inputs)
            else {
                let inputValue = $(`#text-input-${columnName}`).val();
                if (inputValue && inputValue.trim() !== '') {
                    selectedValues[columnName] = inputValue;
                }
                else {
                    // Include empty text fields with an empty string
                    selectedValues[columnName] = "";
                }
            }
        });

        console.log("HI : Selected Columns:", selectedColumns);
        console.log("HI : Selected Values:", selectedValues);
        console.log("User Query:", userQuery);

        // Construct JSON to send to the backend
        let data = {
            columns: selectedColumns,
            selected_values: selectedValues,
            user_query: userQuery  // Add the user query to the data object
        };

        // Send JSON data to the new Flask route
        $.ajax({
            url: '/api/submit-selections',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    console.log('Backend Response:', response);
                    
                    // Show SQL query and results
                    const container = $('#results-container');
                    let resultsHtml = `
                        <div class="alert alert-success mb-3">
                            <strong>Success!</strong> ${response.message}
                        </div>
                        <div class="card mb-3">
                            <div class="card-header bg-light">
                                <h5 class="mb-0">Generated SQL Query</h5>
                            </div>
                            <div class="card-body">
                                <pre class="bg-light p-3 rounded"><code>${response.sql_query || 'No SQL query available'}</code></pre>
                            </div>
                        </div>
                    `;

                    // Add results table if data is available
                    if (response.data && response.data.length > 0) {
                        resultsHtml += `
                            <div class="card">
                                <div class="card-header bg-light">
                                    <h5 class="mb-0">Query Results (${response.count} rows)</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped table-hover">
                                            <thead class="table-light">
                                                <tr>
                        `;

                        // Add column headers
                        response.columns.forEach(column => {
                            resultsHtml += `<th>${column}</th>`;
                        });

                        resultsHtml += `
                                                </tr>
                                            </thead>
                                            <tbody>
                        `;

                        // Add data rows
                        response.data.forEach(row => {
                            resultsHtml += '<tr>';
                            response.columns.forEach(column => {
                                resultsHtml += `<td>${row[column] || ''}</td>`;
                            });
                            resultsHtml += '</tr>';
                        });

                        resultsHtml += `
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        resultsHtml += `
                            <div class="alert alert-info">
                                No results found for this query.
                            </div>
                        `;
                    }

                    container.html(resultsHtml);
                } else {
                    showError('Error: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                showError('Error submitting data: ' + error);
            }
        });
    });
}

function loadSchema() {
$.ajax({
    url: '/api/schema',
    method: 'GET',
    success: function (response) {
        if (response.success) {
            schemaData = response.schema;
            renderSchema();
            populateTableSelect();
            const firstTable = Object.keys(schemaData)[0];
            if (firstTable) {
                $('#table-select').val(firstTable).trigger('change');
            }
        } else {
            showError('Failed to load schema: ' + response.error);
        }
    },
    error: function (xhr, status, error) {
        showError('Error loading schema: ' + error);
    }
});
}

function loadUniqueValues() {
$.ajax({
    url: '/api/unique-values',
    method: 'GET',
    success: function (response) {
        if (response.success) {
            uniqueValues = response.unique_values;
            
            // Log each categorical column's unique values
            console.log('----- Unique Values Loaded -----');
            for (const column in uniqueValues) {
                const values = uniqueValues[column];
                const uniqueCount = new Set(values).size;
                console.log(`${column}: ${uniqueCount} unique values out of ${values.length} total`);
                
                // If there are duplicates, show the first few
                if (uniqueCount < values.length) {
                    console.log(`Warning: ${column} has duplicate values!`);
                    // Ensure uniqueness going forward
                    uniqueValues[column] = [...new Set(values)];
                }
            }
        } else {
            showError('Failed to load unique values: ' + response.error);
        }
    },
    error: function (xhr, status, error) {
        showError('Error loading unique values: ' + error);
    }
});
}

function renderSchema() {
const container = $('#schema-container');
container.empty();

for (const [table, columns] of Object.entries(schemaData)) {
    const tableDiv = $('<div>').addClass('schema-table');
    const tableHeader = $('<h6>').text(table);
    tableDiv.append(tableHeader);

    columns.forEach(column => {
        const columnDiv = $('<div>').addClass('schema-column');
        columnDiv.text(`${column.name} (${column.type})`);
        tableDiv.append(columnDiv);
    });

    container.append(tableDiv);
}
}

function populateTableSelect() {
const select = $('#table-select');
select.empty();
select.append($('<option>').val('').text('Select a table'));

Object.keys(schemaData).forEach(table => {
    select.append($('<option>').val(table).text(table));
});
}

function setupEventListeners() {
$('#table-select').change(function () {
    selectedTable = $(this).val();
    renderColumnCheckboxes();
});
}

function renderColumnCheckboxes() {
const container = $('#column-checkboxes');
container.empty();

if (!selectedTable || !schemaData[selectedTable]) return;

// Filter to only show categorical columns
const categoricalColumns = schemaData[selectedTable].filter(column => {
    const columnName = column.name;
    return ['region', 'rep', 'item'].includes(columnName);
});

categoricalColumns.forEach(column => {
    const columnName = column.name;
    const isCategorical = true; // Since we've already filtered for categorical columns

    const checkboxDiv = $('<div>').addClass('column-checkbox mb-3 border-bottom pb-2');
    const checkboxRow = $('<div>').addClass('d-flex justify-content-between align-items-center');

    const checkboxLabelContainer = $('<div>').addClass('d-flex align-items-center');
    const checkbox = $('<input>')
        .attr('type', 'checkbox')
        .attr('id', `col-${columnName}`)
        .attr('data-type', isCategorical ? 'categorical' : 'non-categorical')
        .addClass('form-check-input me-2');
    const label = $('<label>')
        .attr('for', `col-${columnName}`)
        .addClass('form-check-label')
        .text(`${columnName} (${column.type})`);

    checkboxLabelContainer.append(checkbox, label);
    checkboxRow.append(checkboxLabelContainer);

    const inputContainer = $('<div>')
        .addClass('ms-2 input-container')
        .css('flex-grow', '1')
        .hide();

    const textInput = $('<input>')
        .attr('type', 'text')
        .attr('id', `text-input-${columnName}`)
        .attr('placeholder', 'Enter details...')
        .addClass('form-control form-control-sm');

    inputContainer.append(textInput);
    checkboxRow.append(inputContainer);
    checkboxDiv.append(checkboxRow);
    container.append(checkboxDiv);

    checkbox.change(function () {
        if ($(this).is(':checked')) {
            if (isCategorical) {
                renderValueDropdown(columnName);
            } else {
                inputContainer.show();
            }
        } else {
            if (isCategorical) {
                // Make sure the dropdown is completely removed, not just hidden
                $(`#value-dropdown-${columnName}`).remove();
            } else {
                inputContainer.hide();
            }
        }
    });
});
}

function renderValueDropdown(columnName) {
    // First, remove any existing dropdown for this column
    $(`#value-dropdown-${columnName}`).remove();
    
    // Get the container
    const container = $('#value-selection-container');
    
    // Only proceed if we have unique values for this column
    if (!uniqueValues[columnName] || uniqueValues[columnName].length === 0) {
        console.log(`No unique values found for ${columnName}`);
        return;
    }
    
    console.log(`Rendering dropdown for ${columnName} with values:`, uniqueValues[columnName]);
    
    // Create a new container
    const dropdownContainer = $(`<div id="value-dropdown-${columnName}" class="mb-4">`);
    
    // Create label
    const label = $('<label>')
        .addClass('form-label fw-bold')
        .text(columnName.charAt(0).toUpperCase() + columnName.slice(1));
    
    // Create the select element
    const dropdown = $('<select>')
        .addClass('form-control selectpicker')  // Add both classes
        .attr('id', `select-${columnName}`)
        .attr('multiple', 'multiple')
        .attr('data-live-search', 'true')
        .attr('title', 'Select values');
    
    // Get unique values using a Set
    const uniqueValuesArray = [...new Set(uniqueValues[columnName])];
    
    // Sort the values for better usability
    uniqueValuesArray.sort();
    
    // Log the unique values being added
    console.log(`Adding ${uniqueValuesArray.length} unique options for ${columnName}`);
    
    // Add options to the dropdown
    uniqueValuesArray.forEach(value => {
        dropdown.append(
            $('<option>')
                .val(value)
                .text(value)
        );
    });
    
    // Append elements to the container
    dropdownContainer.append(label, dropdown);
    container.append(dropdownContainer);
    
    // Initialize the bootstrap-select plugin
    try {
        dropdown.selectpicker({
            liveSearch: true,
            actionsBox: true,
            selectedTextFormat: 'count > 2'
        });
    } catch (e) {
        console.error('Error initializing selectpicker:', e);
    }
}

function showError(message) {
    const container = $('#results-container');
    container.html(`<div class="alert alert-danger">${message}</div>`);
}

// Function to display results in the main content area
function displayResults(results, userQuery) {
    const container = $('#results-container');
    container.empty();
    
    if (!results || !results.data || results.data.length === 0) {
        container.html('<p class="text-muted">No results found for your query.</p>');
        return;
    }
    
    // Create result summary with user query if provided
    const summary = $('<div>').addClass('mb-3 alert alert-info');
    let summaryHTML = `<strong>Results:</strong> Found ${results.count} records.`;
    
    if (userQuery) {
        summaryHTML += `<br><strong>Your Instructions:</strong> "${userQuery}"`;
    }
    
    summary.html(summaryHTML);
    
    // Create table
    const table = $('<table>').addClass('table table-striped table-hover');
    const thead = $('<thead>').addClass('table-light');
    const tbody = $('<tbody>');
    
    // Add header row
    const headerRow = $('<tr>');
    results.columns.forEach(column => {
        headerRow.append($('<th>').text(column));
    });
    thead.append(headerRow);
    
    // Add data rows
    results.data.forEach(row => {
        const dataRow = $('<tr>');
        results.columns.forEach(column => {
            dataRow.append($('<td>').text(row[column] !== null ? row[column] : ''));
        });
        tbody.append(dataRow);
    });
    
    // Assemble table
    table.append(thead, tbody);
    
    // Add to container
    container.append(summary, table);
}
