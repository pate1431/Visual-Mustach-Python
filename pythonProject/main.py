import cv2
import numpy as np
import dlib

from math import hypot

# Loading Camera and Nose image and Creating mask
#cap = cv2.VideoCapture(0)
#hair = cv2.imread("mou.png")

#test = cv2.imread("ney.jpg")

# dimension = hair.shape
# height = hair.shape[0]
# width = hair.shape[1]
# channel = hair.shape[2]
# print("height", height)
# print("w", width)

# # _, frame = cap.read()
# rows, cols, _ = test.shape
# nose_mask = np.zeros((rows, cols), np.uint8)
# # Loading Face detector
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#video_capture = cv2.VideoCapture(0)


baseCascadePath = "/om patel/local/programs/Python/Python36/Lib/OpenCV/haarcascades/"

# # xml files describing our haar cascade classifiers
# faceCascadeFilePath ="haarcascade_frontalface_default.xml"
# noseCascadeFilePath ="haarcascade_mcs_nose.xml"

# build our cv2 Cascade Classifiers
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
noseCascade = cv2.CascadeClassifier('haarcascade_mcs_nose.xml')

# -----------------------------------------------------------------------------
#       Load and configure mustache (.png with alpha transparency)
# -----------------------------------------------------------------------------

# Load our overlay image: mustache.png
imgMustache = cv2.imread('mou.png', -1)

# Create the mask for the mustache
orig_mask = imgMustache[:, :, 3]

# Create the inverted mask for the mustache
orig_mask_inv = cv2.bitwise_not(orig_mask)

# Convert mustache image to BGR
# and save the original image size (used later when re-sizing the image)
imgMustache = imgMustache[:, :, 0:3]
origMustacheHeight, origMustacheWidth = imgMustache.shape[:2]

# -----------------------------------------------------------------------------
#       Main program loop
# -----------------------------------------------------------------------------

# collect video input from first webcam on system
video_capture = cv2.VideoCapture(0)

while True:
    # Capture video feed
    ret, frame = video_capture.read()

    # Create greyscale image from the video feed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in input video stream
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Iterate over each face found
    for (x, y, w, h) in faces:
        # Un-comment the next line for debug (draw box around all faces)
        # face = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        # Detect a nose within the region bounded by each face (the ROI)
        nose = noseCascade.detectMultiScale(roi_gray)

        for (nx, ny, nw, nh) in nose:
            # Un-comment the next line for debug (draw box around the nose)
            # cv2.rectangle(roi_color,(nx,ny),(nx+nw,ny+nh),(255,0,0),2)

            # The mustache should be three times the width of the nose
            mustacheWidth = 3 * nw
            mustacheHeight = mustacheWidth * origMustacheHeight / origMustacheWidth

            # Center the mustache on the bottom of the nose
            x1 = int(nx - (mustacheWidth / 4))
            x2 = int(nx + nw + (mustacheWidth / 4))
            y1 = int(ny + nh - (mustacheHeight / 2))
            y2 = int(ny + nh + (mustacheHeight / 2))

            # Check for clipping
            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 > w:
                x2 = w
            if y2 > h:
                y2 = h

            # Re-calculate the width and height of the mustache image
            mustacheWidth = int(x2 - x1)
            mustacheHeight = int(y2 - y1)

            # Re-size the original image and the masks to the mustache sizes
            # calcualted above
            mustache = cv2.resize(imgMustache, (mustacheWidth, mustacheHeight), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(orig_mask, (mustacheWidth, mustacheHeight), interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(orig_mask_inv, (mustacheWidth, mustacheHeight), interpolation=cv2.INTER_AREA)

            # take ROI for mustache from background equal to size of mustache image
            roi = roi_color[y1:y2, x1:x2]

            # roi_bg contains the original image only where the mustache is not
            # in the region that is the size of the mustache.
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

            # roi_fg contains the image of the mustache only where the mustache is
            roi_fg = cv2.bitwise_and(mustache, mustache, mask=mask)

            # join the roi_bg and roi_fg
            dst = cv2.add(roi_bg, roi_fg)

            # place the joined image, saved to dst back over the original image
            roi_color[y1:y2, x1:x2] = dst

            break

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # press any key to exit
    # NOTE;  x86 systems may need to remove: " 0xFF == ord('q')"
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    # When everything is done, release the capture
#video_capture.release()
#cv2.destroyAllWindows()