"use strict";
/*
    INFO: How to change HTML for all users in real-time.
    
    1. [fill_out.ts] Send a request to consumer using `locationSocket.send()`.
    2. [consumers.py] Inside `receive()`, handle the request and generate new HTML if necessary.
    3. [eg_template.html] Render the HTML if necessary (e.g. if it contains django template tags).
    4. [consumers.py] Broadcast the HTML to a location group.
    5. [consumers.py] Send the HTML to WebSocket using `self.send()`.
    6. [fill_out.ts] Receive the HTML from WebSocket using `locationSocket.onmessage()`.
    7. [fill_out.ts] Change the HTML of the page.
*/
const locationName = JSON.parse(document.getElementById('location-name').textContent);
const locationSocket = new WebSocket(`ws://${window.location.host}/fill-out/${locationName}/`);
locationSocket.onopen = function (event) {
    console.log('Connection opened');
};
locationSocket.onmessage = function (event) {
    console.log('Message received');
    const data = JSON.parse(event.data);
    const requestedAction = data['requested_action'];
    switch (requestedAction) {
        case 'request_current_page_contents':
            locationSocket.send(JSON.stringify({
                'requested_action': 'send_current_page_contents',
                'current_page_contents': document.body.innerHTML,
                'csrf_token': document.querySelector('meta[name="csrf_token"]').getAttribute('content'),
                'field_values': getFieldValues(),
                'requester': data.requester
            }));
            break;
        case 'send_current_page_contents':
            locationSocket.send(JSON.stringify({
                'requested_action': 'update_current_page_contents',
                'current_page_contents': data.current_page_contents,
                'field_values': data.field_values
            }));
        case 'update_current_page_contents':
            document.body.innerHTML = data.current_page_contents;
            const valid_csrf_token = document.querySelector('meta[name="csrf_token"]').getAttribute('content');
            const form_csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (form_csrf_token === null) {
                const form = document.getElementById('form-id');
                form.insertAdjacentHTML('afterbegin', `<input name="csrfmiddlewaretoken" value="${valid_csrf_token}" hidden>`);
            }
            else if (form_csrf_token.getAttribute('value') !== '') {
                console.error('Do not send the CSRF token when updating the page!!\nReceived CSRF token:', form_csrf_token.getAttribute('value'));
            }
            else {
                form_csrf_token.setAttribute('value', valid_csrf_token);
            }
            if (data.field_values) {
                updateFieldValues(data.field_values);
            }
            break;
        case 'append_row':
            appendNewRowHtml(data.new_row_html, data.row_UUID);
            break;
        // TODO: Rename `field_change` to `update_field`.
        case 'field_change':
            const row = document.getElementById(data.row_UUID);
            const fieldName = data.field_name;
            const fieldValue = data.field_value;
            const target = row.querySelector(`[name="${fieldName}"]`);
            if (fieldName === 'approvals[]') {
                target.checked = fieldValue === 'on';
            }
            else {
                target.value = fieldValue;
            }
            break;
    }
};
locationSocket.onclose = function (event) {
    console.error('Connection closed unexpectedly');
};
function getFieldValues() {
    let fieldValues = {};
    const table = document.getElementById('table-id');
    const addedRows = table.querySelectorAll('tr[id]');
    if (addedRows.length === 0) {
        return JSON.stringify(fieldValues);
    }
    addedRows.forEach(row => {
        const rowFields = row.querySelectorAll('input, select, textarea');
        fieldValues[row.id] = {};
        rowFields.forEach(field => {
            if (field.name === 'approvals[]') {
                const rowCheckbox = row.querySelector('input[type="checkbox"]');
                fieldValues[row.id]['approvals[]'] = rowCheckbox.checked ? 'on' : 'off';
            }
            else {
                fieldValues[row.id][field.name] = field.value;
            }
        });
    });
    return JSON.stringify(fieldValues);
}
function updateFieldValues(fieldValuesJsonString) {
    const fieldValues = JSON.parse(fieldValuesJsonString);
    Object.keys(fieldValues).forEach(rowId => {
        const row = document.getElementById(rowId);
        Object.keys(fieldValues[rowId]).forEach(fieldName => {
            const fieldValue = fieldValues[rowId][fieldName];
            const target = row.querySelector(`[name="${fieldName}"]`);
            if (fieldName === 'approvals[]') {
                target.checked = fieldValue === 'on';
            }
            else {
                target.value = fieldValue;
            }
        });
    });
}
function generateCurrentFormattedTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}
function generateUnixTimestamp() {
    return Math.floor(Date.now() / 1000);
}
// WARNING: Do NOT use .onsubmit() instead of this function! 
// I don't know why, but it behaves very weirdly if you do.
function submitForm() {
    const form = document.getElementById('form-id');
    const submissionTimestamp = String(generateUnixTimestamp());
    form.querySelector('[name="submission_timestamp"]').setAttribute('value', submissionTimestamp);
    form.submit();
}
function sendAppendRowRequest() {
    const formUID = Date.now();
    locationSocket.send(JSON.stringify({
        'requested_action': 'append_row',
        'form_UID': formUID
    }));
}
function appendNewRowHtml(newRowHtml, row_UUID) {
    const table = document.getElementById('table-id');
    // Append new row.
    if (table.rows.length > 1) {
        const lastRow = table.rows[table.rows.length - 1];
        lastRow.insertAdjacentHTML('beforebegin', newRowHtml);
    }
    else {
        table.insertAdjacentHTML('beforeend', newRowHtml);
    }
    const row = document.getElementById(row_UUID);
    const creationTimestamp = String(generateUnixTimestamp());
    row.querySelector('[name="creation_timestamps[]"]').setAttribute('value', creationTimestamp);
    row.querySelector('[name="zones[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="marks[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="approvals[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="customer_comments[]"]').addEventListener('input', updateFieldForEveryone);
    row.querySelector('[name="contractor_comments[]"]').addEventListener('input', updateFieldForEveryone);
    // TODO: Move this out of the `appendNewRowHtml()`.
    function updateFieldForEveryone(event) {
        const target = event.target;
        const fieldName = target.name;
        let fieldValue = target.value;
        if (fieldName === 'approvals[]') {
            const checkbox = row.querySelector('[name="approvals[]"]');
            fieldValue = checkbox.checked ? 'on' : 'off';
        }
        locationSocket.send(JSON.stringify({
            'requested_action': 'field_change',
            'row_UUID': row_UUID,
            'field_name': fieldName,
            'field_value': fieldValue
        }));
    }
    const lastTimeCell = document.getElementById('last-time-cell');
    if (lastTimeCell === null) {
        insertNewTimeCell();
    }
    else if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
        let lastTimeCell = document.getElementById('last-time-cell');
        lastTimeCell.removeAttribute('id');
        insertNewTimeCell();
    }
    else {
        lastTimeCell.rowSpan += 1;
    }
}
function insertNewTimeCell() {
    const table = document.getElementById('table-id');
    const penultimateRow = table.rows[table.rows.length - 2];
    const currentTime = generateCurrentFormattedTime();
    const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2">${currentTime}</td>`;
    penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
}
