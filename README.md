# 🤖 AI Personal Assistant Web App

A beautiful, responsive AI chatbot web application with personalized location-based features, weather information, internet speed testing, and local radio streaming.

## ✨ Features

- 🌍 **Location Detection**: Automatically detects user location via IP or manual selection
- 🌤️ **Weather Information**: Real-time weather data with beautiful icons
- 💬 **AI Chat**: Interactive chatbot with natural language understanding
- 🎵 **Radio Player**: Stream local radio stations from your country
- ⚡ **Internet Speed**: Test and display your connection speed
- 🌓 **Dark/Light Mode**: Auto-switches based on time, manual toggle available
- 🎙️ **Voice Input**: Use Web Speech API for voice commands
- 📱 **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- 🧠 **NLP Features**: Intent recognition for contextual responses

## 🏗️ Project Structure

```
ai-assistant/
│
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
│
├── templates/
│   └── index.html         # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css      # Stylesheet
    └── js/
        └── script.js      # Frontend JavaScript
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- API Keys:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [OpenWeatherMap API Key](https://openweathermap.org/api)

### Installation

1. **Clone or create the project structure**

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
Navigate to `http://localhost:5000`

## 🔧 Configuration

### API Keys Setup

#### OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to `.env` file

#### OpenWeatherMap API
1. Go to [OpenWeatherMap](https://openweathermap.org/)
2. Sign up for a free account
3. Navigate to API Keys
4. Copy your API key
5. Add to `.env` file

### Customization

**Change AI Model**: In `app.py`, modify the `model` parameter in the `get_ai_response()` function:
```python
'model': 'gpt-4'  # or 'gpt-3.5-turbo'
```

**Add More Countries**: Update the `countries` dictionary in `script.js`

**Customize Theme Colors**: Modify CSS variables in `style.css`:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
}
```

## 📡 API Endpoints

### Backend Routes

- `GET /` - Main application page
- `POST /api/init` - Initialize user session with location
- `GET /api/detect-location` - Auto-detect user location by IP
- `POST /api/chat` - Send message to AI chatbot
- `GET /api/weather/<city>` - Get weather for specific city
- `GET /api/speed-test` - Test internet speed
- `GET /api/radio/<country>` - Get radio stations for country

## 🌐 External APIs Used

- **OpenAI API** - AI chat responses
- **OpenWeatherMap API** - Weather data
- **WorldTimeAPI** - Time zones and local time
- **ip-api.com** - IP-based geolocation
- **Radio Browser API** - Radio station streaming

## 🎨 Features Breakdown

### 1. Location Setup
- Modal popup on first visit
- Country and city selection
- Saves preferences to localStorage

### 2. Weather Display
- Current temperature
- Weather description
- Humidity and wind speed
- Dynamic weather icons

### 3. AI Chatbot
- Natural language processing
- Context-aware responses
- Intent recognition (jokes, weather queries, etc.)
- Typing indicator animation
- Message history

### 4. Radio Player
- Floating player widget
- Play/pause controls
- Station switching
- Country-specific stations

### 5. Theme System
- Auto dark mode (6 PM - 6 AM)
- Manual toggle
- Smooth transitions
- Persistent user preference

## 🚢 Deployment

### Deploy to Render

1. **Create a Render account** at [render.com](https://render.com)

2. **Create a new Web Service**
   - Connect your GitHub repository
   - Select Python environment
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`

3. **Add environment variables** in Render dashboard:
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - `OPENWEATHER_API_KEY`

4. **Deploy** and get your live URL!

### Deploy to Railway

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **New Project → Deploy from GitHub**

3. **Add environment variables**:
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - `OPENWEATHER_API_KEY`

4. Railway will auto-detect Flask and deploy

### Deploy to Vercel (Serverless)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Create `vercel.json`**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

3. **Deploy**:
```bash
vercel
```

4. **Add environment variables** in Vercel dashboard

### Deploy with Docker

1. **Create `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. **Build and run**:
```bash
docker build -t ai-assistant .
docker run -p 5000:5000 --env-file .env ai-assistant
```

## 🛠️ Development

### Running in Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug mode
python app.py
```

The app will reload automatically when you make changes.

### Testing

```bash
# Test weather API
curl http://localhost:5000/api/weather/London

# Test location detection
curl http://localhost:5000/api/detect-location

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 📱 Mobile Optimization

The app is fully responsive and includes:
- Touch-friendly interface
- Optimized layouts for small screens
- Swipe gestures support
- Mobile-first design principles

## 🔒 Security

- Environment variables for sensitive data
- CORS enabled with restrictions
- Session management with Flask
- Input sanitization
- API key rotation recommended

## 🐛 Troubleshooting

### Common Issues

**Issue**: API keys not working
- **Solution**: Ensure `.env` file is in the root directory and properly formatted

**Issue**: Weather data not loading
- **Solution**: Check your OpenWeatherMap API key is valid and activated

**Issue**: Radio stations not playing
- **Solution**: Some stations may have CORS restrictions; try different stations

**Issue**: Voice input not working
- **Solution**: Voice recognition only works on HTTPS or localhost, and requires Chrome/Edge browser

**Issue**: NLTK data errors
- **Solution**: Run `python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"`

## 🎯 Future Enhancements

- [ ] User authentication and profiles
- [ ] Chat history persistence in database
- [ ] More NLP features (sentiment analysis, entity recognition)
- [ ] Integration with more APIs (news, stocks, etc.)
- [ ] Multilingual support
- [ ] Mobile app version (React Native)
- [ ] Advanced voice commands
- [ ] Custom AI model fine-tuning
- [ ] Analytics dashboard
- [ ] Social sharing features

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review API documentation for external services

## 🙏 Acknowledgments

- OpenAI for GPT API
- OpenWeatherMap for weather data
- Radio Browser for radio streaming
- Bootstrap team for UI components
- Font Awesome for icons

## 📊 Performance Tips

1. **Caching**: Implement Redis for caching API responses
2. **Rate Limiting**: Add rate limiting for API endpoints
3. **CDN**: Use CDN for static assets in production
4. **Compression**: Enable gzip compression
5. **Lazy Loading**: Implement lazy loading for images

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask session secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Yes |
| `FLASK_ENV` | Environment (development/production) | No |
| `PORT` | Server port (default: 5000) | No |

## 💡 Tips

- Keep your API keys secure and never commit them
- Use environment-specific configurations
- Enable HTTPS in production
- Monitor API usage to avoid rate limits
- Regularly update dependencies
- Test on multiple devices and browsers

---

Made with ❤️ and AI

**Happy Coding! 🚀**