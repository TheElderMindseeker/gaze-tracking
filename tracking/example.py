"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
import numpy as np
from gaze_tracking import GazeTracking


def mouse_drawing(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Left click")
        ec_ic_r_x.append(abs(iris_r[0] - corner_r[0]))
        ec_ic_r_y.append(abs(iris_r[1] - corner_r[1]))
        ec_ic_l_x.append(abs(iris_l[0] - corner_l[0]))
        ec_ic_l_y.append(abs(iris_l[1] - corner_l[1]))
        circles.append((x, y))


gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
cv2.namedWindow("Demo")
cv2.resizeWindow("Demo", 960, 960)
cv2.setMouseCallback("Demo", mouse_drawing)
iris_l = None
corner_l = None
iris_r = None
corner_r = None
circles = []
ec_ic_r_x = []
ec_ic_r_y = []
ec_ic_l_x = []
ec_ic_l_y = []
train_finish = False
r_x = []
r_y = []
l_x = []
l_y = []


def track_gaze(iris_r, iris_l, corner_r, corner_l):
    try:
        ecic_r_x = abs(iris_r[0] - corner_r[0])
        ecic_r_y = abs(iris_r[1] - corner_r[1])
        ecic_l_x = abs(iris_l[0] - corner_l[0])
        ecic_l_y = abs(iris_l[1] - corner_l[1])
        gaze_r_x = r_x[0] * ecic_r_x + r_x[1] * ecic_r_y + r_x[2] * ecic_r_x * ecic_r_y \
                   + r_x[3] * (ecic_r_x ** 2) + r_x[4] * (ecic_r_y ** 2) + r_x[5]
        gaze_r_y = r_y[0] * ecic_r_x + r_y[1] * ecic_r_y + r_y[2] * ecic_r_x * ecic_r_y \
                   + r_y[3] * (ecic_r_x ** 2) + r_y[4] * (ecic_r_y ** 2) + r_y[5]
        gaze_l_x = l_x[0] * ecic_l_x + l_x[1] * ecic_l_y + l_x[2] * ecic_l_x * ecic_l_y \
                   + l_x[3] * (ecic_l_x ** 2) + l_x[4] * (ecic_l_y ** 2) + l_x[5]
        gaze_l_y = l_y[0] * ecic_l_x + l_y[1] * ecic_l_y + l_y[2] * ecic_l_x * ecic_l_y \
                   + l_y[3] * (ecic_l_x ** 2) + l_y[4] * (ecic_l_y ** 2) + l_y[5]

        gaze_point = (int((gaze_r_x + gaze_l_x)/2), int((gaze_r_y + gaze_l_y)/2))
        circles.append(gaze_point)
        print(circles)
    except Exception as e:
        print("Eyes are blinking")


def fit_poly():
    x_y_r = []
    for i in range(len(ec_ic_r_x)):
        x_y_r.append(ec_ic_r_x[i] * ec_ic_r_y[i])
    x_r_sq = [x ** 2 for x in ec_ic_r_x]
    y_r_sq = [y ** 2 for y in ec_ic_r_y]

    x_y_l = []
    for i in range(len(ec_ic_l_x)):
        x_y_l.append(ec_ic_l_x[i] * ec_ic_l_y[i])
    x_l_sq = [x ** 2 for x in ec_ic_l_x]
    y_l_sq = [y ** 2 for y in ec_ic_l_y]

    b_x_screen = np.array([circle[0] for circle in circles])
    b_y_screen = np.array([circle[1] for circle in circles])
    a_r = np.column_stack([ec_ic_r_x, ec_ic_r_y, x_y_r, x_r_sq, y_r_sq, np.ones(len(ec_ic_r_x))])
    a_l = np.column_stack([ec_ic_l_x, ec_ic_l_y, x_y_l, x_l_sq, y_l_sq, np.ones(len(ec_ic_l_x))])

    out_x_r, _, _, _ = np.linalg.lstsq(a_r, b_x_screen, rcond=None)
    out_y_r, _, _, _ = np.linalg.lstsq(a_r, b_y_screen, rcond=None)
    out_x_l, _, _, _ = np.linalg.lstsq(a_l, b_x_screen, rcond=None)
    out_y_l, _, _, _ = np.linalg.lstsq(a_l, b_y_screen, rcond=None)

    return out_x_r.tolist(), out_y_r.tolist(), out_x_l.tolist(), out_y_l.tolist()


while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    for center_position in circles:
        cv2.circle(frame, center_position, 5, (0, 0, 255), -1)

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()

    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"
    if gaze.is_top():
        text += " top"
    elif gaze.is_bottom():
        text += " bottom"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    left_corner = gaze.eye_left.inner_corner
    right_corner = gaze.eye_right.inner_corner
    iris_l = left_pupil
    iris_r = right_pupil
    corner_l = left_corner
    corner_r = right_corner

    if train_finish:
        track_gaze(iris_r, iris_l, corner_r, corner_l)

    cv2.circle(frame, left_corner, 3, (225, 0, 0), -1)
    cv2.circle(frame, right_corner, 3, (225, 0, 0), -1)
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break

    if len(circles) >= 15 and not train_finish:
        train_finish = True
        r_x, r_y, l_x, l_y = fit_poly()
        circles = []


def annotate_frames(frames):
    """
    This function is used to annotate given frames and points of user gaze and fit regression model
    :param frames: List of tuples in format (frame, coordinates)
    :return: parameters of regression
    """
    ec_ic_r_x = []
    ec_ic_r_y = []
    ec_ic_l_x = []
    ec_ic_l_y = []
    for frame in frames:
        gaze.refresh(frame)
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        left_corner = gaze.eye_left.inner_corner
        right_corner = gaze.eye_right.inner_corner
        iris_l = left_pupil
        iris_r = right_pupil
        corner_l = left_corner
        corner_r = right_corner
        ec_ic_r_x.append(abs(iris_r[0] - corner_r[0]))
        ec_ic_r_y.append(abs(iris_r[1] - corner_r[1]))
        ec_ic_l_x.append(abs(iris_l[0] - corner_l[0]))
        ec_ic_l_y.append(abs(iris_l[1] - corner_l[1]))
    r_x, r_y, l_x, l_y = fit_poly()
    return




