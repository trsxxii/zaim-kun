import requests
import json

def send_line_notification(message_data, access_token):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {"messages": [{"type": "flex", "altText": "残予算のお知らせ", "contents": message_data}]}
    data = json.dumps(payload)
    print(data)
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
