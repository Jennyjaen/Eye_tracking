import sys
import math
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5 import QtCore
from PyQt5 import QtGui

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import tobii_research as tr
import time
g_gaze_data=None

#https://developer.tobiipro.com/tobii.research/python/reference/1.1.0.23-beta-g9262468f/gaze_data_8py-example.html
#http://developer.tobiipro.com/python/python-step-by-step-guide.html

class Visualizer(QWidget):
    recordingInterval_value = 5
    recording_idx = 0
    my_eyetracker = None
    xPos = 0
    yPos = 0

    eyeCursorTrackingPen = QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.DashDotLine)
    eyeCursorNonTrackingPen = QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.DashDotLine)
    eyeCursorPen = eyeCursorTrackingPen

    isNotTracking= False
    oldPos = QtCore.QPoint()
    painter = QPainter()
    prevNow = datetime.now()

    monitorWidth = 1920
    monitorHeight = 1080

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initEyeTracker()

    def initEyeTracker(self):
        found_eyetrackers = tr.find_all_eyetrackers()

        self.my_eyetracker = found_eyetrackers[0]
        print("Address: " + self.my_eyetracker.address)
        print("Model: " + self.my_eyetracker.model)
        print("Name (It's OK if this is empty): " + self.my_eyetracker.device_name)
        print("Serial number: " + self.my_eyetracker.serial_number)

        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary= True)

#초기 도형. gaze 시작하면, 다른 형태로 전환됨.
    def initUI(self):
        self.setWindowTitle('GAZE')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.move(300, 300)
        self.width = 40
        self.height = 40
        self.resize(self.width, self.height)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_NoChildEventsForParent,True) #mouse event skip
        self.setFocusPolicy(QtCore.Qt.NoFocus)


        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #self.setStyleSheet("background-color:transparent;")
        #painter.fillRect(event.rect(), QBrush(QColor(255, 100, 100, 50)))

        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.show()
 
#gaze 시작하면 여기서 바뀐다. self.move 바꿔야할듯. input으로 주는 event는 무엇인가?
    def paintEvent(self, event):
        global g_gaze_data
        self.resize(100,100)
        #print(g_gaze_data)
        if(g_gaze_data!=None):
            left_eye = g_gaze_data['left_gaze_point_on_display_area']
            right_eye = g_gaze_data['right_gaze_point_on_display_area']
            mid_eye=[((left_eye[0]+right_eye[0])*1920/2), ((left_eye[1]+right_eye[1])*1080/2)]
            if(math.isnan(mid_eye[0]) or math.isnan(mid_eye[1])):
                self.move(500,500)
            else:
                print(mid_eye)
                self.move(int(mid_eye[0]), int(mid_eye[1]))
            #print(mid_eye)
        #self.move(500,500)

    def closeEvent(self, event):
        self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        print('destroy Visualizer')


def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    global g_gaze_data
    g_gaze_data=gaze_data

    left_eye = gaze_data['left_gaze_point_on_display_area']
    right_eye = gaze_data['right_gaze_point_on_display_area']
    '''
    print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
        gaze_left_eye=left_eye,
        gaze_right_eye=right_eye))
    '''
def timerEvent():
    ex.repaint()

def exit():
    print('exit')
    timer.stop()
    ex.destroy()
    app.exit(0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Visualizer()


    # pc context logger
    timer = QtCore.QTimer()
    timer.timeout.connect(timerEvent)
    timer.start(0.03)

    sys.exit(app.exec_())
    exit()




