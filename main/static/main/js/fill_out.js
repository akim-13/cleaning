"use strict";
document.getElementById("markForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    fetch(form.action, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(formData)
    })
        .then(response => response.json())
        .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        // Idk what this is for. Just leave it for now.
        console.log(data.location + ' ' + data.zone + ' ' + data.mark + ' ' + data.is_approved);
    })
        .catch(error => console.error('Error:', error));
});
function getCurrentFormattedTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}
function appendRow() {
    const form = document.getElementById("markForm");
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    fetch(form.action, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ 'action': 'append_row' })
    })
        .then(response => response.json())
        .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        const table = document.getElementById("tableID");
        if (!table) {
            console.error('Table not found');
            return;
        }
        // Append new row.
        // NOTE: This is a workaround, `insertBefore` doesn't work for some reason.
        if (table.rows.length > 1) {
            const lastRow = table.rows[table.rows.length - 1];
            lastRow.insertAdjacentHTML('beforebegin', data.new_row_html);
        }
        else {
            table.insertAdjacentHTML('beforeend', data.new_row_html);
        }
        const lastTimeCell = document.getElementById('last-time-cell');
        if (lastTimeCell.getAttribute('time-period-ended') === 'true') {
            // Remove the `last-time-cell` identifier from the previous time cell.
            let lastTimeCell = document.getElementById('last-time-cell');
            lastTimeCell.removeAttribute('id');
            // Insert a new time cell.
            // TODO: Error handling for -2.
            const penultimateRow = table.rows[table.rows.length - 2];
            const currentTime = getCurrentFormattedTime();
            const unixTimestamp = Math.floor(Date.now() / 1000);
            const newTimeCellHtml = `<td id="last-time-cell" time-period-ended="false" class="time-cell" rowspan="2" start-time="${unixTimestamp}">${currentTime}</td>`;
            penultimateRow.insertAdjacentHTML('beforebegin', newTimeCellHtml);
        }
        else {
            lastTimeCell.rowSpan += 1;
        }
    })
        .catch(error => console.error('Error:', error));
}
function submitForms() {
    document.querySelectorAll('form').forEach(form => {
        const event = new Event('submit');
        form.dispatchEvent(event);
    });
    const lastTimeCell = document.getElementById('last-time-cell');
    if (!lastTimeCell.hasAttribute('end-time')) {
        lastTimeCell.innerHTML += ` - ${getCurrentFormattedTime()}`;
    }
    const unixTimestamp = Math.floor(Date.now() / 1000);
    lastTimeCell.setAttribute('end-time', `${unixTimestamp}`);
    lastTimeCell.setAttribute('time-period-ended', 'true');
}
const locationName = JSON.parse(document.getElementById('location-name').textContent);
const locationSocket = new WebSocket('ws://'
    + window.location.host
    + '/fill-out/'
    + locationName
    + '/');
locationSocket.onopen = function (event) {
    console.log('Connection opened');
};
locationSocket.onmessage = function (event) {
    console.log('message received');
    console.log(event.data);
};
locationSocket.onclose = function (event) {
    console.error('Connection closed unexpectedly');
};
