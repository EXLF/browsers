import requests
import json

api_url = "https://api.deepseek.com/chat/completions"
api_key = "sk-fbfb9414374b462795606ed5b2e1ef2d"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    "stream": False
}

try:
    print("发送请求...")
    print(f"URL: {api_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    
    print("\n收到响应:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"\n错误: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response Status Code: {e.response.status_code}")
        print(f"Response Text: {e.response.text}") 