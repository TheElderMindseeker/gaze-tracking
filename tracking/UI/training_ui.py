import cv2
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QThread, QEventLoop, QPoint, QPointF

from PyQt5.QtGui import QPixmap, QPen, QRadialGradient, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush

import numpy as np


from gaze_tracking import GazeTracking
training_points = [(447, 63), (107, 63), (200, 650)]
user_input = []


# class App(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.setGeometry(300, 300, 350, 100)
#         self.setWindowTitle('Colours')
#
#         i = 0
#         while len(user_input) < len(training_points):
#             img = np.zeros((512,512,3), np.uint8)
#             cv2.circle(img, training_points[i], 63, (0, 0, 255), -1)
#             user_input.append(5)
#             self.showFullScreen()
#

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                #p = convertToQtFormat
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle("Video")

        # self.setGeometry(300, 300, 350, 100)
        self.resize(self.width(), self.height())
        # create a label
        self.label = QLabel(self)
        self.label.move(0, 0)
        self.label.resize(self.width(), self.height())
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
