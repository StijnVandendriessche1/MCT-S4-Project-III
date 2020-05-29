""" Class for detecting objects with AI """
from threading import Thread
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2

import pafy

import logging
from time import sleep


class MLObjectDetection:
    def __init__(self, objects = ["person"]):
        try:
            self.show = True
            self.count_total_objects = {}
            self.get_objects_detect(objects)
            self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
                            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
            self.start()
            self.start_threads()
        except Exception as ex:
            logging.error(ex)

    def get_objects_detect(self, objects):
        for o in objects:
            self.count_total_objects[o] = 0
    
    def start_threads(self):
        """ Thread for counting the objects """
        counter_objects = Thread(target=self.count_objects)
        counter_objects.start()

        """ Thread for processing the data """
        process_counter = Thread(target=self.process)
        process_counter.start()

    def start(self):
        try:
            self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
            self.net = cv2.dnn.readNetFromCaffe(
                "ML\MobileNetSSD_deploy.prototxt.txt", "ML\MobileNetSSD_deploy.caffemodel")
            self.cap = cv2.VideoCapture(0)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def count_objects(self):
        try:
            while True:
                try:
                    ret, frame = self.cap.read()
                    frame = imutils.resize(frame, width=400)
                    # Convert img to blob
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(
                        frame, (300, 300)), 0.007843, (300, 300), 127.5)
                    # pass the blob through the network and obtain the detections and
                    # predictions
                    self.net.setInput(blob)
                    detections = self.net.forward()
                    """ Make a list for counting the objects """
                    count_objects = {}
                    for o in self.count_total_objects:
                        count_objects[o] = 0
                    # loop over the detections
                    for i in np.arange(0, detections.shape[2]):
                        # extract the confidence (i.e., probability) associated with
                        # the prediction
                        confidence = detections[0, 0, i, 2]
                        # filter out weak detections by ensuring the `confidence` is
                        # greater than the minimum confidence
                        if confidence > 0.31:
                            # extract the index of the class label from the
                            # `detections`, then compute the (x, y)-coordinates of
                            # the bounding box for the object
                            idx = int(detections[0, 0, i, 1])
                            if self.CLASSES[idx] in count_objects:
                                count_objects[self.CLASSES[idx]] += 1
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")
                            # draw the prediction on the frame
                            label = "{}: {:.2f}%".format(self.CLASSES[idx], confidence * 100)
                            cv2.rectangle(frame, (startX, startY),
                                        (endX, endY), self.COLORS[idx], 2)
                            y = startY - 15 if startY - 15 > 15 else startY + 15
                            cv2.putText(frame, label, (startX, y),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)
                    """ Get the count of each object """
                    for key, val in count_objects.items():
                        self.count_total_objects[key] = val
                    if self.show:
                        # show the output frame
                        cv2.imshow("Frame", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                except Exception as ex:
                    logging.error(ex)
                    raise ValueError(ex)
            # When everything done, release the capture
            self.cap.release()

            # finally, close the window
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        except Exception as ex:
            logging.error(ex)
            raise ValueError(ex)

    def process(self):
        while True:
            print(self.count_total_objects)
            sleep(3)
test = MLObjectDetection()