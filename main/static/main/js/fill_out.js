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
        console.log(data.location + ' ' + data.zone + ' ' + data.mark + ' ' + data.is_approved);
    })
        .catch(error => console.error('Error:', error));
});
function submitForms() {
    document.querySelectorAll('form').forEach(form => {
        const event = new Event('submit');
        form.dispatchEvent(event);
    });
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
        // NOTE: This is a workaround, `insertBefore` doesn't work for some reason.
        if (table.rows.length > 1) {
            const lastRow = table.rows[table.rows.length - 1];
            lastRow.insertAdjacentHTML('beforebegin', data.new_row_html);
        }
        else {
            table.insertAdjacentHTML('beforeend', data.new_row_html);
        }
    })
        .catch(error => console.error('Error:', error));
}
