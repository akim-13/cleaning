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

const locationName = JSON.parse(document.getElementById('location-name')!.textContent!);
const locationSocket = new WebSocket(`ws://${window.location.host}/fill-out/${locationName}/`);

locationSocket.onopen = function(event) {
    console.log('Connection opened');
}


locationSocket.onmessage = function(event) {
    console.log('Message received');

    const data = JSON.parse(event.data);
    const requestedAction = data['requested_action'];

    switch (requestedAction) {
        case 'request_current_page_contents':
            locationSocket.send(JSON.stringify({
                'requested_action': 'send_current_page_contents',
                'current_page_contents': document.body.innerHTML,
                'csrf_token': document.querySelector('meta[name="csrf_token"]')!.getAttribute('content')!,
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

        // TODO: Too large and a lot of code duplication. Refactor.
        case 'update_current_page_contents':
            document.body.innerHTML = data.current_page_contents;
            const valid_csrf_token = document.querySelector('meta[name="csrf_token"]')!.getAttribute('content')!;
            const form_csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement | null;

            if (form_csrf_token === null) {
                const form = document.getElementById('form-id') as HTMLFormElement;
                form.insertAdjacentHTML('afterbegin', `<input name="csrfmiddlewaretoken" value="${valid_csrf_token}" hidden>`);
            } else if (form_csrf_token.getAttribute('value') !== '') {
                console.error('Do not send the CSRF token when updating the page!!\nReceived CSRF token:', form_csrf_token.getAttribute('value'));
            } else {
                form_csrf_token.setAttribute('value', valid_csrf_token);
            }

            const form = document.getElementById('form-id') as HTMLFormElement | null;
            if (form) {
                form.onsubmit = event => {
                    const newRowsAdded = Boolean(document.getElementsByName('zones[]'));
                    if (newRowsAdded) {
                        const submissionTimestamp = String(generateUnixTimestamp());
                        form.querySelector('[name="submission_timestamp"]')!.setAttribute('value', submissionTimestamp);
                    }
                }
            }

            const addedRows = document.getElementById('table-id')!.querySelectorAll('tr[id]') as NodeListOf<HTMLTableRowElement>;
            
            addedRows.forEach(row => {
                const zoneSelector = row.querySelector('[name="zones[]"]') as HTMLSelectElement;
                const markSelector = row.querySelector('[name="marks[]"]') as HTMLSelectElement;
                const isApprovedCheckbox = row.querySelector('[name="approvals[]"]') as HTMLInputElement;
                const customerCommentTextarea = row.querySelector('[name="customer_comments[]"]') as HTMLTextAreaElement;
                const contractorCommentTextarea = row.querySelector('[name="contractor_comments[]"]') as HTMLTextAreaElement;

                if (data.role === 'customer') {
                    isApprovedCheckbox.classList.add('disabled');
                    contractorCommentTextarea.classList.add('disabled');

                    zoneSelector.classList.remove('disabled');
                    markSelector.classList.remove('disabled');
                    customerCommentTextarea.classList.remove('disabled');
                } else if (data.role === 'contractor') {
                    zoneSelector.classList.add('disabled');
                    markSelector.classList.add('disabled');
                    customerCommentTextarea.classList.add('disabled');

                    isApprovedCheckbox.classList.remove('disabled');
                    contractorCommentTextarea.classList.remove('disabled');
                }

                zoneSelector.addEventListener('change', updateFieldForEveryone);
                markSelector.addEventListener('change', updateFieldForEveryone);
                isApprovedCheckbox.addEventListener('change', updateFieldForEveryone);
                customerCommentTextarea.addEventListener('input', updateFieldForEveryone);
                contractorCommentTextarea.addEventListener('input', updateFieldForEveryone);
            
                function updateFieldForEveryone(event: Event) {
                    const target = event.target as HTMLInputElement;
                    const fieldName = target.name;
                    let fieldValue = target.value;
                    
                    if (fieldName === 'approvals[]') {
                        const checkbox = row.querySelector('[name="approvals[]"]') as HTMLInputElement;
                        fieldValue = checkbox.checked ? 'on' : 'off';
                    }
    
                    const row_UUID = row.id;
            
                    locationSocket.send(JSON.stringify({
                        'requested_action': 'field_change',
                        'row_UUID': row_UUID,
                        'field_name': fieldName,
                        'field_value': fieldValue
                    }));
                }
            });

            
            if (data.field_values) {
                updateFieldValues(data.field_values);
            }
            break;

        case 'append_row':
            appendNewRowHtml(data.new_row_html, data.row_UUID, data.role);
            break;

        // TODO: Rename `field_change` to `update_field`.
        case 'field_change':
            const row = document.getElementById(data.row_UUID) as HTMLTableRowElement;
            const fieldName = data.field_name;
            const fieldValue = data.field_value;
            const target = row.querySelector(`[name="${fieldName}"]`) as HTMLInputElement;

            if (fieldName === 'approvals[]') {
                target.checked = fieldValue === 'on';
            } else {
                target.value = fieldValue;
            }

            break;
    }
}


locationSocket.onclose = function(event) {
    console.error('Connection closed unexpectedly');
}


function getFieldValues(): string {
    let fieldValues: Record<string, Record<string, string>> = {};

    const table = document.getElementById('table-id') as HTMLFormElement;
    const addedRows = table.querySelectorAll('tr[id]') as NodeListOf<HTMLTableRowElement>;
    if (addedRows.length === 0) {
        return JSON.stringify(fieldValues);
    }

    addedRows.forEach(row => {
        const rowFields = row.querySelectorAll('input, select, textarea') as NodeListOf<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>;
        fieldValues[row.id] = {};
        rowFields.forEach(field => {
            if (field.name === 'approvals[]') {
                const rowCheckbox = row.querySelector('input[type="checkbox"]') as HTMLInputElement;
                fieldValues[row.id]['approvals[]'] = rowCheckbox.checked ? 'on' : 'off';
            } else {
                fieldValues[row.id][field.name] = field.value;
            }
        });
    });
    
    return JSON.stringify(fieldValues);
}


function updateFieldValues(fieldValuesJsonString: string): void {

    const fieldValues = JSON.parse(fieldValuesJsonString);

    Object.keys(fieldValues).forEach(rowId => {
        const row = document.getElementById(rowId) as HTMLTableRowElement;

        Object.keys(fieldValues[rowId]).forEach(fieldName => {
            const fieldValue = fieldValues[rowId][fieldName];
            const target = row.querySelector(`[name="${fieldName}"]`) as HTMLInputElement;

            if (fieldName === 'approvals[]') {
                target.checked = fieldValue === 'on';
            } else {
                target.value = fieldValue;
            }
        });
    });
}


function generateCurrentFormattedTime(): string {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}


function generateUnixTimestamp(): number {
    return Math.floor(Date.now() / 1000);
}


const form = document.getElementById('form-id') as HTMLFormElement | null;
if (form) {
    form.onsubmit = event => {
        const newRowsAdded = Boolean(document.getElementsByName('zones[]'));
        if (newRowsAdded) {
            const submissionTimestamp = String(generateUnixTimestamp());
            form.querySelector('[name="submission_timestamp"]')!.setAttribute('value', submissionTimestamp);
        }
    }
}


function sendAppendRowRequest(): void {
    const formUID = Date.now();
    locationSocket.send(JSON.stringify({
        'requested_action': 'append_row',
        'form_UID': formUID
    }));
}   


function appendNewRowHtml(newRowHtml: string, row_UUID: string, role: string): void {
    const table = document.getElementById('table-id') as HTMLTableElement;

    // Append new row.
    if (table.rows.length > 1) {
        const lastRow = table.rows[table.rows.length - 1];
        lastRow.insertAdjacentHTML('beforebegin', newRowHtml);
    } else {
        table.insertAdjacentHTML('beforeend', newRowHtml);
    }

    const row = document.getElementById(row_UUID) as HTMLTableRowElement;
    const creationTimestamp = String(generateUnixTimestamp());

    const zoneSelector = row.querySelector('[name="zones[]"]') as HTMLSelectElement;
    const markSelector = row.querySelector('[name="marks[]"]') as HTMLSelectElement;
    const isApprovedCheckbox = row.querySelector('[name="approvals[]"]') as HTMLInputElement;
    const customerCommentTextarea = row.querySelector('[name="customer_comments[]"]') as HTMLTextAreaElement;
    const contractorCommentTextarea = row.querySelector('[name="contractor_comments[]"]') as HTMLTextAreaElement;

    zoneSelector.addEventListener('change', updateFieldForEveryone);
    markSelector.addEventListener('change', updateFieldForEveryone);
    isApprovedCheckbox.addEventListener('change', updateFieldForEveryone);
    customerCommentTextarea.addEventListener('input', updateFieldForEveryone);
    contractorCommentTextarea.addEventListener('input', updateFieldForEveryone);

    if (role === 'customer') {
        isApprovedCheckbox.classList.add('disabled');
        contractorCommentTextarea.classList.add('disabled');
    } else if (role === 'contractor') {
        zoneSelector.classList.add('disabled');
        markSelector.classList.add('disabled');
        customerCommentTextarea.classList.add('disabled');
    }

    row.querySelector('[name="creation_timestamps[]"]')!.setAttribute('value', creationTimestamp);
  
    // TODO: Move this out of the `appendNewRowHtml()`.
    function updateFieldForEveryone(event: Event) {
        const target = event.target as HTMLInputElement;
        const fieldName = target.name;
        let fieldValue = target.value;
        
        if (fieldName === 'approvals[]') {
            const checkbox = row.querySelector('[name="approvals[]"]') as HTMLInputElement;
            fieldValue = checkbox.checked ? 'on' : 'off';
        }

        locationSocket.send(JSON.stringify({
            'requested_action': 'field_change',
            'row_UUID': row_UUID,
            'field_name': fieldName,
            'field_value': fieldValue
        }));
    }
    
    const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
    if (lastTimeCell === null) {
        insertNewTimeCell();
    } else if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
        let lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
        lastTimeCell.removeAttribute('id');
        insertNewTimeCell();
    } else {
        lastTimeCell.rowSpan += 1;
    }
}


function insertNewTimeCell(): void {
    const table = document.getElementById('table-id') as HTMLTableElement;
    const penultimateRow = table.rows[table.rows.length - 2];
    const currentTime = generateCurrentFormattedTime();
    const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2">${currentTime}</td>`;
    penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
}
