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
                'current_page_contents': document.documentElement.innerHTML,
                'requester': data.requester
            }));
            break;
        case 'send_current_page_contents':
            locationSocket.send(JSON.stringify({
                'requested_action': 'update_current_page_contents',
                'current_page_contents': data.current_page_contents
            }));
        case 'update_current_page_contents':
            document.documentElement.innerHTML = data.current_page_contents;
            break;
        case 'append_row':
            appendNewRowHtml(data.new_row_html, data.row_UUID);
            break;
        case 'change_time_period':
            changeLastTimeCellHtml();
            break;
        case 'field_change':
            const row = document.getElementById(data.row_UUID);
            const fieldName = data.field_name;
            const fieldValue = data.field_value;
            const target = row.querySelector(`[name="${fieldName}"]`);
            if (fieldName === 'approvals[]') {
                if (fieldValue === 'on') {
                    target.checked = true;
                }
                else {
                    target.checked = false;
                }
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
function generateCurrentFormattedTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}
function generateUnixTimestamp() {
    return Math.floor(Date.now() / 1000);
}
document.getElementById('form-id').onsubmit = event => {
    const newRowsAdded = document.getElementById('zones[]');
    if (newRowsAdded) {
        sendChangeTimePeriodRequest();
    }
};
function sendChangeTimePeriodRequest() {
    locationSocket.send(JSON.stringify({
        'requested_action': 'change_time_period'
    }));
}
function changeLastTimeCellHtml() {
    const lastTimeCell = document.getElementById('last-time-cell');
    if (lastTimeCell.hasAttribute('end-time')) {
        return;
    }
    lastTimeCell.innerHTML += ` - ${generateCurrentFormattedTime()}`;
    const unixTimestamp = generateUnixTimestamp();
    lastTimeCell.setAttribute('end-time', `${unixTimestamp}`);
    lastTimeCell.setAttribute('time-period-ended', 'true');
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
    // NOTE: This is a workaround, `insertBefore` doesn't work for some reason.
    if (table.rows.length > 1) {
        const lastRow = table.rows[table.rows.length - 1];
        lastRow.insertAdjacentHTML('beforebegin', newRowHtml);
    }
    else {
        table.insertAdjacentHTML('beforeend', newRowHtml);
    }
    const row = document.getElementById(row_UUID);
    row.querySelector('[name="zones[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="marks[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="approvals[]"]').addEventListener('change', updateFieldForEveryone);
    row.querySelector('[name="customer_comments[]"]').addEventListener('input', updateFieldForEveryone);
    row.querySelector('[name="contractor_comments[]"]').addEventListener('input', updateFieldForEveryone);
    function updateFieldForEveryone(event) {
        const target = event.target;
        const fieldName = target.name;
        let fieldValue = target.value;
        if (fieldName === 'approvals[]') {
            const checkbox = row.querySelector('[name="approvals[]"]');
            if (checkbox.checked) {
                fieldValue = 'on';
            }
            else {
                fieldValue = 'off';
            }
        }
        locationSocket.send(JSON.stringify({
            'requested_action': 'field_change',
            'row_UUID': row_UUID,
            'field_name': fieldName,
            'field_value': fieldValue
        }));
    }
    const lastTimeCell = document.getElementById('last-time-cell');
    if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
        // Remove the `last-time-cell` identifier from the previous time cell.
        let lastTimeCell = document.getElementById('last-time-cell');
        lastTimeCell.removeAttribute('id');
        // Insert a new time cell.
        // TODO: Error handling for -2.
        const penultimateRow = table.rows[table.rows.length - 2];
        const currentTime = generateCurrentFormattedTime();
        const unixTimestamp = generateUnixTimestamp();
        const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2" start-time="${unixTimestamp}">${currentTime}</td>`;
        penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
    }
    else {
        lastTimeCell.rowSpan += 1;
    }
}
