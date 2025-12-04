// Location service for Foodie.AI
// Handles user location detection and zipcode to neighborhood mapping

let userLocation = null;

/**
 * Get user's current location using browser geolocation API
 */
async function getUserLocation() {
    const locationBtn = document.getElementById('locationBtn');
    const locationBtnText = document.getElementById('locationBtnText');
    const locationInfo = document.getElementById('locationInfo');
    
    if (!navigator.geolocation) {
        showLocationError('Geolocation is not supported by your browser.');
        return;
    }
    
    locationBtn.classList.add('loading');
    locationBtnText.textContent = 'Locating...';
    locationInfo.classList.remove('show');
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            
            try {
                // Use OpenStreetMap Nominatim API for reverse geocoding (free, no API key needed)
                const response = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`,
                    {
                        headers: {
                            'User-Agent': 'FoodieAI-LocationApp/1.0'
                        }
                    }
                );
                
                const data = await response.json();
                
                if (data && data.address) {
                    const address = data.address;
                    const zipcode = address.postcode || 'Not available';
                    const city = address.city || address.town || address.village || address.county || '';
                    const state = address.state || '';
                    const country = address.country || '';
                    
                    userLocation = {
                        latitude,
                        longitude,
                        zipcode,
                        city,
                        state,
                        country,
                        fullAddress: data.display_name
                    };
                    
                    // Display location info
                    locationInfo.innerHTML = `
                        <i class="fas fa-check-circle"></i>
                        <strong>Location found:</strong> ${zipcode !== 'Not available' ? `Zipcode: ${zipcode}` : 'Location detected'} 
                        ${city ? `| ${city}` : ''} ${state ? `, ${state}` : ''} ${country ? `, ${country}` : ''}
                    `;
                    locationInfo.classList.add('show');
                    locationInfo.style.borderLeftColor = '#ffd60a';
                    
                    locationBtnText.textContent = 'Location Set';
                    locationBtn.style.background = 'linear-gradient(135deg, #4caf50, #66bb6a)';
                    locationBtn.style.borderColor = '#4caf50';
                    
                    // Clear neighborhood select since location is now set (mutually exclusive)
                    const neighborhoodSelect = document.getElementById('neighborhoodSelect');
                    neighborhoodSelect.value = '';
                    
                    // Try to match neighborhood using backend API
                    if (zipcode !== 'Not available') {
                        try {
                            const neighborhoodResponse = await fetch(`/api/neighborhood-by-zipcode/${zipcode}`);
                            const neighborhoodData = await neighborhoodResponse.json();
                            
                            if (neighborhoodData.found && neighborhoodData.neighborhood) {
                                // Automatically select the matched neighborhood
                                neighborhoodSelect.value = neighborhoodData.neighborhood;
                                
                                // Update location info to show matched neighborhood
                                const neighborhoodDisplay = neighborhoodData.neighborhood
                                    .replace(/-/g, ' ')
                                    .replace(/\b\w/g, l => l.toUpperCase());
                                
                                locationInfo.innerHTML = `
                                    <i class="fas fa-check-circle"></i>
                                    <strong>Location found:</strong> Zipcode: ${zipcode}
                                    ${city ? `| ${city}` : ''} ${state ? `, ${state}` : ''} ${country ? `, ${country}` : ''}
                                    <br><span style="color: #ffd60a; font-size: 0.9rem;">✓ Automatically selected neighborhood: ${neighborhoodDisplay}</span>
                                `;
                                locationInfo.style.borderLeftColor = '#ffd60a';
                                
                                // Clear userLocation since we're using neighborhood instead
                                userLocation = null;
                            } else {
                                // Keep userLocation for zipcode-based search
                                locationInfo.innerHTML = `
                                    <i class="fas fa-check-circle"></i>
                                    <strong>Location found:</strong> Zipcode: ${zipcode}
                                    ${city ? `| ${city}` : ''} ${state ? `, ${state}` : ''} ${country ? `, ${country}` : ''}
                                    <br><span style="color: #b0c4de; font-size: 0.9rem;">Note: Zipcode not in Manhattan neighborhoods list</span>
                                `;
                            }
                        } catch (error) {
                            console.error('Error fetching neighborhood:', error);
                            // Keep the basic location info if API call fails
                        }
                    }
                } else {
                    showLocationError('Could not retrieve address information.');
                }
            } catch (error) {
                console.error('Reverse geocoding error:', error);
                showLocationError('Error retrieving location details. Coordinates: ' + latitude.toFixed(4) + ', ' + longitude.toFixed(4));
            } finally {
                locationBtn.classList.remove('loading');
            }
        },
        (error) => {
            locationBtn.classList.remove('loading');
            locationBtnText.textContent = 'Get Location';
            
            let errorMessage = 'Error getting location: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Permission denied. Please enable location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Location request timed out.';
                    break;
                default:
                    errorMessage += 'Unknown error occurred.';
                    break;
            }
            showLocationError(errorMessage);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * Show location error message
 */
function showLocationError(message) {
    const locationInfo = document.getElementById('locationInfo');
    locationInfo.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <strong>Error:</strong> ${message}
    `;
    locationInfo.classList.add('show');
    locationInfo.style.borderLeftColor = '#f44336';
}

/**
 * Handle neighborhood select change
 */
function handleNeighborhoodChange() {
    const neighborhoodSelect = document.getElementById('neighborhoodSelect');
    const locationInfo = document.getElementById('locationInfo');
    const locationBtn = document.getElementById('locationBtn');
    const locationBtnText = document.getElementById('locationBtnText');
    
    // Clear location when neighborhood is manually selected
    if (neighborhoodSelect.value) {
        userLocation = null;
        locationInfo.classList.remove('show');
        locationBtnText.textContent = 'Get My Location';
        locationBtn.style.background = 'linear-gradient(135deg, #1b263b, #0d1b2a)';
        locationBtn.style.borderColor = '#ffd60a';
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getUserLocation,
        showLocationError,
        handleNeighborhoodChange,
        get userLocation() { return userLocation; },
        set userLocation(value) { userLocation = value; }
    };
}

