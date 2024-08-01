#!/usr/bin/env python3
import logging
from threading import Thread    
from ev3dev2.led import Leds

logging.basicConfig(format="\x1b[32m[%(asctime)s] \x1b[33m{%(levelname)s} \x1b[34m%(message)s\x1b[0m", datefmt="%H:%M:%S", level=logging.DEBUG)

logging.info("ev3.py running.")

LEDs = Leds()

LEDs.set_color("LEFT", "RED")
LEDs.set_color("RIGHT", "RED")

logging.info("Initialising CleanSweep...")

from CleanSweep import CleanSweep


LEDs.set_color("LEFT", "AMBER")
LEDs.set_color("RIGHT", "AMBER")

robot = CleanSweep()

controller_read_loop_thread = Thread(target = robot.start_controller_read_loop)
controller_read_loop_thread.start()


motors_loop_thread = Thread(target = robot.start_motors_and_activekeys_loop)
motors_loop_thread.start()

def start_receive_loop():
    from json import loads
    import socket
    # JC's laptop address: D8:12:65:88:74:74
    BLUETOOTH_ADDRESS = "60:f2:62:a9:d8:cc"
    CHANNEL = 5

    # create a socket object with Bluetooth, TCP & RFCOMM
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
        try:
            s.connect((BLUETOOTH_ADDRESS, CHANNEL))
        except ConnectionError as error:
            logging.error("Failed to connect:", error)
            return

        logging.info(str.format("Successfully connected to server (bluetooth device {}, channel {}).", BLUETOOTH_ADDRESS, CHANNEL))
        # robot.connected_to_server = True

        try:
            logging.info("Started Bluetooth socket receive loop.")
            while True:
                # recv even if auto mode is not True so that raw_data doesn't build up into [][][][]
                raw_data = s.recv(1024)
                if (robot.auto_mode != True):
                    continue

                if not raw_data:
                    logging.info("{{Bluetooth socket}} Disconnected from {}.".format(BLUETOOTH_ADDRESS))
                    break

                data_str = raw_data.decode()
                logging.debug(str.format("Data received: {}", data_str))
                
                data_json = loads(data_str)

                closest_obj = []
                # find min distance
                min_val = max(obj[1] for obj in data_json)
                # get the object that has the min distance
                for obj in data_json:
                    if obj[1] == min_val:
                        closest_obj = obj

                robot.closest_detected_obj = closest_obj


        except ConnectionError as error:
            logging.error("Connection error (robot most likely disconnected from server):", error)
            robot.connected_to_server = False

# COMMENT THESE TWO LINES TO STOP PUBLISHING MESSAGES THROUGH BLUETOOTH SOCKET
# send_loop_thread = Thread(target = start_send_loop, args=[robot])
receive_loop_thread = Thread(target = start_receive_loop)
receive_loop_thread.start()


LEDs.set_color("LEFT", "GREEN")
LEDs.set_color("RIGHT", "GREEN")