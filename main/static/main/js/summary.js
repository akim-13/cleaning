document.addEventListener('DOMContentLoaded', function(){
    flatpickr("#start_date", {
    altInput: true,
    altFormat: "F j, Y",
    dateFormat: "Y-m-d",
    });

    flatpickr("#end_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
    });
});