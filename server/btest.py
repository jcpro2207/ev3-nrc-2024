import logging

logging.basicConfig(format="\x1b[32m[%(asctime)s] \x1b[33m{%(levelname)s} \x1b[34m%(message)s\x1b[0m", datefmt="%H:%M:%S", level=logging.DEBUG)

def start_receive_loop():
    print("send loop started")
    import socket
    # JC's laptop address: D8:12:65:88:74:74
    BLUETOOTH_ADDRESS = "60:f2:62:a9:d8:cc"
    CHANNEL = 5

    # create a socket object with Bluetooth, TCP & RFCOMM
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
        try:
            s.connect((BLUETOOTH_ADDRESS, CHANNEL))
        except ConnectionError as error:
            logging.error("Connection failed:")
            logging.error(error)
            return

        logging.info("Successfully connected to server (bluetooth device {}, channel {}).".format (BLUETOOTH_ADDRESS, CHANNEL))
        # robot.connected_to_server = True

        try:
            logging.info("Started Bluetooth socket receive loop.")
            while True:
                raw_data = s.recv(1024)

                if not raw_data:
                    logging.info("{{Bluetooth socket}} Disconnected from {}.".format(BLUETOOTH_ADDRESS))
                    break

                data_str = raw_data.decode()
                logging.debug(str.format("Data received: {}", data_str))

        except ConnectionError as error:
            logging.error("Connection error (robot most likely disconnected from server):")
            logging.error(error)
            # robot.connected_to_server = False

while True:
    start_receive_loop()