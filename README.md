
# Security Breach Detection System using AI (YOLOV4 + dlib)

Repository containing multiple Python scripts meant to prove that AI can be used in protecting and saving lives as per my research paper for the MIICA 2023 Malaysian science contest.

Dependencies:
- requests
- pyqt5 5.15.7
- opencv-python-headless
- numpy
- face_recognition

The YOLOv4 model is a state-of-the-art object detection model that is fast and accurate. It is trained on the COCO (Common Objects in Context) dataset and can detect a wide range of objects, including people, vehicles, and animals.

The dlib library is used for face recognition. It includes a pre-trained face recognition model that can identify faces in images and video.

To get started with this repository, you will need to install the required dependencies, by running the command below. You will also need to download the YOLOv4 weights file, or just use your own.

Create Local Environment & Install Dependencies:

```bash
  pipenv install --python 3.8
  pipenv shell
  pipenv install requests numpy pyqt5 opencv-python-headless face_recognition
```

Next, drop your .weights file in the ./yolov4Weights directory, a picture of a person in the ./faceRecognition directory, and make sure you initialize your camera with the correct index.

Then just run main.py as usual:

```bash
  python3 main.py
```

You may also run demo versions of each script, just for face recognition or object detection.

Once you have everything set up, you can use the provided scripts to detect objects in images or video, or to do face recognition. You can also use the code as a starting point for your own projects.

The script is also capable of sending message via the Telegram Bot API. Just replace the chat_ID and TOKEN in the ./telegramAlerts/sendMessage.py script.