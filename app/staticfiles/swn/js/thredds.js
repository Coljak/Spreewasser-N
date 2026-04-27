
// Get all folder icons and replace the img elements with them
const imgElements = document.querySelectorAll("Folder");
for (let i = 0; i < imgElements.length; i++) {
    const folderIcon = document.createElement('i');
    folderIcon.classList.add('bi', 'bi-folder');
    imgElements[i].parentNode.replaceChild(folderIcon, imgElements[i]);
}

document.getElementById('thredds-content').innerHTML = '<p class="text-muted">Click on a folder to see its content.</p>';
// Get all links and replace the attributes
document.getElementByClassName('threddsContent').addEventListener('click', function (event) {
    // Check if the clicked element is a link
    if (event.target.tagName === 'a') {
        // Prevent the default behavior of the link
        if (!event.target.pathname.startsWith('https')) {
            return;
        }
        else {

        
            event.preventDefault();

            // Fetch the content of the clicked Thredds page via Django view
            fetch(`/thredds-proxy${event.target.pathname}`)
                .then(response => response.text())
                .then(content => {
                    // Update the content of the 'thredds-content' div
                    document.getElementById('threddsContent').innerHTML = content;
                })
                .catch(error => {
                    console.error('Error fetching Thredds page via Django view:', error);
                });
        }
    }
});