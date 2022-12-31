# Get your telegram chat ID for message alerts
import requests

#SENSITIVE INFORMATION
TOKEN = "5484992589:AAFtcv10WpMIxBtTQ7sObYWvWZhcZsL6xXg"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
print(requests.get(url).json())