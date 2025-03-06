
/**
 * Utility functions for geolocation, alert handling, and CSRF token updates.
 */

/**
 * Get the IP's geolocation if enabled in the browser.
 * @returns {Promise<Object>} A promise that resolves with an object containing latitude and longitude.
 * @throws {Error} If geolocation is not supported by the browser or if there is an error getting the geolocation.
 */
export function getGeolocation() {
    return new Promise((resolve, reject) => {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    // Success callback
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                },
                (error) => {
                    // Error callback
                    reject(new Error("Error getting geolocation: " + error.message));
                }
            );
        } else {
            reject(new Error("Geolocation is not supported by this browser."));
        }
    });
};

/**
 * Display a banner at the top of the page with a success or warning message.
 * @param {Object} message - The message object.
 * @param {boolean} message.success - Indicates if the message is a success or warning.
 * @param {string} message.message - The message text to display.
 */
export const handleAlerts = (message) => {
    if (message.success == true) {
        var type = 'success';
    } else if (message.success == false) {
        var type = 'warning';
    } else { ; };
    const alertBox = document.getElementById('alert-box');
    alertBox.innerHTML = `
            <div class="alert alert-${type} alert-dismissible " role="alert">
                    ${message.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
            </div>`;
    alertBox.classList.remove('d-none');
    setTimeout(() => {
        alertBox.classList.add('d-none');
    }, 5000);
};

/**
 * Update the CSRF token value if it changes.
 * @returns {string} The updated CSRF token.
 */
export const getCSRFToken = () => {
    return document.cookie
      .split("; ")
      .find(row => row.startsWith("csrftoken="))
      .split("=")[1];
  };
  


  export function saveProject(saveProjectUrl, project) {
  
    project.updated = Date.now();

    fetch(saveProjectUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      body: JSON.stringify(project)
    })
      .then(response => response.json())
      .then(data => {
        console.log('data', data);
        handleAlerts(data.message);
      });
};