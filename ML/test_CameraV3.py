import cv2
import numpy as np

# Create our body classifier
classifier = cv2.CascadeClassifier('ML\haarcascade_fullbody.xml')
#body_classifier = cv2.CascadeClassifier('ML\haarcascade_fullbody.xml')

# Initiate video capture for video file, here we are using the video file in which pedestrians would be detected
cap = cv2.VideoCapture(0)

while (True):
    # read frame-by-frame
    ret, frame = cap.read()
 
    # set the frame to gray as we do not need color, save up the resources
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    # pass the frame to the classifier
    persons_detected = classifier.detectMultiScale(gray_frame, 1.3, 5)
 
    # check if people were detected on the frame
    try:
        human_count = persons_detected.shape[0]
    except:
        human_count = 0
        # extract boxes so we can visualize things better
        # for actual deployment with hardware, not needed
        for (x, y, w, h) in persons_detected:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
    cv2.imshow('Video footage', frame)
    

""" cap.release()
cv2.destroyAllWindows() """