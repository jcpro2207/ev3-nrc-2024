import typing
from tensorflow.lite.python.interpreter import Interpreter
import cv2
import numpy

BOXES_INDEX, CLASSES_INDEX, SCORES_INDEX = 1, 3, 0
INPUT_MEAN, INPUT_STD = 127.5, 127.5

MIN_CONFIDENCE_THRESHOLD = 0.5

class ObjectDetector:
    def __init__(self, path_to_model: typing.LiteralString, path_to_labels: typing.LiteralString):
        # load model
        interpreter = Interpreter(model_path=path_to_model)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]

        is_floating_model = (input_details[0]["dtype"] == numpy.float32)

        self.interpreter = interpreter
        self.input_details = input_details
        self.output_details = output_details
        self.is_floating_model = is_floating_model
        self.width = width
        self.height = height

        # load labels
        with open(path_to_labels, "r") as file:
            self.labels = [line.strip() for line in file.readlines()]

    def detect_object_from_img(self, image: cv2.typing.MatLike):
        # resize image
        img = image.copy()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (self.width, self.height))
        input_data = numpy.expand_dims(img_resized, axis=0)

        if self.is_floating_model:
            input_data = (numpy.float32(input_data) - INPUT_MEAN) / INPUT_STD

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # DETECTION RESULTS
        # bounding box coordinates of detected objects
        boxes = self.interpreter.get_tensor(self.output_details[BOXES_INDEX]['index'])[0]
        # class index of detected objects
        classes = self.interpreter.get_tensor(self.output_details[CLASSES_INDEX]['index'])[0]
        # confidence of detected objects
        scores = self.interpreter.get_tensor(self.output_details[SCORES_INDEX]['index'])[0]

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > MIN_CONFIDENCE_THRESHOLD) and (scores[i] <= 1.0)):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                y_min = int(max(1, (boxes[i][0] * self.height)))
                x_min = int(max(1, (boxes[i][1] * self.width)))
                y_max = int(min(self.height, (boxes[i][2] * self.height)))
                x_max = int(min(self.width, (boxes[i][3] * self.width)))

                cv2.rectangle(img, (x_min,y_min), (x_max,y_max), (10, 255, 0), 2)

                # DRAW LABEL
                # Look up object name from "labels" array using class index
                object_name = self.labels[int(classes[i])]
                label = f'{object_name}: {int(scores[i]*100)}%' # Example: 'person: 72%'
                # Get font size
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                # Make sure not to draw label too close to top of window
                label_ymin = max(y_min, labelSize[1] + 10)
                # Draw white box to put label text in
                cv2.rectangle(img, (x_min, label_ymin-labelSize[1]-10), (x_min+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
                # Draw label text
                cv2.putText(img, label, (x_min, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        return img