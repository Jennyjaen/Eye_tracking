import sys
import math
import os
import pyautogui as pa
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import tobii_research as tr
import time
import pygame as pg
import schedule as sc

g_gaze_data=None
click_area=[0,500,500] #device time stamp, h, w
drag_area=[]
first=0 
last=0
drag_start=False
start_time=0
#https://developer.tobiipro.com/tobii.research/python/reference/1.1.0.23-beta-g9262468f/gaze_data_8py-example.html
#http://developer.tobiipro.com/python/python-step-by-step-guide.html
'''
{'device_time_stamp': 26987408, 'system_time_stamp': 36628255210, 'left_gaze_point_on_display_area': (0.39376187324523926, 0.3558783531188965), 
'left_gaze_point_in_user_coordinate_system': (-34.740962982177734, 125.78491973876953, 60.326107025146484), 'left_gaze_point_validity': 1, 
'left_pupil_diameter': 5.1175384521484375, 'left_pupil_validity': 1, 
'left_gaze_origin_in_user_coordinate_system': (-62.81155014038086, -77.7467269897461, 617.912109375), 
'left_gaze_origin_in_trackbox_coordinate_system': (0.6468167901039124, 0.7340949177742004, 0.45188695192337036), 'left_gaze_origin_validity': 1, 
'right_gaze_point_on_display_area': (0.36757388710975647, 0.3632172644138336),
 'right_gaze_point_in_user_coordinate_system': (-44.10836410522461, 124.39735412597656, 59.82101058959961), 'right_gaze_point_validity': 1, 
 'right_pupil_diameter': 5.021240234375, 'right_pupil_validity': 1, 
'right_gaze_origin_in_user_coordinate_system': (3.122692108154297, -79.176513671875, 617.5389404296875),
'right_gaze_origin_in_trackbox_coordinate_system': (0.4947779178619385, 0.7384464144706726, 0.44520360231399536), 'right_gaze_origin_validity': 1}
'''

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
        
        self.move(0,0)
        #pa.moveTo(300,300)
        #self.width = 40
        #self.height = 40
        #self.resize(self.width, self.height)
        #self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        #self.setAttribute(QtCore.Qt.WA_NoChildEventsForParent,True) #mouse event skip
        #self.setFocusPolicy(QtCore.Qt.NoFocus)


        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #self.setStyleSheet("background-color:transparent;")
        #painter.fillRect(event.rect(), QBrush(QColor(255, 100, 100, 50)))

        #palette = QPalette(self.palette())
        #palette.setColor(palette.Background, Qt.transparent)
        #self.setPalette(palette)
        
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.show()

    def click_event(self):
        global g_gaze_data, click_area, drag_start

        if(g_gaze_data!=None and drag_start==False):
            left_eye = g_gaze_data['left_gaze_point_on_display_area']
            right_eye = g_gaze_data['right_gaze_point_on_display_area']
            mid_eye=[((left_eye[0]+right_eye[0])*1920/2), ((left_eye[1]+right_eye[1])*1080/2)]
            if(math.isnan(mid_eye[0]) or math.isnan(mid_eye[1])):
                #self.move(click_area[1], click_area[2])
                pa.moveTo(click_area[1], click_area[2])
            else:
                #print(mid_eye)
                #self.move(int(mid_eye[0]), int(mid_eye[1]))
                pa.moveTo(int(mid_eye[0]), int(mid_eye[1]))
                if((abs(mid_eye[0]-click_area[1])<60) and (abs(mid_eye[1]-click_area[2])<60)):
                    if(time.time()-click_area[0]>1):
                        interval=round(2*(time.time()-click_area[0]))
                        pa.click(x=int(mid_eye[0])-5, y=int(mid_eye[1]), button='left', interval=interval)
                        #click_area[0]=time.time()
                else:
                    click_area=[time.time(), int(mid_eye[0]), int(mid_eye[1])]
                    #print("change")
 
 #눈이 감겼는지, 감겼다면 몇 초째 감겨있는지 확인.
    def closed_check(self):
        global g_gaze_data, first, last
        closed=False
        
        if(g_gaze_data!=None):
            l_dia=g_gaze_data['left_pupil_diameter']
            l_valid=g_gaze_data['left_pupil_validity']
            r_dia=g_gaze_data['right_pupil_diameter']
            r_val=g_gaze_data['right_pupil_validity']

            if(math.isnan(l_dia) and l_valid==0 and math.isnan(r_dia) and r_val==0):
                closed=True
                #print(time.time())
                #if(first==0 or time.time()-first>0.1):
                if(first == 0):
                    first=time.time()
                    #print("first close")
                
                last=time.time()

        if(closed==False):
            first = 0
            return False
        else:
            temp= last - first              
            if(temp>1):
                first=0
                return temp
            else:
                return False

            

#문제점 : 1초 지나면 함수 계속 들어옴
    def drag_event(self):
        global g_gaze_data, drag_start,drag_area, start_time
        close=self.closed_check()
        if(close!=False):
            pg.mixer.init()
            drag_start=not drag_start

            if(drag_start==True):
                print("drag start")
                pg.mixer.music.load("GlassDropandRoll.mp3")
            else:
                print("drag end")
                start_time=0
                pg.mixer.music.load("WoodPlankFlicks.mp3")
            pg.mixer.music.play()

        #while로 하면 통제가 안됨.. drag
        if(drag_start==True):
            #drag값 저장 시작.
            if(g_gaze_data!=None):
                if(start_time==0):
                    start_time=time.time()

                left_eye = g_gaze_data['left_gaze_point_on_display_area']
                right_eye = g_gaze_data['right_gaze_point_on_display_area']
                mid_eye=[((left_eye[0]+right_eye[0])*1920/2), ((left_eye[1]+right_eye[1])*1080/2)]

                if( math.isnan(mid_eye[0])==False and math.isnan(mid_eye[1])==False and (time.time()-start_time)>5):
                    pa.moveTo(mid_eye[0], mid_eye[1])
                    left_eye2 = g_gaze_data['left_gaze_point_on_display_area']
                    right_eye2 = g_gaze_data['right_gaze_point_on_display_area']
                    mid_eye2=[((left_eye2[0]+right_eye2[0])*1920/2), ((left_eye2[1]+right_eye2[1])*1080/2)]
                    if( math.isnan(mid_eye2[0])==False and math.isnan(mid_eye2[1])==False):    
                        print(mid_eye2[0]-mid_eye[0],mid_eye2[1]-mid_eye2[0])
                        pa.drag(mid_eye2[0]-mid_eye[0],mid_eye2[1]-mid_eye2[0],3, button='left' )
                        print("drag!")
                        start_time=0
    
                    


    def paintEvent(self, event):
        global g_gaze_data
        global click_area
        self.resize(100,100)
        #print(g_gaze_data)
        self.click_event()
        self.drag_event()

    def closeEvent(self, event):
        self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        print('destroy Visualizer')


def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    global g_gaze_data
    g_gaze_data=gaze_data

    left_eye = gaze_data['left_gaze_point_on_display_area']
    right_eye = gaze_data['right_gaze_point_on_display_area']

    #print(gaze_data)
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




