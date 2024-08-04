import logging

logging.basicConfig(format="\x1b[32m[%(asctime)s] \x1b[33m{%(levelname)s} \x1b[34m%(message)s\x1b[0m", datefmt="%H:%M:%S", level=logging.DEBUG)

import numpy.typing
import cv2
import base64

from detect_colour import detect_colour_and_draw

from json import dumps as stringify_json
from time import time_ns

import flask_socketio
import socket

VIDEO_CAPTURE_DEVICE_INDEX = 2
SOCKETIO_EVENT_NAME = "data-url"
SEND_TO_EV3_EVERY = 250 * pow(10, 6) # nanoseconds (ms * 10^6)

def ndarray_to_b64(ndarray: numpy.typing.NDArray):
    return base64.b64encode(ndarray.tobytes()).decode()


def colour_detection_loop(socketio_app: flask_socketio.SocketIO, client_sock: socket.socket):
    capture = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX)

    if not capture.isOpened():
        logging.error("Error: Could not open video stream.")
        return

    # Get the width of the video frame
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    midpoint_x = frame_width // 2 # double / is floor division

    last = 0
    now = 0
    while True:
        now = time_ns()

        retval, raw_frame = capture.read()
        if not retval:
            logging.error("Error: Could not read frame.")
            return

        (processed_frame, detected_objects) = detect_colour_and_draw(raw_frame, midpoint_x)
        print("1", detected_objects)

        (retval, jpg_image) = cv2.imencode(".jpg", processed_frame) 

        if retval is False:
            logging.warning("Warning: Image encoding unsuccessful, skipping frame.")
            continue

        socketio_app.emit(SOCKETIO_EVENT_NAME, {
            "b64ImageData": ndarray_to_b64(jpg_image),
            "detectedObjects": detected_objects
        })

        if (now - last) < SEND_TO_EV3_EVERY:
            continue

        last = now

        # resultStr = "|"
        # for obj in detected_objects:
        #     resultStr += str(obj[0][0]) # centre x
        #     resultStr += ","
        #     resultStr += str(obj[0][1]) # centre y
        #     resultStr += ","
        #     resultStr += str(int(obj[1])) # distance
        #     resultStr += "|"

        # print(resultStr)
        try:
            client_sock.sendall(stringify_json(detected_objects).encode())
            print("2",detected_objects)
        except OSError as e:
            logging.error(f"`OSError` while sending data: {e}")