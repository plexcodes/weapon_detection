from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
from datetime import datetime
from telegramAlerts.sendMessage import sendAlert, sendFrame
import face_recognition

# Handles the YOLOv4 detection algorithm & saves detected savedFrames
class Detection(QThread):
    def __init__(self):
        super(Detection, self).__init__()

    changePixmap = pyqtSignal(QImage)

    # Runs the detection model, evaluates detections and draws boxes around detected objects
    def run(self):
        # Loads YoloV4
        net = cv2.dnn.readNet("./yolov4Weights/yolov4.weights", "cfgFiles/yolov4-obj.cfg")
        classes = []

        # Loads object names
        with open("./cfgFiles/obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        detected_weapon = ""

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time() - 11

        spotted_individual = "Unknown | Possibly Masked"

        self.running = True

        # Initialize camera
        cap = cv2.VideoCapture(2)

        # Load a sample picture and learn how to recognize it.
        person_image = face_recognition.load_image_file("./faceRecognition/npc.jpeg")
        person_face_encoding = face_recognition.face_encodings(person_image)[0]

        # Create arrays of known face encodings and their names
        known_face_encodings = [
            person_face_encoding,
        ]
        known_face_names = [
            "student1"
        ]

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # Detection while loop
        while self.running:
            spotted_individual = "Unknown | Possibly Masked"

            ret, frame = cap.read()

            if process_this_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=1.00, fy=1.00)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
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
                            self.intruderFrame(frame)

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 1
                right *= 1
                bottom *= 1
                left *= 1

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (34, 139, 34), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (34, 139, 34), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Weapon Detection starts here.

            if ret:
                height, width, channels = frame.shape

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

                        if confidence > 0.05:
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

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)

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

                        # Take a screenshot every 2 seconds when an object is in range

                        if elapsed_time <= -2:
                            starting_time = time.time()
                            self.weaponFrame(frame, detected_weapon, spotted_individual)

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