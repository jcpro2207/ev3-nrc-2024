# note: TPU to speed up?

import cv2
from tensorflow.lite.python.interpreter import Interpreter
import numpy as np

VIDEO_CAPTURE_DEVICE_INDEX = 2

# path to .tflite file
PATH_TO_MODEL = "./test_model/detect.tflite"
PATH_TO_LABELS = "./test_model/labelmap.txt"

IMG_HEIGHT = 320
IMG_WIDTH = 320

MIN_CONFIDENCE_THRESHOLD = 0.5

boxes_index, classes_index, scores_index = 1, 3, 0

input_mean, input_std = 127.5, 127.5

# load the label map
with open(PATH_TO_LABELS, 'r') as file:
    labels = [line.strip() for line in file.readlines()]

interpreter = Interpreter(model_path=PATH_TO_MODEL)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

# initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()

capture = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX)

def run_AI_and_get_frame():
    global frame_rate_calc
    t1 = cv2.getTickCount()

    # capture the video frame by frame
    _retval, raw_frame = capture.read()

    # resize frame
    frame = raw_frame.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # DETECTION RESULTS
    # Bounding box coordinates of detected objects
    boxes = interpreter.get_tensor(output_details[boxes_index]['index'])[0]
    # Class index of detected objects
    classes = interpreter.get_tensor(output_details[classes_index]['index'])[0]
    # Confidence of detected objects
    scores = interpreter.get_tensor(output_details[scores_index]['index'])[0]

    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > MIN_CONFIDENCE_THRESHOLD) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            y_min = int(max(1, (boxes[i][0] * IMG_HEIGHT)))
            x_min = int(max(1, (boxes[i][1] * IMG_WIDTH)))
            y_max = int(min(IMG_HEIGHT, (boxes[i][2] * IMG_HEIGHT)))
            x_max = int(min(IMG_WIDTH, (boxes[i][3] * IMG_WIDTH)))

            cv2.rectangle(frame, (x_min,y_min), (x_max,y_max), (10, 255, 0), 2)

            # DRAW LABEL
            # Look up object name from "labels" array using class index
            object_name = labels[int(classes[i])]
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            # Get font size
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            # Make sure not to draw label too close to top of window
            label_ymin = max(y_min, labelSize[1] + 10)
            # Draw white box to put label text in
            cv2.rectangle(frame, (x_min, label_ymin-labelSize[1]-10), (x_min+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
            # Draw label text
            cv2.putText(frame, label, (x_min, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Draw framerate in corner of frame
    cv2.putText(frame, 'FPS: {0:.2f}'.format(frame_rate_calc), (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    return frame