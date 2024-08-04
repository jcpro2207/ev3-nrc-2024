import cv2
import numpy as np

# Define the lower and upper bounds for the color red in HSV
LOWER_RED_1 = np.array([0, 150, 150])
UPPER_RED_1 = np.array([10, 255, 255])
LOWER_RED_2 = np.array([170, 150, 150])
UPPER_RED_2 = np.array([180, 255, 255])

# Real-world width of the object (in cm or inches)
REAL_OBJECT_WIDTH = 3

# Focal length of the camera
FOCAL_LENGTH = 500

MIN_CONTOUR_AREA = 500
CENTRE_RANGE = 30

# Function to calculate the centre of a contour
def get_contour_centre(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:  # Avoid division by zero
        return None
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return cX, cY

def detect_colour_and_draw(frame, midpoint_x):
    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for the color red
    mask1 = cv2.inRange(hsv, LOWER_RED_1, UPPER_RED_1)
    mask2 = cv2.inRange(hsv, LOWER_RED_2, UPPER_RED_2)

    # Combine the masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detectedObjects = []

    for contour in contours:
        # skip if the contour is not larger than the minimum area
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
            continue

        # calculate the centre of the contour
        centre = get_contour_centre(contour)

        if centre is None:
            continue

        # Get the bounding box coordinates
        x, y, w, h = cv2.boundingRect(contour)
        # Draw the bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Draw the centre point
        cv2.circle(frame, centre, 5, (0, 0, 255), -1)
        # Annotate the centre point
        cv2.putText(frame, f"Centre: {centre}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Calculate the distance to the object
        perceived_width = w  # Use the width of the bounding box
        distance = (REAL_OBJECT_WIDTH * FOCAL_LENGTH) / perceived_width

        location: int

        location_text = ""
        if abs(centre[0] - midpoint_x) < CENTRE_RANGE:
            location = 0
            location_text = "centre"
        elif centre[0] < midpoint_x:
            location = -1
            location_text = "left"
        else:
            location = 1
            location_text = "right"

        # Annotate the distance & location
        cv2.putText(frame, f"Distance: {distance:.2f} cm [{location_text}]", (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        detectedObjects.append((centre, distance, location))
       

    return (frame, detectedObjects)
    # # Display the frame
    # cv2.imshow("Frame", frame)

    # # Exit on pressing 'q'
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# capt.release()
# cv2.destroyAllWindows()