import requests
import json

def send_line_notification(messages, access_token):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {"messages": [{"type": "text", "text": message} for message in messages]}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
