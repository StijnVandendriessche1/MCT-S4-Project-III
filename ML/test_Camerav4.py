# import the necessary packages
import numpy as np
import cv2
 

classifier = cv2.CascadeClassifier('ML\haarcascade_fullbody.xml')

cv2.startWindowThread()

# open webcam video stream
cap = cv2.VideoCapture(0)

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
    print(rects)
    
    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])

    count_persons = 0
    for (xA, yA, xB, yB) in boxes:
        count_persons += 1
        # display the detected boxes in the colour picture
        cv2.rectangle(frame, (xA, yA), (xB, yB),
                          (0, 255, 0), 2)


    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()

# finally, close the window
cv2.destroyAllWindows()
cv2.waitKey(1)