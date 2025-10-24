import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

print(f"Testing with key: {OPENAI_API_KEY[:15]}...")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPENAI_API_KEY}'
}

payload = {
    'model': 'gpt-3.5-turbo',
    'messages': [
        {'role': 'user', 'content': 'Say hello in one sentence'}
    ],
    'max_tokens': 50
}

try:
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! OpenAI API is working!")
        message = response.json()['choices'][0]['message']['content']
        print(f"AI said: {message}")
    else:
        print("\n❌ ERROR!")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")