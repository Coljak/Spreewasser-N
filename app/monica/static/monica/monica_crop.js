document.addEventListener('DOMContentLoaded', function() {
    var speciesParameters = document.getElementById('id_species_parameters');
    var cultivarParameters = document.getElementById('id_cultivar_parameters');
    speciesParameters.addEventListener('change', function() {
        var speciesId = this.value;
        if (speciesId) {
            // TODO write speciesId to cookie
            fetch('/monica/get_cultivar_parameters/' + speciesId + '/')
                .then(response => response.json())
                .then(data => {
                    console.log("DATA: ", data)
                    var cultivarParameters = document.getElementById('id_cultivar_parameters');
                    cultivarParameters.innerHTML = '';
                    for (var i = 0; i < data.cultivars.length; i++) {
                        var cultivar = data.cultivars[i];
                        var option = document.createElement('option');
                        option.value = cultivar.id;
                        option.textContent = cultivar.name;
                        cultivarParameters.appendChild(option);
                    }
                });
    
        } else {
            var cultivarParameters = document.getElementById('id_cultivar_parameters');
            cultivarParameters.innerHTML = '';
        }
    });
});

