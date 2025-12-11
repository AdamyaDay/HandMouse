import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Setup camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Warmup
for _ in range(3):
    s, f = cap.read()
    if s:
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        hands.process(rgb)

screen_w, screen_h = pyautogui.size()

# Variables
prev_x, prev_y = 0, 0
last_left_click = 0
last_right_click = 0
click_cooldown = 0.25
enabled = True
scroll_mode = False
prev_scroll_y = None

dragging = False
last_landmark_time = time.time()

print("Hand Mouse Started")
print("Press 'e' to toggle ON/OFF, 'q' to quit")

while True:
    success, frame = cap.read()
    if not success:
        print("Camera error")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_detected = bool(results.multi_hand_landmarks)

    if hand_detected:
        last_landmark_time = time.time()

        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            # Fingertip landmarks
            index = lm.landmark[8]
            thumb = lm.landmark[4]
            middle = lm.landmark[12]
            ring = lm.landmark[16]

            ix, iy = int(index.x * w), int(index.y * h)
            tx, ty = int(thumb.x * w), int(thumb.y * h)
            mx, my = int(middle.x * w), int(middle.y * h)
            rx, ry = int(ring.x * w), int(ring.y * h)

            # Draw circles
            cv2.circle(frame, (ix, iy), 10, (255, 0, 255), -1)
            cv2.circle(frame, (tx, ty), 10, (0, 255, 255), -1)
            cv2.circle(frame, (mx, my), 10, (255, 255, 0), -1)
            cv2.circle(frame, (rx, ry), 10, (0, 128, 255), -1)

            # Distances
            dist_left = np.hypot(ix - tx, iy - ty)
            dist_right = np.hypot(mx - tx, my - ty)
            dist_scroll = np.hypot(ix - mx, iy - my)
            dist_drag = np.hypot(rx - tx, ry - ty)

            # ========== SCROLL MODE ==========
            if dist_scroll < 20:
                if not scroll_mode:
                    scroll_mode = True
                    prev_scroll_y = iy

                if enabled and prev_scroll_y is not None:
                    dy = iy - prev_scroll_y
                    if abs(dy) > 2:
                        pyautogui.scroll(int(-dy * 2))
                    prev_scroll_y = iy
            else:
                scroll_mode = False
                prev_scroll_y = None

            # ========== CURSOR MOVEMENT ==========
            if enabled and not scroll_mode:
                screen_x = np.interp(ix, (100, w - 100), (0, screen_w))
                screen_y = np.interp(iy, (100, h - 100), (0, screen_h))

                dx = screen_x - prev_x
                dy = screen_y - prev_y

                # Dead zone
                if abs(dx) < 3: dx = 0
                if abs(dy) < 3: dy = 0

                dist = np.hypot(dx, dy)
                if dist < 20:
                    smooth_factor = 8
                elif dist < 60:
                    smooth_factor = 5
                else:
                    smooth_factor = 3

                weight = 1 / smooth_factor
                curr_x = prev_x * (1 - weight) + screen_x * weight
                curr_y = prev_y * (1 - weight) + screen_y * weight

                curr_x = prev_x + np.clip(curr_x - prev_x, -40, 40)
                curr_y = prev_y + np.clip(curr_y - prev_y, -40, 40)

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

            # ========== DRAG MODE (RING + THUMB) ==========
            now = time.time()
            ring_thumb = dist_drag < 30

            # Auto-drop if tracking lost
            if dragging and (time.time() - last_landmark_time) > 0.25:
                pyautogui.mouseUp(_pause=False)
                dragging = False

            # Start drag
            if ring_thumb and not dragging:
                pyautogui.mouseDown(_pause=False)
                dragging = True
                cv2.circle(frame, (rx, ry), 20, (0, 128, 255), -1)

            # End drag
            if dragging and not ring_thumb:
                pyautogui.mouseUp(_pause=False)
                dragging = False

            # ========== LEFT / RIGHT CLICK ==========
            if not dragging:

                if dist_left < 30 and (now - last_left_click) > click_cooldown:
                    pyautogui.click()
                    last_left_click = now
                    cv2.circle(frame, (ix, iy), 15, (0, 255, 0), -1)

                if dist_right < 30 and (now - last_right_click) > click_cooldown:
                    pyautogui.click(button='right')
                    last_right_click = now
                    cv2.circle(frame, (mx, my), 15, (0, 0, 255), -1)

    # ========== HUD ==========
    status = "ENABLED" if enabled else "DISABLED"
    color = (0, 255, 0) if enabled else (0, 0, 255)

    cv2.putText(frame, f"Mouse: {status}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    if scroll_mode:
        cv2.putText(frame, "SCROLL MODE", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    if dragging:
        cv2.putText(frame, "DRAGGING", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 128, 255), 2)

    cv2.putText(frame, "Press 'e' to toggle, 'q' to quit",
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Hand Mouse", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('e'):
        enabled = not enabled
        dragging = False
        scroll_mode = False

cap.release()
cv2.destroyAllWindows()
print("Stopped.")
