// 
$(document).ready(function() {
    $('#myTable').DataTable({
        "paging": false, 
        "ordering": true, 
        "searching": false,
        "order": [
            // [0, "asc"]
        ], // default order by first column disabled
        "info": false, // pagination info
        language: {
            // url: '//cdn.datatables.net/plug-ins/2.2.1/i18n/pl.json',
            // paginate: {
            //     first: "↶",    
            //     previous: "←",
            //     next: "→",         
            //     last: "↷",   
            // }
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById("submitButton");
    const spinner = document.getElementById("spinner");
    const form = document.querySelector("form");

    submitButton.addEventListener("click", function (event) {
        event.preventDefault(); // Zapobiega domyślnemu wysłaniu formularza
        submitButton.hidden = true; // Ukrywa przycisk
        spinner.hidden = false; // Pokazuje spinner
        form.submit(); // Wysyła formularz
    });
});



function printTable() {
    // print table with id myTable with light mode
    var style = "<style> \
    table {width: 100%; border-collapse: collapse;} \
    th, td {border: 1px solid black; padding: 8px; text-align: left;} \
    </style>";
    var div = document.createElement('div');
    div.innerHTML = style + document.getElementById('myTable').outerHTML;
    var printWindow = window.open('', '', 'height=400,width=800');
    printWindow.document.write(div.innerHTML);
    printWindow.document.close();
    printWindow.print();

}
// 
