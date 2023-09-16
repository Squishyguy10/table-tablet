import cv2
import numpy as np
from matplotlib import pyplot as plt
import mediapipe as mp

cap = cv2.VideoCapture(1)
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.15, min_tracking_confidence=0.8)
mpDraw = mp.solutions.drawing_utils

cap.set(3, 1920)
cap.set(4, 1080)

tips = [4, 8, 12, 16, 20]

pts = [(0, 0), (0, 0), (0, 0), (0, 0)]
pointIndex = 0

# Calculate destination points to match the input image size
pts2 = np.float32([[0, 0], [1920, 0], [0, 1080], [1920, 1080]])


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global img
    global pointIndex
    global pts

    if event == cv2.EVENT_LBUTTONDOWN:
        print("Mouse Callback!")
        pts[pointIndex] = (x, y)
        pointIndex = pointIndex + 1


def selectFourPoints():
    global img
    global pointIndex

    print("Please select 4 points, by double clicking on each of them in the order: \n\
    top left, top right, bottom left, bottom right.")

    while (pointIndex != 4):
        _, img = cap.read()
        cv2.imshow('Select Corners', img)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False

    return True

cv2.namedWindow('Select Corners')
cv2.setMouseCallback('Select Corners', draw_circle)

while True:
    if (selectFourPoints()):
        cv2.destroyWindow('Select Corners')

        selected_width = abs(pts[1][0] - pts[0][0])  # Calculate the width
        selected_height = abs(pts[2][1] - pts[0][1])  # Calculate the height

        # Calculate destination points to match the selected portion's size
        pts2 = np.float32([[0, 0], [selected_width, 0], [0, selected_height], [selected_width, selected_height]])

        # The four points of the A4 paper in the image
        pts1 = np.float32([ \
            [pts[0][0], pts[0][1]], \
            [pts[1][0], pts[1][1]], \
            [pts[2][0], pts[2][1]], \
            [pts[3][0], pts[3][1]]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        while True:
            success, frame = cap.read()

            image = cv2.warpPerspective(frame, M, (1920, 1080))
            imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(imageRGB)

            # checking whether a hand is detected
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks: # working with each hand
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)

                        if id in tips:
                            cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                    mpDraw.draw_landmarks(image, handLms, mpHands.HAND_CONNECTIONS)

            cv2.imshow('Perspective Transformation', image)
            key = cv2.waitKey(1)

            plt.show()
            if key == 27:
                break

cap.release()
cv2.destroyAllWindows()

