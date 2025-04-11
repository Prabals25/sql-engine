// Global variables
let schemaData = null;
let selectedTable = null;
let uniqueValues = {};

// Initialize the application
$(document).ready(function() {
    loadSchema();
    loadUniqueValues();
    setupEventListeners();
});

// Load database schema
function loadSchema() {
    $.ajax({
        url: '/api/schema',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                schemaData = response.schema;
                renderSchema();
                populateTableSelect();
                // Automatically select the first table
                const firstTable = Object.keys(schemaData)[0];
                if (firstTable) {
                    $('#table-select').val(firstTable).trigger('change');
                }
            } else {
                showError('Failed to load schema: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error loading schema: ' + error);
        }
    });
}

// Load unique values for all columns
function loadUniqueValues() {
    $.ajax({
        url: '/api/unique-values',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                uniqueValues = response.unique_values;
                console.log('Unique values loaded:', uniqueValues);
            } else {
                showError('Failed to load unique values: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error loading unique values: ' + error);
        }
    });
}

// Render schema information
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

// Populate table select dropdown
function populateTableSelect() {
    const select = $('#table-select');
    select.empty();
    select.append($('<option>').val('').text('Select a table'));

    Object.keys(schemaData).forEach(table => {
        select.append($('<option>').val(table).text(table));
    });
}

// Setup event listeners
function setupEventListeners() {
    $('#table-select').change(function() {
        selectedTable = $(this).val();
        renderColumnCheckboxes();
    });
}

// Render column checkboxes
function renderColumnCheckboxes() {
    const container = $('#column-checkboxes');
    container.empty();

    if (!selectedTable || !schemaData[selectedTable]) {
        return;
    }

    schemaData[selectedTable].forEach(column => {
        const columnName = column.name;
        const checkboxDiv = $('<div>').addClass('column-checkbox mb-3');
        const checkbox = $('<input>')
            .attr('type', 'checkbox')
            .attr('id', `col-${columnName}`)
            .addClass('form-check-input');
        const label = $('<label>')
            .attr('for', `col-${columnName}`)
            .addClass('form-check-label')
            .text(`${columnName} (${column.type})`);

        checkbox.change(function() {
            if ($(this).is(':checked')) {
                // Only show value dropdown for categorical columns
                if (['region', 'rep', 'item'].includes(columnName)) {
                    renderValueDropdown(columnName);
                }
            } else {
                $(`#value-dropdown-${columnName}`).remove();
            }
        });

        checkboxDiv.append(checkbox, label);
        container.append(checkboxDiv);
    });
}

// Render value dropdown for a column
function renderValueDropdown(columnName) {
    const container = $('#value-selection-container');
    const dropdownContainer = $(`<div id="value-dropdown-${columnName}" class="value-dropdown mb-3">`);
    
    if (uniqueValues[columnName]) {
        const values = uniqueValues[columnName];
        
        // Create dropdown label
        const label = $('<label>')
            .addClass('form-label')
            .text(columnName.charAt(0).toUpperCase() + columnName.slice(1));
        
        // Create dropdown with search functionality
        const dropdown = $('<select>')
            .addClass('form-select')
            .attr('multiple', 'multiple')
            .attr('data-live-search', 'true');
        
        // Add search box
        const searchBox = $('<input>')
            .attr('type', 'text')
            .addClass('form-control mb-2')
            .attr('placeholder', `Search ${columnName}...`);
        
        // Add values to dropdown
        values.forEach(value => {
            dropdown.append($('<option>').val(value).text(value));
        });
        
        dropdownContainer.append(label, searchBox, dropdown);
        container.append(dropdownContainer);
        
        // Initialize Bootstrap Select
        dropdown.selectpicker();
        
        // Add search functionality
        searchBox.on('input', function() {
            const searchText = $(this).val().toLowerCase();
            dropdown.find('option').each(function() {
                const value = $(this).text().toLowerCase();
                $(this).toggle(value.includes(searchText));
            });
            dropdown.selectpicker('refresh');
        });
    }
}

// Show error message
function showError(message) {
    const container = $('#value-selection-container');
    container.html(`<div class="alert alert-danger">${message}</div>`);
} 