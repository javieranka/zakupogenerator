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

// 