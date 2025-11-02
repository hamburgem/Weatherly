from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import requests
from datetime import datetime
import secrets
import random
from openai import OpenAI
import threading
import speedtest


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# API Keys (set these as environment variables)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-key')
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'your-weather-key')

# ===========================
# HELPER FUNCTIONS
# ===========================

def get_weather(city):
    """Fetch weather data from OpenWeatherMap"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'], 1),
                'feels_like': round(data['main']['feels_like'])
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None

def get_local_time(timezone):
    """Fetch local time from WorldTimeAPI"""
    try:
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('datetime', None)
    except Exception as e:
        print(f"Time API error: {e}")
    return None

def get_user_location_by_ip():
    """Get user location from IP"""
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city'),
                'country': data.get('country'),
                'timezone': data.get('timezone'),
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
    except Exception as e:
        print(f"Location API error: {e}")
    return None

def get_greeting(hour):
    """Generate greeting based on time"""
    if 5 <= hour < 12:
        return "Good morning", "🌅"
    elif 12 <= hour < 17:
        return "Good afternoon", "☀️"
    elif 17 <= hour < 21:
        return "Good evening", "🌆"
    else:
        return "Good night", "🌙"

def analyze_intent(message):
    """Simple NLP intent analysis"""
    message_lower = message.lower()
    
    # Mood detection
    if any(word in message_lower for word in ['bored', 'boring', 'nothing to do']):
        return 'bored'
    elif any(word in message_lower for word in ['weather', 'temperature', 'sunny', 'rain', 'cold', 'hot']):
        return 'weather'
    elif any(word in message_lower for word in ['time', 'what time', 'clock']):
        return 'time'
    elif any(word in message_lower for word in ['joke', 'fun', 'funny', 'laugh']):
        return 'joke'
    elif any(word in message_lower for word in ['music', 'song', 'spotify', 'play']):
        return 'music'
    elif any(word in message_lower for word in ['speed', 'internet', 'connection']):
        return 'speed'
    
    return 'general'

def get_ai_response(message, context):
    """Get AI response from OpenAI API or use fallback"""
    intent = analyze_intent(message)

    # --- Handle specific intents locally ---
    if intent == 'bored':
        return "Want me to play some music or tell you a joke? 🎵😄"
    elif intent == 'weather':
        weather = context.get('weather')
        if weather:
            return f"The weather is currently {weather['description']} with a temperature of {weather['temp']}°C. {get_weather_emoji(weather['description'])}"
        return "I don't have weather information right now."
    elif intent == 'time':
        return f"The current time is {datetime.now().strftime('%I:%M %p')} ⏰"
    elif intent == 'joke':
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "Why did the AI go to school? To improve its learning algorithm! 📚",
            "What's an AI's favorite snack? Computer chips! 🍟",
            "Why do Java developers wear glasses? Because they can't C#! 👓",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡"
        ]
        return random.choice(jokes)
    elif intent == 'music':
        return "I can play Spotify songs for you! Check the music player on the right side. 🎵"

    # --- Use OpenAI for normal chat ---
    try:
        city = context.get('city', 'your city')
        weather_info = context.get('weather', {})
        weather_desc = weather_info.get('description', 'unknown')
        temp = weather_info.get('temp', 'unknown')

        system_prompt = (
            f"You are a friendly and concise AI assistant. "
            f"The user is in {city}. Current weather: {weather_desc}, {temp}°C. "
            f"Provide helpful and relevant responses. (you can use the city/weather info if needed) "
            f"Keep responses under 300 words."
        )
        client =  OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",               
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.7
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        # Handles quota errors or connection issues
        if "insufficient_quota" in str(e):
            return "⚠️ My OpenAI account ran out of credits. Please check your API quota."
        elif "401" in str(e):
            return "⚠️ Invalid API key. Please check your OpenAI key."
        elif "429" in str(e):
            return "⚠️ Too many requests. Please wait a bit and try again."
        else:
            print(f"❌ Unexpected error: {e}")
            return f"An unexpected error occurred: {e}"
        
    # --- Fallbacks if API fails ---
    msg = message.lower()
    if any(w in msg for w in ['hello', 'hi', 'hey']):
        return "Hello! How can I help you today? 😊"
    elif any(w in msg for w in ['thank', 'thanks']):
        return "You're welcome! 😊"
    elif any(w in msg for w in ['bye', 'goodbye']):
        return "Goodbye! 👋"
    else:
        return "I'm here and ready to chat, but my main AI brain seems offline right now. 😅"
    
def get_weather_emoji(description):
    """Get emoji based on weather description"""
    description = description.lower()
    if 'clear' in description or 'sunny' in description:
        return '☀️'
    elif 'cloud' in description:
        return '☁️'
    elif 'rain' in description:
        return '🌧️'
    elif 'snow' in description:
        return '❄️'
    elif 'thunder' in description or 'storm' in description:
        return '⛈️'
    return '🌤️'

# ===========================
# ROUTES
# ===========================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_user():
    """Initialize user session with location"""
    try:
        data = request.json
        city = data.get('city')
        country = data.get('country')
        timezone = data.get('timezone')
        
        # Store in session
        session['city'] = city
        session['country'] = country
        session['timezone'] = timezone
        
        # Get weather
        weather = get_weather(city)
        
        # If weather fails, return mock data
        if not weather:
            weather = {
                'temp': 20,
                'description': 'clear sky',
                'icon': '01d',
                'humidity': 50,
                'wind_speed': 3.5,
                'feels_like': 19
            }
        
        # Get local time
        now = datetime.now()
        hour = now.hour
        greeting_text, greeting_emoji = get_greeting(hour)
        
        return jsonify({
            'success': True,
            'city': city,
            'country': country,
            'weather': weather,
            'greeting': f"{greeting_text}, {city}! {greeting_emoji}",
            'hour': hour
        })
    except Exception as e:
        print(f"Init error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/detect-location', methods=['GET'])
def detect_location():
    """Detect user location by IP"""
    location = get_user_location_by_ip()
    return jsonify(location or {})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get context from session
        context = {
            'city': session.get('city', 'Unknown'),
            'country': session.get('country', 'Unknown'),
            'weather': get_weather(session.get('city', 'London'))
        }
        
        # Get AI response
        response = get_ai_response(message, context)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'response': "I'm here to help! What would you like to know? 😊",
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/weather/<city>', methods=['GET'])
def weather(city):
    """Get weather for a city"""
    weather_data = get_weather(city)
    return jsonify(weather_data or {'error': 'Could not fetch weather'})


def run_speed_test(result_container):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        result_container['data'] = {
            'download_speed': round(download_speed, 2),
            'upload_speed': round(upload_speed, 2),
            'unit': 'Mbps'
        }
    except Exception as e:
        result_container['error'] = str(e)

@app.route('/api/speed-test', methods=['GET'])
def speed_test():
    result = {}
    thread = threading.Thread(target=run_speed_test, args=(result,))
    thread.start()
    thread.join(timeout=20)

    if 'data' in result:
        return jsonify(result['data'])
    elif 'error' in result:
        return jsonify({'error': result['error']}), 500
    else:
        return jsonify({'message': 'Speed test taking too long, please try again'}), 202



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)