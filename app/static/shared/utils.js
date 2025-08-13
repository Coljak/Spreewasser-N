
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
            // reject(new Error("Geolocation is not supported by this browser."));
            return {
                latitude: 52.40,
                longitude: 14.174,
            };
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
  


  export function saveProject(project) {
  
    project.updated = Date.now();

    fetch('save-project/', {
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


/**
 * Sets the language for Bootstrap datepickers.
 *
 * @param {string} language_code - The language code to set for the datepicker.
 */
export function setLanguage(language_code){
    console.log('setLanguage', language_code);
    $('.datepicker').datepicker({
        language: language_code,
        autoclose: true
    })
};

export const populateDropdown = (data, dropdown) => {
    console.log('populateDropdown', data, dropdown);
    dropdown.innerHTML = '';
    data.options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.id;
        optionElement.text = option.name;
        dropdown.appendChild(optionElement);
    });       
};

export const addToDropdown = (id, name, dropdown) => {
    console.log('addToDropdown', id, name, dropdown);
 
    const optionElement = document.createElement('option');
    optionElement.value = id;
    optionElement.text = name;
    dropdown.appendChild(optionElement);
    dropdown.value = id;
    $(dropdown).trigger('change');
      
};

// function to check when the update of a dropdown menu is finished
/**
 * Observes a dropdown element for changes in its child nodes (options) and executes a callback function when options are added.
 *
 * @param {string} selector - The CSS selector for the dropdown element to observe.
 * @param {Function} callback - The callback function to execute when options are added to the dropdown.
 */
export function observeDropdown (selector, callback) {
    // console.log('observeDropdown', selector);
    const dropdown = document.querySelector(selector);
    if (!dropdown) 
        {
            console.error(`Dropdown not found: ${selector}`);
            return; // Exit if dropdown does not exist
        }
    if (dropdown.options.length > 0) {
        callback(dropdown);
        return; // Exit if options are already loaded
    }

    const observer = new MutationObserver((mutations, obs) => {
        mutations.forEach(mutation => {
            if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
                callback(dropdown);
                obs.disconnect(); // Stop observing after options are loaded
            }
        });
    });

    observer.observe(dropdown, { childList: true });
};

export function getBsColor(varName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(varName)
        .trim();
};

