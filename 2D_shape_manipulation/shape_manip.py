import cv2
import mediapipe as mp
import time


cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0



'''
def get_fingers_down(handLms, h, w):
    lm = []
    for id, l in enumerate(handLms.landmark):
        lm.append((int(l.x * w), int(l.y * h)))

    fingers = {}

    # Other fingers (vertical logic)
    fingers["index"] = lm[8][1] < lm[6][1]
    fingers["middle"] = lm[12][1] < lm[10][1]
    fingers["ring"] = lm[16][1] < lm[14][1]
    fingers["pinky"] = lm[20][1] < lm[18][1]

    return fingers
'''




#Loop
while True:
    success, img = cap.read()


    if not success:
        print("Failed to read from webcam. Check your camera connection.")
        break

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    index_x = index_y = None

    # Hand landmarks
    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]

        h, w, c = img.shape

        for id, lm in enumerate(handLms.landmark):
            cx = int(lm.x * w)
            cy = int(lm.y * h)

            if id in [4, 8, 12, 16, 20]:
                cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

            if id in [5, 9, 13, 17]:
                cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

            if id == 8:
                index_x, index_y = cx, cy

        mpDraw.draw_landmarks(
            img, handLms, mpHands.HAND_CONNECTIONS
        )

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime

    cv2.putText(
        img, str(int(fps)), (10, 70),
        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3
    )

    cv2.imshow("Image", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    # Release the webcam AFTER the loop ends
cap.release()
cv2.destroyAllWindows()
