# import the necessary packages
import numpy as np
import cv2
from imutils.object_detection import non_max_suppression
import imutils
import pafy
import argparse



# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cv2.startWindowThread()

# open webcam video stream
#cap = cv2.VideoCapture(0)

urls = ["oMJyrvHSGqY", "6iuNSa4lJoA",
        "fz9eXjzg1ZA", "8HXxSnuXYLM", "rjb9FdVdX5I"]
url = f'https://youtu.be/{urls[2]}'
vPafy = pafy.new(url)
play = vPafy.getbest(preftype="mp4")

# start the video
cap = cv2.VideoCapture()
cap.open(play.url)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image",help="path to the input image")
ap.add_argument("-w", "--win-stride", type=str, default="(4, 4)",
                help="window stride")
ap.add_argument("-p", "--padding", type=str, default="(8, 8)",
                help="object padding")
ap.add_argument("-s", "--scale", type=float, default=0.5,
                help="image pyramid scale")
ap.add_argument("-m", "--mean-shift", type=int, default=-1,
                help="whether or not mean shift grouping should be used")
args = vars(ap.parse_args())

winStride = eval(args["win_stride"])
padding = eval(args["padding"])
meanShift = True if args["mean_shift"] > 0 else False


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # resizing for faster detection
    frame = imutils.resize(frame, width=min(400, frame.shape[1]))

    """ gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blackwhite = cv2.equalizeHist(gray) """

    orig = frame.copy()

    rects, weights = hog.detectMultiScale(
        frame, winStride=winStride, padding=padding, scale=args["scale"], useMeanshiftGrouping=meanShift)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.11)

    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

    print(len(pick))

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()

# finally, close the window
cv2.destroyAllWindows()
cv2.waitKey(1)
