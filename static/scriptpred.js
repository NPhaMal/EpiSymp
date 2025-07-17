window.addEventListener('DOMContentLoaded', () => {
    var table = document.getElementById('myTable');
    var rows = table.getElementsByTagName('tr');
    var stable = document.getElementById('sympTable');
    var srows = stable.getElementsByTagName('tr');

    // Loop through each row and add a click event listener
    for (var i = 0; i < rows.length; i++) {
        rows[i].addEventListener('click', function() {
            // Get the selected row data
            var cells = this.getElementsByTagName('td');
            var rowData = [];
            for (var j = 0; j < cells.length; j++) {
                rowData.push(cells[j].textContent);
            }

            // Display the row data in the console
            console.log(rowData);
        });
    }

    for (var i = 0; i < srows.length; i++) {
        srows[i].addEventListener('click', function() {
            // Get the selected row data
            var cells = this.getElementsByTagName('td');
            var rowData = [];
            for (var j = 0; j < cells.length; j++) {
                rowData.push(cells[j].textContent);
            }

            // Display the row data in the console
            console.log(rowData);
        });
    }
});