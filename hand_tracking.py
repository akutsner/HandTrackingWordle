import cv2
import mediapipe as mp
import time
from buttons import buttons

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
button_cooldown = 0
pressed_list = []


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

"""
def thumbs_up(handLms, h, w):
    lm = []
    for id, l in enumerate(handLms.landmark):
        lm.append((int(l.x * w), int(l.y * h)))
        fingers = {}
        fingers["thumb"] = lm[4][1] < lm[6][1]
"""


#Loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    index_x = index_y = None
    text_color = (0, 0, 0)
    # Draw buttons
    for button in buttons:
        color = button["color_on"] if button["enabled"] else button["color_off"]
        cv2.rectangle(img, (button["x"], button["y"]), (button["x"] + button["w"], button["y"] + button["h"]),
                      color, -1)
        cv2.putText(img, f"{button['label']}", (button["x"] + 10, button["y"] + 40), cv2.FONT_HERSHEY_PLAIN, 2,
                    text_color, 2)
    # Hand landmarks
    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        for id, lm in enumerate(handLms.landmark):
            h, w, c = img.shape
            cx = int(lm.x * w)
            cy = int(lm.y * h)

            if id in [4, 8, 12, 16, 20]:
                cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
            if id in [5, 9, 13, 17]:
                cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
            if id == 8:
                index_x, index_y = cx, cy

            fingers_down = get_fingers_down(handLms, h, w)
            index_only = (
                    fingers_down["index"] == True and
                    fingers_down["middle"] == False and
                    fingers_down["ring"] == False and
                    fingers_down["pinky"] == False

            )

        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)


    # Index out all the rest down for button press


    # Button hover & press logic
    if button_cooldown > 0:
        button_cooldown -= 1


    #pressing buttons
    if index_x is not None and index_only:
        for button in buttons:
            hovering = button["x"] <= index_x <= button["x"] + button["w"] and button["y"] <= index_y <= button["y"] + button["h"]
            if hovering and not button["pressed"] and button_cooldown == 0:
                if button["delete"] == True:
                    if len(pressed_list) > 0:
                        pressed_list.pop()
                        button["pressed"] = True
                        button_cooldown = 15
                elif button["quit"] == True:
                    cap.release()
                    cv2.destroyAllWindows()


                else:
                    if len(pressed_list) < 5:
                        pressed_list.append(button["value"])

                    button["pressed"] = True
                    button_cooldown = 15
            if not hovering:
                button["pressed"] = False
            button["enabled"] = hovering and index_only

    #joins buttons string
    pressed_string = "".join(pressed_list)
    cv2.putText(img, str(pressed_string), (100, 75), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    #fps
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)



    cv2.imshow("Image", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break




cap.release()
cv2.destroyAllWindows()

