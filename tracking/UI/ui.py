import sys

import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from UI.reader_ui import gaze, webcam


class QtThreadObject(QtCore.QThread):
    sig = QtCore.pyqtSignal()

    def run(self):
        while True:
            _, frame = webcam.read()

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
            cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (147, 58, 31), 1)
            cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (147, 58, 31),
                        1)

            # cv2.imshow("Demo", frame)
            print(text)
            if cv2.waitKey(1) == 27:
                break
            if gaze.is_blinking():
                self.sig.emit()

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.label = QLabel(self)
        self.pixmap = QPixmap('/Users/irina/Documents/POLIMI/1 semester/image.png')
        self.label.setPixmap(self.pixmap)
        self.qtobj = QtThreadObject()
        self.qtobj.sig.connect(self.qtslot)
        self.qtobj.start()

    def qtslot(self):
        self.pixmap = QPixmap('/Users/irina/Documents/POLIMI/1 semester/image2.png')
        print(self.pixmap.width())
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':

    app = QtWidgets.QApplication([])
    window = Window()
    window.setGeometry(1000, 1000, 1000, 1000)
    window.show()
    sys.exit(app.exec_())