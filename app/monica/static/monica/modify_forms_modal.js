
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('modifyResidueBtn').addEventListener('click', function() {
        const speciesId = document.querySelector('[name="species"]').value;
        if (speciesId) {
            fetch(`/get-residue-parameters/${speciesId}/`)
                .then(response => response.json())
                .then(data => {
                    // Populate the residue modal form with data
                    document.getElementById('id_name').value = data.name;
                    document.getElementById('id_description').value = data.description;
                    // Populate other fields as necessary
                })
                .catch(error => console.error('Error:', error));
        }
    });

    document.getElementById('saveResidueParameters').addEventListener('click', function() {
        const residueForm = document.getElementById('residueForm');
        const formData = new FormData(residueForm);

        fetch('/save-residue-parameters/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Ensure you have a function to get CSRF token
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Residue parameters saved successfully.');
                document.getElementById('residueModal').modal('hide');
            } else {
                alert('Error saving residue parameters.');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

