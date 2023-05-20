# IDENTIFICAREA AMENINȚĂRILOR IMINENTE FOLOSIND INTELIGENȚA ARTIFICIALĂ

Instructiuni de instalare:

1. Copierea fisierelor local:

```bash
  cd your_dir
  git clone https://github.com/plexcodes/weapon_detection_system.git -b master
```
2. Instalarea dependentelor si crearea unui mediu virtual PipEnv:

```bash
  cd weapon_detection_system
  pipenv install --python 3.8
  pipenv shell
  pipenv install requests numpy pyqt5 opencv-python-headless face_recognition
```

3. Copierea fisierelor YOLOv4 sub numele "yolov4.weights" din link-ul de Google Drive atasat mai jos in folderul /yolov4Weights/.

4. (Optional) Introducerea cheilor API Telegram pentru testarea alertelor in timp real in fisierul /telegramAlerts/sendMessage.py.

5. (Optional) Introducerea imaginilor pentru recunoastere faciala in folderul /faceRecognition/ si inregistrarea lor in scriptul /breachDetection/breachDetection.py

5. Rularea sistemului:

```bash
  python3 main.py
```

Dependente utilizate:
- requests (Pentru API Requests)
- pyqt5 5.15.7 (Pentru Interfata Grafica)
- opencv-python-headless (Pentru Procesarea Cadrelor)
- numpy (Pentru Calcule)
- face_recognition (Pentru Recunoastere Faciala)

Instrumente utilizate:
- Jetbrains PyCharm Professional (Pentru Editare Cod)
- Google Collaboratory (Pentru Antrenarea Modelului AI)
- Google Drive (Pentru Google Collaboratory)
- Github (Versionare Cod)
- Git
- Python 3
- LabelImg (Pentru Etichetarea Imaginilor din Dataset)
- Darknet (Arhitectura Pentru Antrenarea AI)
- YOLOv4 (Algoritm Pentru Detectarea Obiectelor)

Link Notebook Google Collaboratory: https://colab.research.google.com/drive/1PRWqJExSRWzQLW5aaaL3UsafkjuYEoDA?usp=sharing#scrollTo=BZjRqnuOdvXe
Link Dataset: https://drive.google.com/drive/folders/1jDKhHkOc_CzEB-WeFfKqfvXYIdWxiZZk?usp=share_link
Link Fisiere YOLOv4: https://drive.google.com/drive/folders/1bi7aRlD_Pngy-Y2LAtw2_EI_3puLUj-f?usp=share_link

# Security Breach Detection System using AI (YOLOV4 + dlib)

Repository containing multiple Python scripts meant to prove that AI can be used in protecting and saving lives as per my research paper.

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