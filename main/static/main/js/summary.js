document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr for start and end date inputs
    const startDatePicker = flatpickr("#start_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        defaultDate: document.getElementById('start_date').value || null  
    });

    const endDatePicker = flatpickr("#end_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        defaultDate: document.getElementById('end_date').value || null  
    });

    // Check if there are any messages to display
    if (document.querySelector('.messages')) {
        setTimeout(function() {
            document.querySelector('.messages').style.display = 'none';
        }, 5000);
    }
});
