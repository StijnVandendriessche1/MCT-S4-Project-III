# import the necessary packages
import numpy as np
import cv2
from imutils.object_detection import non_max_suppression
import pafy

classifier = cv2.CascadeClassifier('ML\haarcascade_fullbody.xml')

cv2.startWindowThread()

# open webcam video stream
#cap = cv2.VideoCapture(0)
urls = ["oMJyrvHSGqY", "6iuNSa4lJoA"]
url = f'https://youtu.be/{urls[0]}'
vPafy = pafy.new(url)
play = vPafy.getbest(preftype="mp4")

#start the video
cap = cv2.VideoCapture()
cap.open(play.url)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # resizing for faster detection
    frame = cv2.resize(frame, (640, 480))
    # using a greyscale picture, also for faster detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blackwhite = cv2.equalizeHist(gray)

    # detect people in the image
    rects = classifier.detectMultiScale(
        blackwhite, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)
    
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
    print(len(pick))

    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)


    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()

# finally, close the window
cv2.destroyAllWindows()
cv2.waitKey(1)