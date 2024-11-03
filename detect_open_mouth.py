# Import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
from ChocolateDetector import get_target, has_target
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

def put_in_mouth(frame):
    tgt = get_target(frame)
    center = center_mouth(mouth)
    
    buffer = 10
    
    while has_target(frame):
        while tgt[0] < (center[0] - buffer):
            print("Move Right")
        while tgt[0] > (center[0] + buffer):
            print("Move Left")

        while tgt[1] < (center[1] - buffer):
            print("Move Down")
        while tgt[1] > (center[1] + buffer):
            print("Move Up")
        

def center_mouth(mouth):
    vert_center = (mouth[2][1] + mouth[10][1]) / 2
    horiz_center = (mouth[0][0] + mouth[6][0]) / 2
    
    return (horiz_center, vert_center)
def mouth_aspect_ratio(mouth):
    # Compute the Euclidean distances between the two sets of
    # vertical mouth landmarks (x, y)-coordinates
    A = dist.euclidean(mouth[2], mouth[10])  # 51, 59
    B = dist.euclidean(mouth[4], mouth[8])   # 53, 57

    # Compute the Euclidean distance between the horizontal
    # mouth landmark (x, y)-coordinates
    C = dist.euclidean(mouth[0], mouth[6])   # 49, 55

    # Compute the mouth aspect ratio
    mar = (A + B) / (2.0 * C)

    # Return the mouth aspect ratio
    return mar

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=False, default='shape_predictor_68_face_landmarks.dat',
    help="Path to facial landmark predictor")
ap.add_argument("-w", "--webcam", type=int, default=0,
    help="Index of webcam on system")
args = vars(ap.parse_args())

# Define a constant for the mouth aspect ratio to indicate open mouth
MOUTH_AR_THRESH = 0.79

# Initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

# Grab the indexes of the facial landmarks for the mouth
(mStart, mEnd) = (49, 68)

# Start the video stream thread
print("[INFO] Starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

# Adjust frame dimensions for the rotated frame
frame_width = 360  # Width becomes the original height after rotation
frame_height = 640  # Height becomes the original width after rotation

# Define the codec and create VideoWriter object. The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))
time.sleep(1.0)

# Loop over frames from the video stream
while True:
    # Grab the frame from the threaded video file stream
    frame = vs.read()
    
    # Rotate the frame by 90 degrees clockwise
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # Resize the frame if needed
    frame = imutils.resize(frame, width=frame_width)
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    rects = detector(gray, 0)

    # Loop over the face detections
    for rect in rects:
        # Determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # Extract the mouth coordinates, then use the
        # coordinates to compute the mouth aspect ratio
        mouth = shape[mStart:mEnd]

        mouthMAR = mouth_aspect_ratio(mouth)
        mar = mouthMAR

        # Compute the convex hull for the mouth, then
        # visualize the mouth
        mouthHull = cv2.convexHull(mouth)
        
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
        cv2.putText(frame, "MAR: {:.2f}".format(mar), (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Draw text if mouth is open
        if mar > MOUTH_AR_THRESH:
            cv2.putText(frame, "Mouth is Open!", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Write the frame into the file 'outpy.avi'
    out.write(frame)

    # Show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# Do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()