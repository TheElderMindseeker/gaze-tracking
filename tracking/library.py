import numpy as np
from tracking.gaze_tracking import GazeTracking

def annotate_frames(frames):
    """
    This function is used to annotate given frames and points of user gaze and fit regression model
    :param frames: List of tuples in format (frame, coordinates)
    :return: parameters of regression
    """
    gaze = GazeTracking()
    ec_ic_r_x = []
    ec_ic_r_y = []
    ec_ic_l_x = []
    ec_ic_l_y = []
    gaze_points = []
    for frame in frames:
        gaze.refresh(frame[0])
        try:
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
        except Exception as e:
            continue
        gaze_points.append((frame[1][0], frame[1][1]))
    r_x, r_y, l_x, l_y = fit_poly(ec_ic_r_x, ec_ic_r_y, ec_ic_l_x, ec_ic_l_y, gaze_points)
    return [r_x, r_y, l_x, l_y]


def fit_poly(ec_ic_r_x, ec_ic_r_y, ec_ic_l_x, ec_ic_l_y, gaze_points):
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

    b_x_screen = np.array([circle[0] for circle in gaze_points], dtype=np.float)
    b_y_screen = np.array([circle[1] for circle in gaze_points], dtype=np.float)
    a_r = np.column_stack([ec_ic_r_x, ec_ic_r_y, x_y_r, x_r_sq, y_r_sq, np.ones(len(ec_ic_r_x))])
    a_l = np.column_stack([ec_ic_l_x, ec_ic_l_y, x_y_l, x_l_sq, y_l_sq, np.ones(len(ec_ic_l_x))])

    out_x_r, _, _, _ = np.linalg.lstsq(a_r, b_x_screen, rcond=None)
    out_y_r, _, _, _ = np.linalg.lstsq(a_r, b_y_screen, rcond=None)
    out_x_l, _, _, _ = np.linalg.lstsq(a_l, b_x_screen, rcond=None)
    out_y_l, _, _, _ = np.linalg.lstsq(a_l, b_y_screen, rcond=None)

    return out_x_r.tolist(), out_y_r.tolist(), out_x_l.tolist(), out_y_l.tolist()


def get_info(frame, parameters):
    r_x, r_y, l_x, l_y = parameters
    gaze = GazeTracking()
    gaze.refresh(frame)
    info = {}
    if gaze.is_blinking():
        info["Blinking"] = True
    elif gaze.is_right():
        info["Looking_right"] = True
    elif gaze.is_left():
        info["Looking_left"] = True
    elif gaze.is_center():
        info["Looking center"] = True
    if gaze.is_top():
        info["Top"] = True
    elif gaze.is_bottom():
        info["Bottom"] = True

    try:
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        left_corner = gaze.eye_left.inner_corner
        right_corner = gaze.eye_right.inner_corner
        iris_l = left_pupil
        iris_r = right_pupil
        corner_l = left_corner
        corner_r = right_corner
    except:
        pass
    #TODO
    r_x = None
    r_y = None
    l_x = None
    l_y = None
    try:
        gaze_point = track_gaze(iris_r, iris_l, corner_r, corner_l, r_x, r_y, l_x, l_y)
    except:
        gaze_point = None

    if gaze_point:
        info["Gaze_x"] = gaze_point[0]
        info["Gaze_y"] = gaze_point[1]
    return info


def track_gaze(iris_r, iris_l, corner_r, corner_l, r_x, r_y, l_x, l_y):
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
        return gaze_point
    except Exception as e:
        print("Eyes are blinking")
