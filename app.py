import os
import json
import secrets
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests
from openai import OpenAI
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-key')
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'your-weather-key')

# Initialize OpenAI client only if API key is valid
client = None
if OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-key':
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")


def get_weather(city: str) -> dict | None:
    """Fetch weather data from OpenWeatherMap or return mock data."""
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'your-weather-key':
        return {
            'temp': 20,
            'description': 'clear sky (mock)',
            'icon': '01d',
            'humidity': 50,
            'wind_speed': 3.5,
            'feels_like': 19
        }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'humidity': data['main'].get('humidity'),
                'wind_speed': round(data.get('wind', {}).get('speed', 0), 1),
                'feels_like': round(data['main'].get('feels_like', data['main']['temp']))
            }
        return None
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None


def get_user_location_by_ip() -> dict | None:
    """Get user location by IP address."""
    try:
        resp = requests.get('http://ip-api.com/json/', timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return {
                'city': d.get('city'),
                'country': d.get('country'),
                'timezone': d.get('timezone')
            }
    except Exception as e:
        print(f"IP Location Error: {e}")
    return None


def get_greeting(hour: int) -> tuple[str, str]:
    """Return greeting based on time of day."""
    if 5 <= hour < 12:
        return "Good morning", "🌅"
    if 12 <= hour < 17:
        return "Good afternoon", "☀️"
    if 17 <= hour < 21:
        return "Good evening", "🌆"
    return "Good night", "🌙"


def analyze_intent(message: str) -> str:
    """Simple intent detection for quick responses."""
    msg = (message or '').lower()
    if any(w in msg for w in ['time', 'what time', 'clock']):
        return 'time'
    if any(w in msg for w in ['joke', 'fun', 'funny', 'laugh']):
        return 'joke'
    return 'ai'


BASE_SYSTEM_PROMPT = """You are Sky, a friendly and knowledgeable weather assistant chatbot. Your primary role is to provide accurate and concise weather-related information and advice. You have access to up-to-date information from the OpenWeatherMap tool, which provides current weather and 7-day forecasts for any requested location.

When interacting with users, follow these guidelines:
1. Always be kind, polite, and maintain a relaxed, casual, and cheerful tone.
2. Focus exclusively on weather-related information, including temperature, cloud coverage, precipitation, snowfall, wind speed, and other weather phenomena.
3. Answer all weather-related questions, even those that do not require real-time data. Provide clear and concise explanations for general weather concepts and phenomena.
4. Follow user queries closely and provide only the necessary details. If the user requests specific information, provide that without overwhelming them with additional data.
5. Use natural, human-like language to summarize weather forecasts and conditions. Avoid sounding like a list or a printed report.
6. If a question is outside the scope of weather, kindly decline to answer and remind the user of your specialization in weather-related queries.
7. Make use of markdown formatting to present information in a clear and organized manner.

IMPORTANT: Do NOT provide medical, legal, financial, or any other non-weather-related advice. If a user asks for such advice, politely inform them that you specialize in weather-related queries and suggest they consult the appropriate professionals for their specific needs."""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_for_location",
            "description": "Get current weather for a specified city (used when user asks about another city).",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    }
]


def call_openai_model(messages: list, tools: list | None = None, tool_choice: str | None = None) -> tuple[dict, list | None]:
    """Call OpenAI API with error handling."""
    
    # Check if client is initialized
    if not client:
        return {
            "role": "assistant", 
            "content": "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
        }, None
    
    try:
        print(f"[DEBUG] Calling OpenAI with {len(messages)} messages")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=400,
            temperature=0.7
        )
        
        response_message = completion.choices[0].message
        
        # Convert to dict for consistent access
        response_dict = {
            "role": response_message.role,
            "content": response_message.content
        }
        
        # Handle tool calls if present
        tool_calls = None
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            tool_calls = []
            for tc in response_message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
            response_dict["tool_calls"] = tool_calls
        
        print(f"[DEBUG] OpenAI response: content={'Yes' if response_dict.get('content') else 'No'}, tool_calls={len(tool_calls) if tool_calls else 0}")
        
        return response_dict, tool_calls
    
    except Exception as e:
        print(f"[ERROR] OpenAI API Error: {e}")
        traceback.print_exc()
        
        error_msg = str(e).lower()
        if 'quota' in error_msg or 'insufficient_quota' in error_msg:
            return {"role": "assistant", "content": "⚠️ OpenAI quota exhausted. Please check your API usage."}, None
        if '401' in error_msg or 'unauthorized' in error_msg or 'invalid' in error_msg:
            return {"role": "assistant", "content": "⚠️ Invalid OpenAI API key. Please check your configuration."}, None
        if '429' in error_msg or 'rate_limit' in error_msg:
            return {"role": "assistant", "content": "⚠️ Too many requests. Please try again in a moment."}, None
        
        return {"role": "assistant", "content": f"⚠️ AI service error: {str(e)}"}, None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_user():
    """Initialize user session with location and weather data."""
    try:
        print("[DEBUG] Init user called")
        data = request.json or {}
        loc = get_user_location_by_ip()
        
        city = data.get('city') or (loc or {}).get('city', 'London')
        
        session['city'] = city
        session['country'] = data.get('country') or (loc or {}).get('country')
        session['timezone'] = data.get('timezone') or (loc or {}).get('timezone')
        
        weather = get_weather(city) or {
            'temp': 20, 
            'description': 'clear sky (mock)', 
            'icon': '01d',
            'humidity': 50,
            'wind_speed': 3.5,
            'feels_like': 19
        }

        now = datetime.now()
        hour = now.hour
        greeting_text, greeting_emoji = get_greeting(hour)
        
        # Initialize chat history with system prompt
        session['chat_history'] = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
        
        print(f"[DEBUG] Initialized session for {city}")

        return jsonify({
            'success': True,
            'city': city,
            'country': session.get('country'),
            'weather': weather,
            'greeting': f"{greeting_text}, {city}! {greeting_emoji}",
            'hour': hour
        })
    
    except Exception as e:
        print(f"[ERROR] Init Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI and tool calling."""
    try:
        print("\n[DEBUG] === New Chat Request ===")
        data = request.json or {}
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'response': 'No message provided', 'timestamp': datetime.now().isoformat()}), 400

        print(f"[DEBUG] User message: {message}")

        # Load chat history from session
        chat_history = session.get('chat_history')
        if not chat_history:
            print("[WARNING] No chat history in session, initializing...")
            chat_history = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
        
        print(f"[DEBUG] Current history length: {len(chat_history)}")
        
        # Quick intent checks (avoid AI call for simple queries)
        intent = analyze_intent(message)
        
        if intent == 'time':
            print("[DEBUG] Intent: time")
            return jsonify({
                'response': f"The current time is {datetime.now().strftime('%I:%M %p')} ⏰",
                'timestamp': datetime.now().isoformat()
            })
        
        if intent == 'joke':
            print("[DEBUG] Intent: joke")
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                "What's an AI's favorite snack? Computer chips! 🍟",
                "Why did the AI go to school? To improve its learning algorithm! 📚"
            ]
            return jsonify({
                'response': random.choice(jokes),
                'timestamp': datetime.now().isoformat()
            })

        # Add user message to history
        chat_history.append({"role": "user", "content": message})
        print(f"[DEBUG] Added user message, history length: {len(chat_history)}")

        # Prepare messages for API (last 10 to save tokens)
        messages_to_send = chat_history[-10:]
        print(f"[DEBUG] Sending {len(messages_to_send)} messages to OpenAI")

        # First AI call (may trigger tool use)
        response_message, tool_calls = call_openai_model(
            messages_to_send,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        # Check for API errors
        content = response_message.get('content') or ''
        if content.startswith('⚠️'):
            print(f"[WARNING] API error: {content}")
            return jsonify({
                'response': content,
                'timestamp': datetime.now().isoformat()
            })

        # Handle tool calls if any
        if tool_calls:
            print(f"[DEBUG] Tool calls detected: {len(tool_calls)}")
            chat_history.append(response_message)
            
            for tool_call in tool_calls:
                fname = tool_call.get("function", {}).get("name")
                args_json = tool_call.get("function", {}).get("arguments", "{}")
                tool_call_id = tool_call.get('id')
                
                print(f"[DEBUG] Processing tool call: {fname}, args: {args_json}")

                if fname == "get_weather_for_location":
                    try:
                        args = json.loads(args_json)
                        target_city = args.get("city")
                        print(f"[DEBUG] Fetching weather for: {target_city}")
                        weather_data = get_weather(target_city)

                        if weather_data:
                            weather_data_str = (
                                f"CURRENT WEATHER DATA FOR {target_city}: "
                                f"{weather_data['description']}, {weather_data['temp']}°C, "
                                f"Feels Like: {weather_data['feels_like']}°C, "
                                f"Humidity: {weather_data['humidity']}%, "
                                f"Wind Speed: {weather_data['wind_speed']} m/s."
                            )
                        else:
                            weather_data_str = f"Weather data not available for {target_city}."

                        # Add tool response to history
                        chat_history.append({
                            "role": "tool",
                            "name": fname,
                            "content": weather_data_str,
                            "tool_call_id": tool_call_id
                        })
                        print(f"[DEBUG] Added tool response to history")
                    
                    except Exception as ex:
                        print(f"[ERROR] Tool execution error: {ex}")
                        traceback.print_exc()
                        chat_history.append({
                            "role": "tool",
                            "name": fname,
                            "content": f"Error while fetching weather: {str(ex)}",
                            "tool_call_id": tool_call_id
                        })
            
            # Second AI call with tool results
            print("[DEBUG] Making second OpenAI call with tool results")
            final_message, _ = call_openai_model(chat_history[-10:])
            final_response = (final_message.get("content") or "").strip()
            chat_history.append(final_message)
            print(f"[DEBUG] Final response: {final_response[:100]}...")
        
        else:
            # No tool call - use direct response
            print("[DEBUG] No tool calls, using direct response")
            final_response = (response_message.get("content") or "").strip()
            chat_history.append(response_message)

        # Save updated history to session (keep manageable size)
        MAX_HISTORY = 20
        if len(chat_history) > MAX_HISTORY:
            print(f"[DEBUG] Trimming history from {len(chat_history)} to {MAX_HISTORY}")
            system_prompt = chat_history[0]
            recent_messages = chat_history[-(MAX_HISTORY-1):]
            chat_history = [system_prompt] + recent_messages
        
        session['chat_history'] = chat_history
        print(f"[DEBUG] Saved history to session, length: {len(chat_history)}")

        return jsonify({
            'response': final_response or "I'm not sure how to respond to that.",
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print("[ERROR] === CHAT ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'response': f"⚠️ Server error: {str(e)}. Please check the console logs.",
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/weather/<city>', methods=['GET'])
def api_weather(city):
    """Get weather for a specific city."""
    data = get_weather(city)
    return jsonify(data or {'error': 'Could not fetch weather'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)