import sys
import math
import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
import pyautogui as pa
from win32api import *
from datetime import datetime
import tobii_research as tr
import pygame as pg
import schedule as sc

'''

'''

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


#Global 변수 선언...
music=False
goal=0
howlong=1
now=0
g_gaze_data=None
click_area=[0,500,500] #device time stamp, h, w
first=0 
last=0
mid_eye=[500,500]
slider_geo=[0,0]
window_geo=[0,0]
#forward geo, backward geo [0, 1] 은 얘네의 실질적 위치, [2]는 직전에 보고 있었는지 여부로 결정하자.
forward_geo=[0,0,0]
backward_geo=[0,0,0]
pointer_geo=[500,500]
dwell=False
drag=False

class Mymp3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.player=QMediaPlayer()
        self.playlist=QMediaPlaylist(self.player)
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.duration_Changed)
        self.player.positionChanged.connect(self.position_Changed)
    
    def initUI(self):
        self.setWindowTitle("Music Player")
        self.setGeometry(300,300,1000,600)
        btn=QPushButton("Add music", self)
        btn.move(20,20)
        btn.clicked.connect(self.btn_clicked)

        self.pointer=QPushButton("", self)
        self.pointer.setGeometry(150,110,40,40)
        self.pointer.setStyleSheet("background-color: green; border-radius : 20; border : 2px solid black")
        self.pointer.pressed.connect(self.button_move)

        self.forward=QPushButton("▶", self)
        self.backward=QPushButton("◀", self)
        self.forward.move(700, 110)
        self.forward.resize(80, 80)
        self.backward.move(20, 110)
        self.backward.resize(80, 80)
        self.forward.clicked.connect(self.go_front)
        self.backward.clicked.connect(self.go_back)

        self.loudness=QLabel("S", self)

        self.where1=QLabel("S",self)
        self.where1.move(725, 80)
        self.where1.setFont(QFont('Arial', 20))
        self.where2=QLabel("S",self)
        self.where2.move(50, 80)
        self.where2.setFont(QFont('Arial', 20))

        
 #움직이긴 하는데 한번에 움직임
    def paintEvent(self, event):
        global howlong, now
        qp=QPainter()
        qp.begin(self)
        self.pbar=self.progressbar(qp)
        self.update_geo()
        qp.end()

    def button_move(self):
        global howlong, click_area, drag
        #print("click is done either")
        while(GetAsyncKeyState(0x01) & 0x8000):
            mx,_ = pa.position()
            ax=self.geometry().x()
            #ay=self.geometry().y()
            depart=mx-ax-25
            
            #문제: 얘가 async 하게 움직이지 않음.
            #어떤때는 잘 재생되는데, 어떤때는 멈춰있음. 다른 action 취해주면 또 다시 잘됨.
            if(depart>125 and depart<625):
                self.pointer.move(depart, 105)
                self.update_point()
                self.player.setPosition(int((depart-125)*howlong/500))
            elif(depart<=125):
                self.pointer.move(125, 105)
                self.update_point()
                self.player.setPosition(1)
            elif(depart>=625):
                self.pointer.move(625, 105)
                self.update_point()
                self.player.setPosition(howlong)
        
        if(drag):            
            mx=click_area[1]
            ax=self.geometry().x()
            depart=mx-ax-25
            print("should be update", depart)

            #문제: 얘가 async 하게 움직이지 않음.
            #어떤때는 잘 재생되는데, 어떤때는 멈춰있음. 다른 action 취해주면 또 다시 잘됨.
            if(depart>125 and depart<625):
                self.pointer.move(depart, 105)
                self.update_point()
                self.player.setPosition(int((depart-125)*howlong/500))
            elif(depart<=125):
                self.pointer.move(125, 105)
                self.update_point()
                self.player.setPosition(1)
            elif(depart>=625):
                self.pointer.move(625, 105)
                self.update_point()
                self.player.setPosition(howlong)
            drag=False


    def update_point(self):
        global pointer_geo
        px=self.pointer.geometry().x()
        py=self.pointer.geometry().y()
        ax=self.geometry().x()
        ay=self.geometry().y()
        print("updated", px)
        pointer_geo=[px+ax+25, py+ay+25]

    def update_geo(self):
        #print("updated")
        global slider_geo, window_geo, forward_geo, backward_geo
        ax=self.geometry().x()
        ay=self.geometry().y()
        fx=self.forward.geometry().x()
        fy=self.forward.geometry().y()
        bx=self.backward.geometry().x()
        by=self.backward.geometry().y()
        
        slider_geo=[ax+150, ay+130]
        window_geo=[ax, ay]
        forward_geo=[fx+ax,fy+ay,0]
        backward_geo=[bx+ax, by+ay,0]

        #print(forward_geo, backward_geo)

    def progressbar(self, qp):
        global dwell, click_area, window_geo
        pen=QPen(Qt.black,3,Qt.SolidLine)
        brush=QBrush(Qt.VerPattern)
        qp.setPen(pen)
        qp.drawLine(150,130,650,130)
        #눈금.
        pen=QPen(Qt.gray,1, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(100):
            qp.drawLine(150+5*i, 120, 150+i*5, 140)

        pen=QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(21):
            qp.drawLine(150+i*25, 115, 150+i*25, 145)   

        if(dwell==True):
            qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            if(drag==True):
                qp.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
            hello_future=click_area[1]-window_geo[0]
            qp.drawEllipse(hello_future, 110, 20, 20)
            self.loudness.move(hello_future-5, 105)
            self.loudness.setText(str(int(hello_future*100/howlong)))

    def duration_Changed(self, msec):
        global howlong
        howlong=msec
        #self.slider.setRange(0,msec)

    def position_Changed(self, position):
        global now, howlong
        now=position
        self.where1.setText(str(int(now*100/howlong)))
        self.where2.setText(str(int(now*100/howlong)))

        rate=now/howlong
        #print(rate)
        self.pointer.setGeometry(int(150+rate*500),110,50,50)
        self.update_point()
        #self.slider.setValue(position)

    def btn_clicked(self):
        global music
        files=QFileDialog.getOpenFileNames(None, 'Get Audio', filter='Audio Files (*.mp3 *.ogg *.wav)')
        url=QUrl.fromLocalFile(files[0][0])
        if(url!=None):
            music=True
        self.playlist.addMedia(QMediaContent(url))
        self.player.setPlaylist(self.playlist)
        self.playlist.setCurrentIndex(0)
        self.player.play()

    def go_front(self):
        global now, howlong
        print("front")
        print(time.time())
        if(howlong-now>1000):
            self.player.setPosition(now+1000)
        else:
            self.player.setPosition(howlong)

    def go_back(self):
        global now, pointer_geo
        print("backward")
        print(time.time())
        if(now>2000):
            self.player.setPosition(now-2000)
            
        else:
            self.player.setPosition(0)

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
        self.setGeometry(300,300,1000,600)
        self.move(0,0)
        
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.show()


    def click_event(self):
        global g_gaze_data, window_geo, forward_geo, backward_geo, mid_eye
        eye=[500,500]
        if(g_gaze_data!=None):
            where=self.wink()
            if(where=="left"):
                eye = g_gaze_data['left_gaze_point_on_display_area']
            
            elif(where=="right"):
                eye = g_gaze_data['right_gaze_point_on_display_area']
            else:
                #print("wrong case")
                eye=[500,500]

            if(where!=False):
                #print(eye[0]*1920, eye[1]*1080)
                #pa.move(int(eye[0]*1920), int(eye[1]*1080))
                #pa.move(int(eye[0]*960 +10), int(eye[1]*540+10))
                print(eye[0], eye[1])
                if(forward_geo[0]<=eye[0] and forward_geo[0]+50>=eye[0] and forward_geo[1]<=eye[1] and forward_geo[1]+50>=eye[1]):
                    print("looking at forward")
                    
                    #forward_geo[2]=1
                elif(backward_geo[0]<=eye[0] and backward_geo[0]+50>=eye[0] and backward_geo[1]<=eye[1] and backward_geo[1]+50>=eye[1]):
                    print("looking at backward")
                    #backward_geo[2]=1

 
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
                if(first == 0):
                    first=time.time()
                last=time.time()

        if(closed==False):
            first = 0
            return False
        else:
            temp= last - first              
            return temp
        
    def wink(self):
        global g_gaze_data
        if(g_gaze_data!=None):
            l_dia=g_gaze_data['left_pupil_diameter']
            l_valid=g_gaze_data['left_pupil_validity']
            r_dia=g_gaze_data['right_pupil_diameter']
            r_val=g_gaze_data['right_pupil_validity']

            #왼쪽 눈 감기
            if(math.isnan(l_dia) and l_valid==0 and (not math.isnan(r_dia)) and r_val!=0):
                #print("left wink")
                #right_eye = gaze_data['right_gaze_point_on_display_area']
                #pa.move(int(right_eye[0]*1920), int(right_eye[1]*1080))
                return "right"
            elif((not math.isnan(l_dia)) and l_valid!=0 and math.isnan(r_dia) and r_val==0):
                #print("right wink")
                #left_eye = gaze_data['left_gaze_point_on_display_area']
                #pa.move(int(left_eye[0]*1920), int(left_eye[1]*1080))
                return "left"
                
            else:
                return False



    def drag_event(self):
        global g_gaze_data, pointer_geo, slider_geo, pointer_geo, mid_eye,dwell, click_area, drag

        #slider 범위
        if(g_gaze_data!=None and drag==False):

            #시간 timeline을 좀 나누자
            if(math.isnan(mid_eye[0]) or math.isnan(mid_eye[1])):
                #self.move(click_area[1], click_area[2])
                left_eye = g_gaze_data['left_gaze_point_on_display_area']
                #pa.moveTo(click_area[1], click_area[2])
            else:
                #print(int(pointer_geo[0]), int(pointer_geo[1]))
                if(dwell==False):
                    pa.moveTo(int(mid_eye[0]), int(mid_eye[1]))
                #else:
                #    pa.moveTo(pointer_geo[0], pointer_geo[1]) #pointer 위치로 옮겨야함.

                #click area같은 애를 사용하고, 거기서 몇 정도를 줄까
                if(slider_geo[1]-10<=mid_eye[0] and mid_eye[1]<=slider_geo[1]+510 and (abs(mid_eye[1]-slider_geo[1])<30)):
                    if(click_area[0]==0):
                        click_area=[time.time(), mid_eye[0], mid_eye[1]]
                    #print("in the area", time.time()-click_area[0])
                    if(abs(mid_eye[0]-click_area[1])<50):
                        if(time.time()-click_area[0]>0.1 and time.time()-click_area[0]<0.6):
                            dwell=True
                        elif(time.time()-click_area[0]>=0.8):
                            print("drag start")
                            drag=True
                    else:
                        click_area=[time.time(), mid_eye[0], mid_eye[1]]
                        dwell=False

        elif (drag==True):
            pa.click(pointer_geo[0], pointer_geo[1]) #pointer 위치로 옮겨야함.
            #pa.mouseUp(click_area[1], click_area[2], duration=1, button='left')
            dwell=False
            drag=False


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
    global g_gaze_data, mid_eye
    g_gaze_data=gaze_data

    left_eye = gaze_data['left_gaze_point_on_display_area']
    right_eye = gaze_data['right_gaze_point_on_display_area']
    mid_eye=[((left_eye[0]+right_eye[0])*1920/2), ((left_eye[1]+right_eye[1])*1080/2)]
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


if __name__=="__main__":
    app=QApplication(sys.argv)
    myWindow=Mymp3()
    myWindow.show()

    ex = Visualizer()
    timer = QtCore.QTimer()
    timer.timeout.connect(timerEvent)
    #timer.start(0.03)
    timer.start(3)
    sys.exit(app.exec_())
    exit()