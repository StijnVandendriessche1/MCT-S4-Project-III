import cv2
import time
import numpy as np

# Create an object. Zeor for externa camera

video = cv2.VideoCapture(0)
a = 0
while True:
    a += 1
    # Create a freame object and
    check, frame = video.read()

    print(check)
    print(frame)

    # Converting to grayscale
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret,frame = cv2.threshold(frame,80,255,cv2.THRESH_BINARY)

    # Show the frame
    cv2.imshow("Capturing", gray)

    # For press any key to out (miliseconds)
    # cv2.waitKey(0)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break
print(a)
# Shutdown the camera
video.release()
cv2.destroyAllWindows()
