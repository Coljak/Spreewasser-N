console.log("chart_page")

const endpoint = '/chartdata/'

// chart params


$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        console.log(data)

    const ctx = document.getElementById('myChart');

    new Chart(ctx, {
    type: 'line',
    data: {
            labels: data.Date,
            datasets: [{
            label: 'Bodenfeuchte 1',
            data: data.Mois_1,
            borderColor: '#aa8800',
            borderWidth: 2
        },
        {
            label: 'Bodenfeuchte 2',
            data: data.Mois_2,
            borderColor: '#ccaa00',
            borderWidth: 2
        },
        {
            label: 'Bodenfeuchte 3',
            data: data.Mois_3,
            borderColor: '#ffcc00',
            borderWidth: 2
        },
        {
            label: 'LAI',
            data: data.LAI,
            borderWidth: 2,
            borderColor: '#00cc22',
        },
        // {
        //     label: 'Niederschlag',
        //     data: data.Precip,
        //     borderWidth: 1,
        //     borderColor: '#00ccbb',
        //     type: 'bar'
        // },
        
    ]
    },
    options: {
        elements: {
            point:{
                radius: 0
            }
        },
        responsive: true,
        scales: {
        y: {
            display: true,
            position: 'left',
            beginAtZero: true
        },
        y1: {
            display: true,
            position: 'right',
            beginAtZero: true
        }
        }
    }
    });

        },
        error: function(error_data){
            console.log(error_data)
        }
    });

