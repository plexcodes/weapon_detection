from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
from datetime import datetime
from telegramAlerts.sendMessage import sendAlert, sendFrame
import face_recognition

# ~ handles the YOLOv4 detection algorythm,
# ~ sends alerts via Telegram API
# ~ saves frames with 'intruders' & weapons in sight in directory ./savedFrames

class Detection(QThread):
    def __init__(self):
        super(Detection, self).__init__()
    changePixmap = pyqtSignal(QImage)

    # Runs the detection model, evaluates detections and draws boxes around detected objects
    def run(self):

        # Loads YoloV4 configuration & weight files
        net = cv2.dnn.readNet("./yolov4Weights/yolov4.weights", "cfgFiles/yolov4-obj.cfg")
        classes = []

        # Loads object names
        with open("./cfgFiles/obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        detected_weapon = ""
        spotted_individual = "Unknown | Possibly Masked"

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time() - 11
        self.running = True

        # Initialize camera
        cap = cv2.VideoCapture(0)

        # Loads a sample picture and learns how to recognize it.
        person_image = face_recognition.load_image_file("./faceRecognition/npc.jpeg")
        person_face_encoding = face_recognition.face_encodings(person_image)[0]

        # Create arrays of known face encodings and their names
        known_face_encodings = [
            person_face_encoding,
        ]
        known_face_names = [
            "student_001"
        ]

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # Detection while loop
        while self.running:
            spotted_individual = "Unknown | Possibly Masked"

            ret, frame = cap.read()

            if ret:
                height, width, channels = frame.shape

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = frame[:, :, ::-1]

                # Search for all the faces and face encodings in the current frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        spotted_individual = known_face_names[best_match_index]
                    else:
                        elapsed_time = starting_time - time.time()
                        # Take a screenshot every 10 seconds when an unknown individual is in range
                        if elapsed_time <= -10:
                            starting_time = time.time()
                            # self.intruderFrame(frame)
                            face_names.append(name)
                # Running the detection model

                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)

                # Evaluating detections

                class_ids = []
                confidences = []
                boxes = []

                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        # Confidence Threshold (0.99 = 99%)

                        if confidence > 0.5:
                            print("Weapon ID in Sight: " + str(class_id) + " | Confidence: " + str(int(confidence * 100)) + "%")
                            # Calculating coordinates
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)

                            # Rectangle coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)

                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

                # Draw boxes around detected objects

                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = confidences[i]
                        color = (255, 0, 255)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)
                        print(label)
                        detected_weapon = label

                        elapsed_time = starting_time - time.time()

                        # Take a screenshot and send an alert on Telegram every 2 seconds when an object is in range.
                        if elapsed_time <= -2:
                            starting_time = time.time()
                            # self.weaponFrame(frame, detected_weapon, spotted_individual)

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (34, 139, 34), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (34, 139, 34), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Apply settings
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bytesPerLine = channels * width
                convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)



    # Saves detected frame as a .jpg within the "savedFrames" folder
    def weaponFrame(self, frame, spottedWeapon, individual_id):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        frame_address = "savedFrames/spotted-weapon-" + current_time + ".jpg"
        cv2.imwrite(frame_address, frame)
        print('Frame Saved, Sending Message')

        sendAlert("WARNING! Weapon Detected at " + current_time)
        sendAlert("Spotted Weapon Type: '" + spottedWeapon + "'")
        sendAlert("Camera Location: Hallway 1")
        sendAlert("Armed Individual: " + individual_id)
        sendAlert("SEE IMAGE BELOW, PROCEED WITH EXTREME CAUTION!")
        sendFrame(frame_address)

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
