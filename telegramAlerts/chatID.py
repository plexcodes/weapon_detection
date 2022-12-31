# Get your telegram chat ID for message alerts
import requests

#SENSITIVE INFORMATION
TOKEN = ""

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
print(requests.get(url).json())