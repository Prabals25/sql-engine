let schemaData = null;
let selectedTable = null;
let uniqueValues = {};

$(document).ready(function () {
loadSchema();
loadUniqueValues();
setupEventListeners();
});

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
            console.log('Unique values loaded:', uniqueValues);
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

schemaData[selectedTable].forEach(column => {
    const columnName = column.name;
    const isCategorical = ['region', 'rep', 'item'].includes(columnName);

    const checkboxDiv = $('<div>').addClass('column-checkbox mb-3 border-bottom pb-2');
    const checkboxRow = $('<div>').addClass('d-flex justify-content-between align-items-center');

    const checkboxLabelContainer = $('<div>').addClass('d-flex align-items-center');
    const checkbox = $('<input>')
        .attr('type', 'checkbox')
        .attr('id', `col-${columnName}`)
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
                $(`#value-dropdown-${columnName}`).remove();
            } else {
                inputContainer.hide();
            }
        }
    });
});
}

function renderValueDropdown(columnName) {
const container = $('#value-selection-container');
const dropdownContainer = $(`<div id="value-dropdown-${columnName}" class="mb-4">`);

if (uniqueValues[columnName]) {
    const values = uniqueValues[columnName];

    const label = $('<label>')
        .addClass('form-label fw-bold')
        .text(columnName.charAt(0).toUpperCase() + columnName.slice(1));

    const dropdown = $('<select>')
        .addClass('selectpicker form-control')
        .attr('multiple', 'multiple')
        .attr('data-live-search', 'true')
        .attr('title', 'Select values');

    values.forEach(value => {
        dropdown.append($('<option>').val(value).text(value));
    });

    dropdownContainer.append(label, dropdown);
    container.append(dropdownContainer);

    dropdown.selectpicker('refresh');
}
}

function showError(message) {
const container = $('#value-selection-container');
container.html(`<div class="alert alert-danger">${message}</div>`);
}
