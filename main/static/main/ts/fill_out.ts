/*
    INFO: How to change HTML for all users in real-time.
    
    1. [fill_out.ts] Send a request to consumer using `locationSocket.send()`.
    2. [consumers.py] Receive the request and generate new HTML.
    3. [eg_template.html] Render HTML if necessary (e.g. if it contains django template tags).
    4. [consumers.py] Broadcast the HTML to a location group.
    5. [consumers.py] Send the new HTML to WebSocket using `self.send()`.
    6. [fill_out.ts] Receive the new HTML from WebSocket using `locationSocket.onmessage`.
    7. [fill_out.ts] Change the HTML.
*/

const locationName = JSON.parse(document.getElementById('location-name')!.textContent!);

const locationSocket = new WebSocket(`ws://${window.location.host}/fill-out/${locationName}/`);

locationSocket.onopen = function(event) {
    console.log('Connection opened');
}

locationSocket.onmessage = function(event) {
    console.log('Message received');

    const data = JSON.parse(event.data);
    if ('new_row_html' in data) {
        appendNewRowHtml(data.new_row_html);
    } else if ('change_time_period_request' in data) {
        changeLastTimeCellHtml();
    }
}

locationSocket.onclose = function(event) {
    console.error('Connection closed unexpectedly');
}

function generateCurrentFormattedTime(): string {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}


function generateUnixTimestamp(): number {
    return Math.floor(Date.now() / 1000);
}


function submitForms(): void {
    document.querySelectorAll('form').forEach(form => {
        const event = new Event('submit');
        form.dispatchEvent(event);
    });

    sendChangeTimePeriodRequest();
}


function sendChangeTimePeriodRequest(): void {
    locationSocket.send(JSON.stringify({
        'requested_action': 'change_time_period'
    }));
}


function changeLastTimeCellHtml(): void {
    const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
    if (lastTimeCell.hasAttribute('end-time')) {
        return;
    }

    lastTimeCell.innerHTML += ` - ${generateCurrentFormattedTime()}`;
    const unixTimestamp = generateUnixTimestamp();
    lastTimeCell.setAttribute('end-time', `${unixTimestamp}`);
    lastTimeCell.setAttribute('time-period-ended', 'true');
}


function sendAppendRowRequest(): void {
    const formUID = Date.now();
    locationSocket.send(JSON.stringify({
        'requested_action': 'append_row',
        'form_UID': formUID
    }));
}   


function appendNewRowHtml(newRowHtml: string): void {
    const table = document.getElementById('table-id') as HTMLTableElement;

    // Append new row.
    // NOTE: This is a workaround, `insertBefore` doesn't work for some reason.
    if (table.rows.length > 1) {
        const lastRow = table.rows[table.rows.length - 1];
        lastRow.insertAdjacentHTML('beforebegin', newRowHtml);
    } else {
        table.insertAdjacentHTML('beforeend', newRowHtml);
    }
    
    const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
    if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
        // Remove the `last-time-cell` identifier from the previous time cell.
        let lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
        lastTimeCell.removeAttribute('id');

        // Insert a new time cell.
        // TODO: Error handling for -2.
        const penultimateRow = table.rows[table.rows.length - 2];
        const currentTime = generateCurrentFormattedTime();
        const unixTimestamp = generateUnixTimestamp();
        const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2" start-time="${unixTimestamp}">${currentTime}</td>`;
        penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
    } else {
        lastTimeCell.rowSpan += 1;
    }
}
