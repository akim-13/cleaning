const locationName = JSON.parse(document.getElementById('location-name')!.textContent!);

const locationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/fill-out/'
    + locationName
    + '/'
)

locationSocket.onopen = function(event) {
    console.log('Connection opened');
}

locationSocket.onmessage = function(event) {
    console.log('message received');

    const data = JSON.parse(event.data);
    if ('new_row_html' in data) {
        appendNewRowHtml(data.new_row_html);
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

    const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
    if (!lastTimeCell.hasAttribute('end-time')) {
        lastTimeCell.innerHTML += ` - ${generateCurrentFormattedTime()}`;
    }
    const unixTimestamp = generateUnixTimestamp();
    lastTimeCell.setAttribute('end-time', `${unixTimestamp}`);
    lastTimeCell.setAttribute('time-period-ended', 'true');
}


function sendAppendRowRequest(): void {
    // locationSocket.send() a request to consumer to append a new row.
    // Inside consumer's `receive`, use render_to_string and _new_row.html template to render the row
    // consumer sends it to group
    // group send it to WebSocket
    // websocket.onmessage receives it and appends it to the table

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
