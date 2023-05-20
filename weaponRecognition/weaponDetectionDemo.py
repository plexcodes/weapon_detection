# from PyQt5.QtCore import QThread, Qt, pyqtSignal
# from PyQt5.QtGui import QImage
# import cv2
# import numpy as np
# import time
# from datetime import datetime
# from telegramAlerts.sendMessage import sendAlert, sendFrame
# #To run this demo, replace the import from ./uiLibrary/detectionWindow.py with this .py file.
#
# # Handles the YOLOv4 detection algorithm & saves detected savedFrames
# class Detection(QThread):
#     def __init__(self):
#         super(Detection, self).__init__()
#
#     changePixmap = pyqtSignal(QImage)
#
#     # Runs the detection model, evaluates detections and draws boxes around detected objects
#     def run(self):
#
#         # Loads YoloV4
#         net = cv2.dnn.readNet("./yolov4Weights/yolov4.weights", "cfgFiles/yolov4-obj.cfg")
#         classes = []
#
#         # Loads object names
#         with open("./cfgFiles/obj.names", "r") as f:
#             classes = [line.strip() for line in f.readlines()]
#
#         layer_names = net.getLayerNames()
#         output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
#         colors = np.random.uniform(0, 255, size=(len(classes), 3))
#         detected_weapon = ""
#
#         font = cv2.FONT_HERSHEY_PLAIN
#         starting_time = time.time() - 11
#
#         self.running = True
#
#         # Initialize camera
#         cap = cv2.VideoCapture(0)
#
#         # Detection while loop
#         while self.running:
#             ret, frame = cap.read()
#             if ret:
#
#                 height, width, channels = frame.shape
#
#                 # Running the detection model
#
#                 blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
#                 net.setInput(blob)
#                 outs = net.forward(output_layers)
#
#                 # Evaluating detections
#
#                 class_ids = []
#                 confidences = []
#                 boxes = []
#
#                 for out in outs:
#                     for detection in out:
#                         scores = detection[5:]
#                         class_id = np.argmax(scores)
#                         confidence = scores[class_id]
#                         # Confidence Threshold (0.99 = 99%)
#
#                         if confidence > 0.05:
#                             print("Weapon ID in Sight: " + str(class_id) + " | Confidence: " + str(int(confidence * 100)) + "%")
#                             # Calculating coordinates
#                             center_x = int(detection[0] * width)
#                             center_y = int(detection[1] * height)
#                             w = int(detection[2] * width)
#                             h = int(detection[3] * height)
#
#                             # Rectangle coordinates
#                             x = int(center_x - w / 2)
#                             y = int(center_y - h / 2)
#
#                             boxes.append([x, y, w, h])
#                             confidences.append(float(confidence))
#                             class_ids.append(class_id)
#
#                 indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)
#
#                 # Draw boxes around detected objects
#
#                 for i in range(len(boxes)):
#                     if i in indexes:
#                         x, y, w, h = boxes[i]
#                         label = str(classes[class_ids[i]])
#                         confidence = confidences[i]
#                         color = (256, 0, 0)
#                         cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
#                         cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)
#                         print(label)
#                         detected_weapon = label
#                         elapsed_time = starting_time - time.time()
#
#                         # Take a screenshot every 10 seconds when an object is in range
#
#                         if elapsed_time <= -2:
#                             starting_time = time.time()
#                             self.saveDetection(frame, detected_weapon)
#
#                 # Apply settings
#
#                 rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 bytesPerLine = channels * width
#                 convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
#                 p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
#                 self.changePixmap.emit(p)
#
#     # Saves detected frame as a .jpg within the "savedFrames" folder
#     def saveDetection(self, frame, spottedWeapon):
#         now = datetime.now()
#         current_time = now.strftime("%H:%M:%S")
#         frame_address = "savedFrames/spotted-weapon-" + current_time + ".jpg"
#         cv2.imwrite(frame_address, frame)
#         print('Frame Saved, Sending Message')
#         sendAlert("WARNING! Weapon Detected at " + current_time)
#         sendAlert("Spotted Weapon Type: '" + spottedWeapon + "'")
#         sendAlert("Camera Location: Hallway 1")
#         sendAlert("SEE IMAGE BELOW, PROCEED WITH EXTREME CAUTION!")
#         sendFrame(frame_address)