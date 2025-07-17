document.addEventListener('DOMContentLoaded', function() {
    var searchForm = document.getElementById("search-fom");

    searchForm.addEventListener("submit", function(event) {
        event.preventDefault();
        var query = document.getElementById("query-input").value;
    
        // Make an AJAX request to the backend for search results
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "statsearch?q=" + encodeURIComponent(query));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    displaySearchResults(response);
                } else {
                    console.log("Error:", xhr.status);
                }
            }
        };
        xhr.send();
    });

    function displaySearchResults(results) {
        var searchResultsContainer = document.getElementById("search-results");
        searchResultsContainer.innerHTML = ''; // Clear previous results

        if (results.reply === 0){
            searchResultsContainer.innerHTML = "<h2 style='color: white; text-align: center; margin-top: 2rem;'>No results found for your search.</h2>";
            return;
        }

        // Create containers within a card structure for consistent styling
        searchResultsContainer.innerHTML = `
            <div class="card">
                <h3 class="card-title">Chloropleth Map for ${results.graph_title}</h3>
                <div id="smap"></div>
            </div>
            <div class="card">
                <h3 class="card-title">Distribution of People Diagnosed with ${results.graph_title} by Suburb</h3>
                <div id="statchart"></div>
            </div>
            <div class="card">
                <h3 class="card-title">Highest Disease Diagnosis Counts</h3>
                <div id="table-container" class="table-wrapper"></div>
            </div>
            <div class="card">
                 <h3 class="card-title">Trend for ${results.graph_title} over time</h3>
                <div id="statlchart"></div>
            </div>
        `;

        // Update map, charts, and table with new data
        updateMap(results.map_data);
        updateChart(results.chart_data, results.graph_title);
        updateTable(results.table_data);
        updateLChart(results.line_data, results.graph_title);
    }

    // Function to update map
    function updateMap(mapdata){
        // Check if map container exists and destroy previous instance if it does
        var smapContainer = L.DomUtil.get('smap');
        if(smapContainer != null){
            smapContainer._leaflet_id = null;
        }

        var smap = L.map('smap').setView([-20.1457, 28.5873], 11);

        // Use the same dark theme as the main map
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(smap);

        L.geoJSON(mapdata, {
            style: function (feature) {
                return {
                    fillColor: getColor(feature.properties.Number_of_Diagnosed),
                    weight: 2,
                    opacity: 1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity: 0.7
                };
            }
        }).addTo(smap);

        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend'),
                grades = [0, 10, 20, 50, 100, 200, 500, 1000];
            div.innerHTML += '<strong>Cases</strong><br>';
            for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                    grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
            }
            return div;
        };
        legend.addTo(smap);
    }

    // get Chloropleth colors
    function getColor(d) {
        return d > 1000 ? '#800026' :
               d > 500  ? '#BD0026' :
               d > 200  ? '#E31A1C' :
               d > 100  ? '#FC4E2A' :
               d > 50   ? '#FD8D3C' :
               d > 20   ? '#FEB24C' :
               d > 10   ? '#FED976' :
                          '#FFEDA0';
    }

    // Common styling options for all search charts
    const commonChartOptions = {
        chart: {
            foreColor: '#ccc',
            toolbar: { show: false }
        },
        tooltip: {
            theme: 'dark'
        },
        xaxis: {
            labels: {
                style: {
                    colors: '#ccc'
                }
            },
             axisBorder: { show: false },
             axisTicks: { show: false }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#ccc'
                }
            }
        },
        grid: {
            borderColor: '#404040',
            strokeDashArray: 4
        },
        title: {
            align: 'left',
            style: {
                fontSize:  '18px',
                fontWeight:  '600',
                color: '#FFFFFF'
            }
        }
    };


    // Function to update the bar chart with search results
    function updateChart(graphdata, gtitle){
        var chartData = graphdata;
        var categories = chartData.map(item => item[0]);
        var values = chartData.map(item => item[1]);

        var options = {
            ...commonChartOptions,
            series: [{ name: 'Value', data: values }],
            chart: { ...commonChartOptions.chart, type: 'bar', height: 450 },
            plotOptions: {
                bar: {
                    distributed: true,
                    borderRadius: 4,
                    horizontal: true,
                }
            },
            xaxis: { ...commonChartOptions.xaxis, categories: categories },
            yaxis: { ...commonChartOptions.yaxis },
            legend: { show: false },
            title: { ...commonChartOptions.title, text: `Distribution for ${gtitle}` }
        };

        var chart = new ApexCharts(document.querySelector("#statchart"), options);
        chart.render();
    }

    // Function to update the line chart with search results
    function updateLChart(graphdata, gtitle){
        var chartData = graphdata;
        var categories = chartData.map(item => item[0]);
        var values = chartData.map(item => item[1]);

        var options = {
            ...commonChartOptions,
            series: [{ name: 'Value', data: values }],
            chart: { ...commonChartOptions.chart, type: 'area', height: 350 },
            xaxis: { ...commonChartOptions.xaxis, categories: categories, type: 'datetime' },
            stroke: { curve: 'smooth', width: 2 },
            fill: {
                type: "gradient",
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.1,
                    stops: [0, 90, 100]
                }
            },
            dataLabels: { enabled: false },
            title: { ...commonChartOptions.title, text: `Trend for ${gtitle}` }
        };

        var chart = new ApexCharts(document.querySelector("#statlchart"), options);
        chart.render();
    }
    
    // Function to update the table with search results
    function updateTable(data) {
        var tableContainer = $('#table-container');
        tableContainer.empty();

        var table = $('<table>').addClass('data-table');
        var thead = $('<thead>').appendTo(table);
        var tbody = $('<tbody>').appendTo(table);

        var headerRow = $('<tr>').appendTo(thead);
        $('<th>').text('Disease').appendTo(headerRow);
        $('<th>').text('Infected').appendTo(headerRow);
        $('<th>').text('Suburb Most Infected').appendTo(headerRow);
        $('<th>').text('Number in Suburb').appendTo(headerRow);

        $.each(data, function(index, item) {
            var row = $('<tr>').appendTo(tbody);
            $('<td>').text(item.Disease).appendTo(row);
            $('<td>').text(item.Infected).appendTo(row);
            $('<td>').text(item.Suburb_Most_Infected).appendTo(row);
            $('<td>').text(item.Number_Infected_in_Suburb).appendTo(row);
        });

        tableContainer.append(table);
    }
});