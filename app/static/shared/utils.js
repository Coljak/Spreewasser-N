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
}
