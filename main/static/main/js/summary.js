document.addEventListener('DOMContentLoaded', function() {
    // Get the values from the input fields to set as default dates
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    flatpickr("#start_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        defaultDate: startDate ? startDate : null  
    });

    flatpickr("#end_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        defaultDate: endDate ? endDate : null  
    });

    if (document.querySelector('.messages')) {
        setTimeout(function() {
            window.location.reload();
        }, 5000);
    }
});
