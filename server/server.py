# fix incorrect MIME types in Windows registry
import mimetypes

import numpy.typing
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

import numpy
from flask import Flask, redirect, render_template, url_for
from flask_socketio import SocketIO
import cv2
import base64

from object_detector import ObjectDetector
from concurrent.futures import ThreadPoolExecutor

PORT = 8000
PATH_TO_MODEL = "./object_detection_1/detect.tflite"
PATH_TO_LABELS = "./object_detection_1/labelmap.txt"
VIDEO_CAPTURE_DEVICE_INDEX = 1
SOCKETIO_EVENT_NAME = "data-url"

flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

# region ROUTES
# redirects
@flask_app.route('/interface/')
def r_i():
    return redirect(url_for("interface"))

@flask_app.route('/camera/')
def r_c():
    return redirect(url_for("camera"))


@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    return render_template("interface.html")

@flask_app.route("/camera")
def camera():
    return render_template("camera.html")
# endregion

# region AI
def ndarray_to_b64(ndarray: numpy.typing.NDArray):
    return base64.b64encode(ndarray.tobytes()).decode()

# camera: webcam on server device
executor = ThreadPoolExecutor(max_workers=1)

def AI_loop():
    capture = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX)

    detector = ObjectDetector(PATH_TO_MODEL, PATH_TO_LABELS)

    while True:
        _retval, raw_frame = capture.read()

        processed_frame = detector.detect_object_from_img(raw_frame)

        (retval, jpg_image) = cv2.imencode(".jpg", processed_frame)

        # skip this frame if image encoding was unsuccessful
        if retval is False:
            continue

        socketio_app.emit(SOCKETIO_EVENT_NAME, ndarray_to_b64(jpg_image))

executor.submit(AI_loop)

# camera: client camera at /camera route
'''
detector = ObjectDetector(PATH_TO_MODEL, PATH_TO_LABELS)

@socketio_app.on("client-camera-frame")
def client_camera_frame(imageData):
    bytes = base64.b64decode(imageData)

    np_arr = numpy.frombuffer(bytes, dtype=numpy.uint8)

    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR).copy()

    processed_frame = detector.detect_object_from_img(img)

    (retval, jpg_image) = cv2.imencode(".jpg", processed_frame)

    # skip this frame if image encoding was unsuccessful
    if retval is False:
        return

    current_data_url = ndarray_to_b64(jpg_image)

    socketio_app.emit(SOCKETIO_EVENT_NAME, current_data_url)
'''
# endregion

if __name__ == "__main__":
    socketio_app.run(app=flask_app, port=PORT, use_reloader=False, log_output=True)
