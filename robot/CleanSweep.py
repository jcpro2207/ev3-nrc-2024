import logging

logging.info("Loading modules...")

import evdev # type: ignore
from PS4Keymap import PS4Keymap
# from datetime import datetime
from time import sleep

from ev3dev2.motor import MoveJoystick, LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2 import DeviceNotFound
from ev3dev2.power import PowerSupply
from ev3dev2.sensor import Sensor, INPUT_1, INPUT_4
from ev3dev2.sensor.lego import ColorSensor

from typing import Tuple

from threading import Thread
from data_sender import start_send_loop


logging.info("Modules loaded.")

class CleanSweep:
    '''
    Receives input from a connected PS4 controller and runs the robot. 
    '''

    #region static methods
    @staticmethod
    def scale_range(val: float, src: Tuple[float, float], dst: Tuple[float, float]):
        MIN = src[0]
        MAX = src[1]
        NEW_MIN = dst[0]
        NEW_MAX = dst[1]
        a = (NEW_MAX - NEW_MIN) / (MAX - MIN)
        b = NEW_MAX - (a * MAX)
        return (a * val) + b

    @staticmethod
    def scale_joystick(val: float):
        return CleanSweep.scale_range(
            val,
            (0, 255),
            (-CleanSweep.JOYSTICK_SCALE_RADIUS, CleanSweep.JOYSTICK_SCALE_RADIUS)
        )

    @staticmethod
    def find_ps4_controller():
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        controller = None
        for device in devices:
            if device.name == "Wireless Controller":
                controller = device
                logging.info("PS4 controller found.")
                return controller

        raise ConnectionError(str.format("PS4 controller not found (devices: `{}`).", devices))

    #endregion

    JOYSTICK_SCALE_RADIUS = 100
    JOYSTICK_THRESHOLD = 10
    OPENING_MOTOR_SPEED = 10
    OPENING_MOTOR_ROTATIONS = 1

    # automatic mode
    _MOVEMENT_SPEED_PERCENT_ = 100

    def __init__(self):
        self.controller = CleanSweep.find_ps4_controller()

        self.connect_inputs_and_outputs()

        self.joystick_x = 0.0
        self.joystick_y = 0.0

        self.power = PowerSupply("/sys/class/power_supply/", "lego-ev3-battery", True)

        self.auto_mode = False

        self.connected_to_server = False
        self.closest_detected_obj = []

    def connect_inputs_and_outputs(self):
        t = 5
        while True:
            try:
                self.move_joystick = MoveJoystick(OUTPUT_B, OUTPUT_C)

                self.opening_motor = MediumMotor(OUTPUT_A)
                self.left_motor = LargeMotor(OUTPUT_B)
                self.right_motor = LargeMotor(OUTPUT_C)

                # this break statement will only be reached if the above code executes without error
                break

            except DeviceNotFound as error:
                print()
                logging.error(error)
                logging.info("Initialising again in {} seconds.".format(t))
                sleep(t)

    def start_controller_read_loop(self):
        logging.info("Started PS4 controller read loop.")
        for event in self.controller.read_loop():
            # joystick [do not remove this condition]
            if event.type == 3 and self.auto_mode is False:
                raw_val = event.value
                if event.code == PS4Keymap.AXE_LX.value: # left joystick, X axis
                    self.joystick_x = CleanSweep.scale_joystick(raw_val)
                elif event.code == PS4Keymap.AXE_LY.value: # left joystick, Y axis
                    # "-" in front is to reverse the sign (+/-) of y (the y-axis of the PS4 joystick is reversed - see notes.md)
                    self.joystick_y = -(CleanSweep.scale_joystick(raw_val))

    def start_motors_and_activekeys_loop(self):
        logging.info("Started motors loop.")
        while True:
            # ACTIVE KEYS
            active_keys = self.controller.active_keys()

            if self.auto_mode is True:
                if PS4Keymap.BTN_R2.value in active_keys:
                    self.auto_mode = False
                    logging.info("Automatic mode stopped. The remote control (PS4 controller) is now ENABLED.\n")
                else:
                    self.run_auto_mode()

            if PS4Keymap.BTN_R1.value in active_keys and self.auto_mode is False:
                self.auto_mode = True
                logging.info("Automatic mode started. The remote control (PS4 controller) is now DISABLED.\n")

            # MOTORS
            self.move_joystick.on(
                self.joystick_x if abs(self.joystick_x) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                self.joystick_y if abs(self.joystick_y) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )

            if PS4Keymap.BTN_L1.value in active_keys:
                self.opening_motor.on(CleanSweep.OPENING_MOTOR_SPEED)
            elif PS4Keymap.BTN_L2.value in active_keys:
                self.opening_motor.on(-CleanSweep.OPENING_MOTOR_SPEED)
            else:
                self.opening_motor.stop()

    def run_auto_mode(self, detected_obj_location):
        if detected_obj_location == 0:
            self.move_joystick.on(
                0, # go straight
                CleanSweep._MOVEMENT_SPEED_PERCENT_,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif detected_obj_location == -1:
            self.move_joystick.on(
                -(CleanSweep._MOVEMENT_SPEED_PERCENT_ / 2), # turn left
                CleanSweep._MOVEMENT_SPEED_PERCENT_,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif detected_obj_location == 1:
            self.move_joystick.on(
                CleanSweep._MOVEMENT_SPEED_PERCENT_ / 2, # turn right
                CleanSweep._MOVEMENT_SPEED_PERCENT_,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        else:
            print("???")
