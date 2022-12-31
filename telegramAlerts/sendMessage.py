import requests

#SENSITIVE INFORMATION
TOKEN = ""
chat_id = ""

def sendAlert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    call = requests.get(url).json()

def sendFrame(image_path):
    data = {"chat_id": chat_id, "caption": ""}
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}"
    with open(image_path, "rb") as image_file:
        ret = requests.post(url, data=data, files={"photo": image_file})
    return ret.json()