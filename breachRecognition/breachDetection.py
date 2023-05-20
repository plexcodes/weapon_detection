from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
from datetime import datetime
from telegramAlerts.sendMessage import sendAlert, sendFrame
import face_recognition
import threading

# Calcularea timpului de detectie pentru arme
detection_time = time.time() - 11

class Detection(QThread):
    def __init__(self):
        super(Detection, self).__init__()
    changePixmap = pyqtSignal(QImage)

    def run(self):
        # Initializarea modelului YOLOv4 pentru detectarea obiectelor
        net = cv2.dnn.readNet("./yolov4Weights/yolov4.weights", "cfgFiles/yolov4-obj.cfg")
        classes = []

        with open("./cfgFiles/obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        # Calcularea timpului de detectie pentru recunoastere faciala
        starting_time = time.time() - 11
        self.running = True

        # Initializarea camerei
        cap = cv2.VideoCapture(0)

        # Definirea listei de imagini cu persoane cunoscute pentru recunoastere faciala
        person_image = face_recognition.load_image_file("./faceRecognition/npc.jpeg")
        person_face_encoding = face_recognition.face_encodings(person_image)[0]

        known_face_encodings = [person_face_encoding]
        known_face_names = ["wanted_001"]

        face_locations = []
        face_names = []

        # Functia de detectare a armelor
        def detection_model(frame):
            global detection_time
            # Preprocesarea și detectarea obiectelor utilizând modelul YOLOv4
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    # Daca sistemul este destul de sigur peste o anumita marja ca obiectul de pe camera este o arma
                    # acesta demareaza procesul de alertare

                    if confidence > 0.95:
                        print("Weapon ID in Sight: " + str(class_id) + " | Confidence: " + str(int(confidence * 100)))
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

            # Procesarea vizuala a cadrelor

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    color = (255, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20),
                                cv2.FONT_HERSHEY_DUPLEX, 3, color, 3)
                    elapsed_time = detection_time - time.time()
                    # Daca arma este detectata pentru mai mult de 2 secunde, sistemul trimite o alerta
                    if elapsed_time <= -2:
                        detection_time = time.time()
                        self.weaponFrame(frame, label, "spotted_individual")

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (34, 139, 34), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (34, 139, 34), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Functia de recunoastere faciala
        def face_recognition_model(frame):
            rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    spotted_individual = known_face_names[best_match_index]
                else:
                    elapsed_time = starting_time - time.time()
                    if elapsed_time <= -10:
                        starting_time = time.time()
                        self.intruderFrame(frame)
                        face_names.append(name)

        while self.running:
            ret, frame = cap.read()

            if ret:
                # Initializarea thread-urilor
                t1 = threading.Thread(target=detection_model, args=(frame,))
                t1.start()

                height, width, channels = frame.shape

                t2 = threading.Thread(target=face_recognition_model, args=(frame,))
                t2.start()

                t1.join()
                t2.join()

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bytesPerLine = channels * width
                convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

    # Functia de trimitere a alertelor prin Telegram API pentru arme
    def weaponFrame(self, frame, spotted_weapon, individual_id):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        frame_address = "savedFrames/spotted-weapon-" + current_time + ".jpg"
        cv2.imwrite(frame_address, frame)
        print('Frame Saved, Sending Message')

        sendAlert("WARNING! Weapon Detected at " + current_time)
        sendAlert("Spotted Weapon Type: '" + spotted_weapon + "'")
        sendAlert("Camera Location: Hallway 1")
        sendAlert("Armed Individual: " + individual_id)
        sendAlert("SEE IMAGE BELOW, PROCEED WITH EXTREME CAUTION!")
        sendFrame(frame_address)

    # Functia de alertare prin Telegram API pentru persoane recunoscute
    def intruderFrame(self, frame):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        frame_address = "savedFrames/intruder-" + current_time + ".jpg"
        cv2.imwrite(frame_address, frame)
        print('Frame Saved, Sending Message')

        sendAlert("Unknown Individual Spotted at: " + current_time)
        sendAlert("Camera Location: Hallway 1")
        sendAlert("See Image Below:")
        sendFrame(frame_address)