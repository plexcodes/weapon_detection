from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time

# Handles the YOLOv4 detection algorithm & saves detected frames
class Detection(QThread):
    def __init__(self):
        super(Detection, self).__init__()

    changePixmap = pyqtSignal(QImage)

    # Runs the detection model, evaluates detections and draws boxes around detected objects
    def run(self):

        # Loads YoloV4
        net = cv2.dnn.readNet("weights/yolov4.weights", "cfg/yolov4.cfg")
        classes = []

        # Loads object names
        with open("obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time() - 11

        self.running = True

        # Initialize camera
        cap = cv2.VideoCapture(0)

        # Detection while loop
        while self.running:
            ret, frame = cap.read()
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
                        print(scores[class_id])

                        # Confidence Threshold (0.99 = 99%)

                        if confidence > 0.05:
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
                        color = (256, 0, 0)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)

                        elapsed_time = starting_time - time.time()

                        # Take a screenshot every 10 seconds when an object is in range

                        if elapsed_time <= -10:
                            starting_time = time.time()
                            self.saveDetection(frame)

                # Apply settings

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bytesPerLine = channels * width
                convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

    # Saves detected frame as a .jpg within the "frames" folder
    def saveDetection(self, frame):
        cv2.imwrite("frames/frame.jpg", frame)
        print('Frame Saved')