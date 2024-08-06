document.getElementById("markForm")!.addEventListener("submit", (event: Event) => {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);
    const csrfToken = (document.querySelector('[name="csrfmiddlewaretoken"]') as HTMLInputElement).value;

    fetch(form.action, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(formData as any)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        // TODO: Save data in the db.
        console.log(data.location + ' ' + data.zone + ' ' + data.mark + ' ' + data.is_approved);
    })
    .catch(error => console.error('Error:', error));
});


function getCurrentFormattedTime(): string {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}


function appendRow(): void {
    const form = document.getElementById("markForm") as HTMLFormElement;
    const csrfToken = (document.querySelector('[name="csrfmiddlewaretoken"]') as HTMLInputElement).value;

    fetch(form.action, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({'action': 'append_row'})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        
        const table = document.getElementById("tableID") as HTMLTableElement;
        
        if (!table) {
            console.error('Table not found');
            return;
        }

        // Append new row.
        // NOTE: This is a workaround, `insertBefore` doesn't work for some reason.
        if (table.rows.length > 1) {
            const lastRow = table.rows[table.rows.length - 1];
            lastRow.insertAdjacentHTML('beforebegin', data.new_row_html);
        } else {
            table.insertAdjacentHTML('beforeend', data.new_row_html);
        }
        
        const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
        if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
            // Remove the `last-time-cell` identifier from the previous time cell.
            let lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
            lastTimeCell.removeAttribute('id');

            // Insert a new time cell.
            // TODO: Error handling for -2.
            const penultimateRow = table.rows[table.rows.length - 2];
            const currentTime = getCurrentFormattedTime();
            const unixTimestamp = Math.floor(Date.now() / 1000);
            const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2" start-time="${unixTimestamp}">${currentTime}</td>`;
            penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
        } else {
            lastTimeCell.rowSpan += 1;
        }
    })
    .catch(error => console.error('Error:', error));
}


function submitForms(): void {
    document.querySelectorAll('form').forEach(form => {
        const event = new Event('submit');
        form.dispatchEvent(event);
    });

    const lastTimeCell = document.getElementById('last-time-cell') as HTMLTableCellElement;
    if (!lastTimeCell.hasAttribute('end-time')) {
        lastTimeCell.innerHTML += ` - ${getCurrentFormattedTime()}`;
    }
    const unixTimestamp = Math.floor(Date.now() / 1000);
    lastTimeCell.setAttribute('end-time', `${unixTimestamp}`);
    lastTimeCell.setAttribute('time-period-ended', 'true');
}
