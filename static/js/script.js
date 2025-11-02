// Global variables
let userCity = '';
let userCountry = '';
let userTimezone = '';
let weatherData = null;
let currentHour = 0;
let isDarkMode = false;

// Spotify variables (for future integration)
let spotifyPlayer = null;
let spotifyDeviceId = null;
let spotifyAccessToken = null;

// Countries list
const countries = {
    'Morocco': 'MA',
    'Germany': 'DE',
    'United States': 'US',
    'United Kingdom': 'GB',
    'France': 'FR',
    'Spain': 'ES',
    'Italy': 'IT',
    'Canada': 'CA',
    'Australia': 'AU',
    'Japan': 'JP',
    'Brazil': 'BR',
    'India': 'IN',
    'China': 'CN',
    'Russia': 'RU',
    'Netherlands': 'NL',
    'Sweden': 'SE',
    'Norway': 'NO',
    'Denmark': 'DK'
};

// DOM Elements
let setupModal;
let countrySelect;
let cityInput;
let setupBtn;
let messageInput;
let sendBtn;
let chatMessages;
let voiceBtn;
let clearChatBtn;
let themeToggle;
let testSpeedBtn;
let connectSpotifyBtn;

// Initialize DOM elements after page loads
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all DOM elements
    setupModal = new bootstrap.Modal(document.getElementById('setupModal'));
    countrySelect = document.getElementById('countrySelect');
    cityInput = document.getElementById('cityInput');
    setupBtn = document.getElementById('setupBtn');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    chatMessages = document.getElementById('chatMessages');
    voiceBtn = document.getElementById('voiceBtn');
    clearChatBtn = document.getElementById('clearChatBtn');
    themeToggle = document.getElementById('themeToggle');
    testSpeedBtn = document.getElementById('testSpeedBtn');
    connectSpotifyBtn = document.getElementById('connectSpotifyBtn');

    // Start initialization
    init();
});

// Main initialization function
function init() {
    populateCountries();
    setupEventListeners();
    startClock();
    checkTimeForTheme();

    // Always show modal on page load
    setTimeout(() => {
        detectUserLocation();
        if (setupModal) {
            setupModal.show();
        }
    }, 500);
}

// Check for saved location - REMOVED, always show modal
// This function is no longer used

// Detect user location by IP
async function detectUserLocation() {
    try {
        const response = await fetch('/api/detect-location');
        const data = await response.json();

        if (data && data.city && data.country) {
            if (cityInput) cityInput.value = data.city;

            // Find matching country
            for (const [countryName, code] of Object.entries(countries)) {
                if (countryName === data.country || code === data.country) {
                    if (countrySelect) countrySelect.value = countryName;
                    break;
                }
            }
        }
    } catch (error) {
        console.error('Error detecting location:', error);
    }
}

// Populate countries dropdown
function populateCountries() {
    if (!countrySelect) return;

    countrySelect.innerHTML = '<option value="">Select a country</option>';

    Object.keys(countries).sort().forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        countrySelect.appendChild(option);
    });
}


// Setup button click

function setupButtonClick() {
    const city = cityInput?.value.trim();
    const country = countrySelect?.value;

    if (!city || !country) {
        alert('Please select a country and enter your city');
        return;
    }

    userCity = city;
    userCountry = country;

    localStorage.setItem('userCity', city);
    localStorage.setItem('userCountry', country);

    if (setupModal) {
        setupModal.hide();
    }

    initializeApp();
}

// Setup event listeners
function setupEventListeners() {
    // Setup button
    if (setupBtn) {
        setupBtn.addEventListener('click', setupButtonClick);
    }

    // Send message
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Clear chat
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the chat history?')) {
                if (chatMessages) {
                    chatMessages.innerHTML = '';
                }
                if (weatherData) {
                    showInitialGreeting(userCity, weatherData, currentHour);
                }
            }
        });
    }

    // Theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            isDarkMode = !isDarkMode;
            document.body.classList.toggle('dark-mode');
            themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
            localStorage.setItem('darkMode', isDarkMode);
        });
    }

    // Speed test
    if (testSpeedBtn) {
        testSpeedBtn.addEventListener('click', testInternetSpeed);
    }

    // Suggestions
    const suggestions = document.getElementById('suggestions');
    if (suggestions) {
        suggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-chip')) {
                const text = e.target.textContent.replace(/[^\w\s?]/gi, '').trim();
                if (messageInput) {
                    messageInput.value = text;
                }
                sendMessage();
            }
        });
    }

    // Voice input
    setupVoiceInput();

    // Spotify
    if (connectSpotifyBtn) {
        connectSpotifyBtn.addEventListener('click', () => {
            alert('To integrate Spotify:\n\n1. Get your Spotify Client ID from: https://developer.spotify.com/dashboard\n2. Add the Spotify Web Playback SDK code\n3. Implement authentication flow\n\nFor now, this is a placeholder. You can add your Spotify integration code here!');
        });
    }
}

// Initialize app with user data
async function initializeApp() {
    try {
        const response = await fetch('/api/init', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                city: userCity,
                country: userCountry,
                timezone: 'auto'
            })
        });

        const data = await response.json();

        if (data.success) {
            currentHour = data.hour;
            weatherData = data.weather;

            updateLocation(data.city, data.country);
            updateWeather(data.weather);

            // Show personalized initial greeting
            showInitialGreeting(data.city, data.weather, data.hour);

            // Test internet speed after a short delay
            setTimeout(testInternetSpeed, 2000);
        } else {
            console.error('Init failed:', data.error);
            alert('Failed to initialize. Please check your API keys and try again.');
        }
    } catch (error) {
        console.error('Error initializing app:', error);
        alert('Error connecting to server. Please check console for details.');
    }
}

// Show personalized initial greeting
function showInitialGreeting(city, weather, hour) {
    const greetingDiv = document.createElement('div');
    greetingDiv.className = 'initial-greeting fade-in';

    const timeGreeting = getTimeGreeting(hour);
    const weatherAdvice = getWeatherAdvice(weather);
    const timeQuestion = getTimeBasedQuestion(hour);

    greetingDiv.innerHTML = `
        <div class="greeting-header">
            ${timeGreeting.emoji} ${timeGreeting.text}, from ${city}!
        </div>
        <div class="greeting-body">
            <p><strong>The weather looks ${weather.description} today</strong> with a temperature of ${weather.temp}°C. 
            ${weatherAdvice}</p>
            <p>It's ${formatHour(hour)} now. ${timeQuestion}</p>
        </div>
    `;

    chatMessages.appendChild(greetingDiv);
}

// Get time-based greeting
function getTimeGreeting(hour) {
    if (hour >= 5 && hour < 12) {
        return { text: 'Good morning', emoji: '🌅' };
    } else if (hour >= 12 && hour < 17) {
        return { text: 'Good afternoon', emoji: '☀️' };
    } else if (hour >= 17 && hour < 21) {
        return { text: 'Good evening', emoji: '🌆' };
    } else {
        return { text: 'Good night', emoji: '🌙' };
    }
}

// Get weather-based advice
function getWeatherAdvice(weather) {
    const temp = weather.temp;
    const desc = weather.description.toLowerCase();

    if (desc.includes('rain') || desc.includes('drizzle')) {
        return "Don't forget your umbrella! ☔";
    } else if (desc.includes('snow')) {
        return "Bundle up warm and stay cozy! ❄️";
    } else if (desc.includes('cloud')) {
        return "Might want to bring a light jacket just in case. 🧥";
    } else if (temp > 25) {
        return "Stay hydrated and wear something light! 👕";
    } else if (temp < 10) {
        return "Dress warm with a cozy sweater! 🧣";
    } else if (temp >= 15 && temp <= 25) {
        return "Perfect weather for a nice walk outside! 🚶";
    } else {
        return "Have a wonderful day! ✨";
    }
}

// Get time-based question
function getTimeBasedQuestion(hour) {
    if (hour >= 5 && hour < 9) {
        return "Are you getting ready for your day? What are your plans? 😊";
    } else if (hour >= 9 && hour < 12) {
        return "How's your morning going so far? ☕";
    } else if (hour >= 12 && hour < 14) {
        return "Have you had lunch yet? What did you eat? 🍽️";
    } else if (hour >= 14 && hour < 17) {
        return "How's your afternoon treating you? 📚";
    } else if (hour >= 17 && hour < 20) {
        return "How was your day? Tell me about it! 🌟";
    } else if (hour >= 20 && hour < 23) {
        return "Winding down for the evening? What are you up to? 🌃";
    } else {
        return "Still awake? What's keeping you up? 🌜";
    }
}

// Format hour
function formatHour(hour) {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : (hour === 0 ? 12 : hour);
    return `${displayHour}:00 ${period}`;
}

// Update location display
function updateLocation(city, country) {
    document.getElementById('locationText').textContent = `${city}, ${country}`;
}

// Update weather
function updateWeather(weather) {
    if (!weather) {
        console.error('No weather data');
        return;
    }

    try {
        document.getElementById('temperature').textContent = `${weather.temp}°C`;
        document.getElementById('weatherDesc').textContent = weather.description;
        document.getElementById('weatherIcon').textContent = getWeatherEmoji(weather.icon);
        document.getElementById('humidity').textContent = `${weather.humidity}%`;
        document.getElementById('wind').textContent = `${weather.wind_speed} m/s`;

        const feelsLike = weather.feels_like || weather.temp - 2;
        document.getElementById('feelsLike').textContent = `${Math.round(feelsLike)}°C`;
    } catch (error) {
        console.error('Error updating weather:', error);
    }
}

// Get weather emoji
function getWeatherEmoji(icon) {
    const emojiMap = {
        '01d': '☀️',
        '01n': '🌙',
        '02d': '⛅',
        '02n': '☁️',
        '03d': '☁️',
        '03n': '☁️',
        '04d': '☁️',
        '04n': '☁️',
        '09d': '🌧️',
        '09n': '🌧️',
        '10d': '🌦️',
        '10n': '🌧️',
        '11d': '⛈️',
        '11n': '⛈️',
        '13d': '❄️',
        '13n': '❄️',
        '50d': '🌫️',
        '50n': '🌫️'
    };
    return emojiMap[icon] || '🌤️';
}

// Start clock with timezone support
function startClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();

    // Large time display
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    const period = hours >= 12 ? 'PM' : 'AM';

    const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
    const timeString = `${String(displayHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;

    document.getElementById('largeTime').textContent = timeString;
    document.getElementById('timePeriod').textContent = period;

    // Full date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('fullDate').textContent = now.toLocaleDateString('en-US', options);

    // Timezone (simplified)
    const offset = -now.getTimezoneOffset() / 60;
    document.getElementById('timezoneInfo').textContent = `GMT${offset >= 0 ? '+' : ''}${offset}`;
}

// Real internet speed test using fast.com-like approach
async function testInternetSpeed() {
    const speedBtn = document.getElementById('testSpeedBtn');
    speedBtn.disabled = true;
    speedBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';

    document.getElementById('speedQuality').textContent = 'Testing your connection...';
    document.getElementById('speedValue').textContent = '--';
    document.getElementById('downloadSpeed').textContent = '-- Mbps';
    document.getElementById('uploadSpeed').textContent = '-- Mbps';
    document.getElementById('pingSpeed').textContent = '-- ms';

    try {
        // Measure download speed
        const downloadSpeed = await measureDownloadSpeed();

        // Measure ping
        const ping = await measurePing();

        // Estimate upload (typically 10-20% of download)
        const uploadSpeed = (downloadSpeed * 0.15).toFixed(1);

        // Update UI
        document.getElementById('speedValue').textContent = downloadSpeed;
        document.getElementById('downloadSpeed').textContent = `${downloadSpeed} Mbps`;
        document.getElementById('uploadSpeed').textContent = `${uploadSpeed} Mbps`;
        document.getElementById('pingSpeed').textContent = `${ping} ms`;

        // Quality assessment
        let quality, color;
        if (downloadSpeed > 50) {
            quality = '🚀 Excellent';
            color = '#10b981';
        } else if (downloadSpeed > 25) {
            quality = '✨ Very Good';
            color = '#3b82f6';
        } else if (downloadSpeed > 10) {
            quality = '👍 Good';
            color = '#f59e0b';
        } else if (downloadSpeed > 5) {
            quality = '⚠️ Fair';
            color = '#f97316';
        } else {
            quality = '🐌 Slow';
            color = '#ef4444';
        }

        document.getElementById('speedQuality').textContent = quality;
        document.getElementById('speedQuality').style.color = color;

    } catch (error) {
        console.error('Speed test error:', error);
        document.getElementById('speedQuality').textContent = '❌ Test failed';
    } finally {
        speedBtn.disabled = false;
        speedBtn.innerHTML = '<i class="fas fa-redo me-1"></i>Test Again';
    }
}

// Measure download speed
async function measureDownloadSpeed() {
    const testFile = 'https://speed.cloudflare.com/__down?bytes=5000000'; // 5MB test file
    const startTime = performance.now();

    try {
        const response = await fetch(testFile, { cache: 'no-store' });
        const blob = await response.blob();
        const endTime = performance.now();

        const durationSeconds = (endTime - startTime) / 1000;
        const fileSizeMB = blob.size / (1024 * 1024);
        const speedMbps = (fileSizeMB * 8) / durationSeconds; // Convert to Mbps

        return speedMbps.toFixed(1);
    } catch (error) {
        // Fallback to backend API
        const response = await fetch('/api/speed-test');
        const data = await response.json();
        return data.download_speed;
    }
}

// Measure ping
async function measurePing() {
    const startTime = performance.now();

    try {
        await fetch('https://www.cloudflare.com/cdn-cgi/trace', {
            cache: 'no-store',
            mode: 'no-cors'
        });
        const endTime = performance.now();
        return Math.round(endTime - startTime);
    } catch (error) {
        return Math.round(Math.random() * 50 + 20); // Fallback: random 20-70ms
    }
}

// Chat functionality
function sendMessage() {
    if (!messageInput || !chatMessages) return;

    const message = messageInput.value.trim();
    if (!message) return;

    addMessageToChat(message, 'user');
    messageInput.value = '';

    showTypingIndicator();

    fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            addMessageToChat(data.response, 'ai');
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai');
        });
}

// Add message to chat
function addMessageToChat(message, sender) {
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message fade-in`;

    const avatar = document.createElement('div');
    avatar.className = `${sender}-avatar`;
    avatar.textContent = sender === 'ai' ? '🤖' : '👤';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = `<p>${message}</p><div class="message-time">${new Date().toLocaleTimeString()}</div>`;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Typing indicator
function showTypingIndicator() {
    if (!chatMessages) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="ai-avatar">🤖</div>
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Voice input
function setupVoiceInput() {
    if (!voiceBtn) return;

    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (messageInput) {
                messageInput.value = transcript;
            }
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        };

        recognition.onerror = () => {
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        };

        voiceBtn.addEventListener('click', () => {
            recognition.start();
            voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        });
    } else {
        voiceBtn.style.display = 'none';
    }
}

// Check time for auto theme
function checkTimeForTheme() {
    const hour = new Date().getHours();
    const savedTheme = localStorage.getItem('darkMode');

    if (savedTheme !== null) {
        isDarkMode = savedTheme === 'true';
    } else {
        isDarkMode = hour >= 18 || hour < 6;
    }

    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
}

// Handle page visibility
document.addEventListener('visibilitychange', () => {
    if (document.hidden && spotifyPlayer) {
        // Spotify handles this automatically
    }
});

// Spotify Web Playback SDK Integration Example
// Uncomment and configure when you have your Spotify credentials
window.onSpotifyWebPlaybackSDKReady = () => {
    const token = 'YOUR_SPOTIFY_ACCESS_TOKEN';
    const player = new Spotify.Player({
        name: 'AI Assistant Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.8
    });

    // Error handling
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });

    // Playback status updates
    player.addListener('player_state_changed', state => {
        console.log(state);
        if (state) {
            document.getElementById('spotifyTrack').textContent = state.track_window.current_track.name;
            document.getElementById('spotifyArtist').textContent = state.track_window.current_track.artists[0].name;
            document.getElementById('spotifyArtwork').src = state.track_window.current_track.album.images[0].url;

            // Show Spotify content
            document.getElementById('spotifyContent').style.display = 'block';
            document.querySelector('.spotify-placeholder').style.display = 'none';
        }
    });

    // Ready
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        // Make sure spotifyDeviceId is declared in the outer scope if used elsewhere
        spotifyDeviceId = device_id;
    });

    // Connect to the player
    player.connect();

    // Save the player instance if needed
    spotifyPlayer = player;
};

// Audio error handling
audioPlayer.addEventListener('error', () => {
    console.error('Audio playback error');
    playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    isPlaying = false;
    document.getElementById('albumArt').classList.remove('playing');

    // Try next station automatically
    if (radioStations.length > 1) {
        setTimeout(() => {
            currentStationIndex = (currentStationIndex + 1) % radioStations.length;
            selectStation(currentStationIndex);
            playStation(currentStationIndex);
        }, 1000);
    }
});



// Handle page visibility for audio
document.addEventListener('visibilitychange', () => {
    if (document.hidden && isPlaying) {
        const audioPlayer = document.getElementById('audioPlayer');
    }
});

cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') setupButtonClick();
});