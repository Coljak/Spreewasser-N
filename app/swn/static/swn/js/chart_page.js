console.log("chart_page");

const endpoint = "chartdata/";
const chartDiv = document.getElementById("chartDiv")
const crop = document.getElementById("id_Feldfrucht")

// chart params

const getChart = function () {
    chartDiv.innerHTML = '<canvas id="Chart"></canvas>'
    const ctx = document.getElementById("Chart")
    console.log("Feldfrucht:", crop.value)
    $.ajax({
        method: "GET",
        url: endpoint + crop.value,

        success: function (data) {
            console.log('SUCCESS data: ', data)
            const chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.Date,
                    datasets: [{
                        yAxisID: 'y',
                        label: "Bodenfeuchte 1",
                        data: data.Mois_1,
                        borderColor: "#aa8800",
                        borderWidth: 2,
                        },
                        {
                        yAxisID: 'y',
                        label: "Bodenfeuchte 2",
                        data: data.Mois_2,
                        borderColor: "#ccaa00",
                        borderWidth: 2,
                        },
                        {
                        yAxisID: 'y',
                        label: "Bodenfeuchte 3",
                        data: data.Mois_3,
                        borderColor: "#ffcc00",
                        borderWidth: 2,
                        },
                        {
                        yAxisID: 'y1',
                        label: "LAI",
                        data: data.LAI,
                        borderWidth: 2,
                        borderColor: "#00cc22",
                        }],
                    },
                options: {
                    
                    elements: {
                        point: {
                        radius: 0,
                        },
                    },
                    responsive: true,
                    scales: {
                        y: {
                            // id: 'y',
                            type: 'linear',
                            position: 'left',
                            ticks: {
                                min: 0,
                                max: data.mois_max * 1.1,
                                }
                            },
                        y1: {
                            // id: 'y1',
                            type: 'linear',
                            position: 'right',
                            label: 'LAI',
                            ticks: {
                                min: 0,
                                max: data.lai_max * 1.1,
                                color: "#00cc22",
                                }
                            }
                        }
                    }
            });

            chart.update()
        },
        error: function (error_data) {
        console.log('Chart error: ', error_data);
        },
    });
};
