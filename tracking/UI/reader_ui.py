import threading

import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread, QEventLoop

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *


from gaze_tracking import GazeTracking

# app = QApplication([])
# button = QPushButton('Click')
#
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)


# def on_button_clicked():
#     while True:
#         _, frame = webcam.read()
#
#         # We send this frame to GazeTracking to analyze it
#         gaze.refresh(frame)
#         frame = gaze.annotated_frame()
#         text = ""
#
#         if gaze.is_blinking():
#             text = "Blinking"
#         elif gaze.is_right():
#             text = "Looking right"
#         elif gaze.is_left():
#             text = "Looking left"
#         elif gaze.is_center():
#             text = "Looking center"
#         if gaze.is_top():
#             text += " top"
#         elif gaze.is_bottom():
#             text += " bottom"
#
#         cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
#
#         left_pupil = gaze.pupil_left_coords()
#         right_pupil = gaze.pupil_right_coords()
#         cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
#         cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31),
#                     1)
#
#         cv2.imshow("Demo", frame)
#
#         if cv2.waitKey(1) == 27:
#             break
#
#         #frame = gaze.annotated_frame()
#         if gaze.is_right() and gaze.is_bottom() and not gaze.is_blinking():
#             alert = QMessageBox()
#             alert.setText('You clicked the button!')
#             alert.exec_()


# button.clicked.connect(on_button_clicked)
# button.show()
# app.exec_()
# class TurnedPage(QObject):
#     changed = pyqtSignal()
#
#     def __init__(self):
#         QObject.__init__(self)
#
#     def change(self):
#             self.changed.emit()
class DataCaptureThread(QThread):
    def collectProcessData(self):
        print("Collecting Process Data")

    def __init__(self, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)

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

            cv2.imshow("Demo", frame)

            if cv2.waitKey(1) == 27:
                break

            # frame = gaze.annotated_frame()
            if gaze.is_right() and gaze.is_bottom() and not gaze.is_blinking():
                print('hi')
        # loop = QEventLoop()
        # loop.exec_()

class App(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.photo_list = ['/Users/irina/Documents/POLIMI/1 semester/image.png',
                           '/Users/irina/Documents/POLIMI/1 semester/image2.png',
                           '/Users/irina/Documents/POLIMI/1 semester/image3.png',
                           '/Users/irina/Documents/POLIMI/1 semester/image4.png']
        self.curr_photo = 0
        self.title = 'Eye-Tracked Book Reader'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.label = QLabel(self)
        self.pixmap = None
        self.dataCollectionThread = DataCaptureThread()
        self.dataCollectionThread.start()
        self.initUI()

    def initUI(self):
        previous_button = QPushButton('Previous Page')
        next_button = QPushButton('Next Page')
        # page = TurnedPage()
        # page.changed.connect(self.change_page)

        self.pixmap = QPixmap(self.photo_list[self.curr_photo])
        self.label.setPixmap(self.pixmap)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(previous_button)
        hbox.addWidget(next_button)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.label)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle(self.title)
        # page.change()
        self.show()

    # @pyqtSlot()
    # def change_page(self):
    #     while True:
    #         _, frame = webcam.read()
    #
    #         # We send this frame to GazeTracking to analyze it
    #         gaze.refresh(frame)
    #         frame = gaze.annotated_frame()
    #         text = ""
    #
    #         if gaze.is_blinking():
    #             text = "Blinking"
    #         elif gaze.is_right():
    #             text = "Looking right"
    #         elif gaze.is_left():
    #             text = "Looking left"
    #         elif gaze.is_center():
    #             text = "Looking center"
    #         if gaze.is_top():
    #             text += " top"
    #         elif gaze.is_bottom():
    #             text += " bottom"
    #
    #         cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
    #
    #         left_pupil = gaze.pupil_left_coords()
    #         right_pupil = gaze.pupil_right_coords()
    #         cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9,
    #                     (147, 58, 31), 1)
    #         cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9,
    #                     (147, 58, 31),
    #                     1)
    #
    #         cv2.imshow("Demo", frame)
    #
    #         if cv2.waitKey(1) == 27:
    #             break
    #
    #         # frame = gaze.annotated_frame()
    #         if gaze.is_right() and gaze.is_bottom() and not gaze.is_blinking():
    #             self.curr_photo += 1
    #             self.initUI()


if __name__ == '__main__':
    app = QApplication([])
    window = QWidget()
    mywidget = App()
    # mywidget.changed.connect(mywidget.change_page)
    ex = App()
    app.exec_()



