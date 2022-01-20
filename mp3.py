import sys
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
import time
howlong=1
now=0
sound=50

#dial: music volume, slider: music 
class MyWindow(QMainWindow):
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

        #self.playbtn=QPushButton("Play", self)
        #self.playbtn.move(20,30)
        #self.playbtn.clicked.connect(self.play)

        self.where=QLabel("S", self)
        self.where.move(300,30)
        self.where1=QLabel("S", self)
        self.where1.move(80,75)
        self.where2=QLabel("S", self)
        self.where2.move(630,75)

        self.forward=QPushButton("▶", self)
        self.backward=QPushButton("◀", self)
        self.forward.move(370,10)
        self.forward.resize(100,100)
        self.backward.move(220,10)
        self.backward.resize(100,100)
        self.forward.clicked.connect(self.go_front)
        self.backward.clicked.connect(self.go_back)


        self.forward1=QPushButton("▶", self)
        self.backward1=QPushButton("◀", self)
        self.forward1.move(570,100)
        self.forward1.resize(100,100)
        self.backward1.move(30,100)
        self.backward1.resize(100,100)
        self.forward1.clicked.connect(self.go_front)
        self.backward1.clicked.connect(self.go_back)

        self.slider=QSlider(Qt.Horizontal, self)
        self.slider.setRange(0,100)
        self.slider.move(150,110)
        self.slider.setValue(50)
        self.slider.resize(400, 50)
        self.slider.setTickPosition(1)
        self.slider.setTickInterval(5)
        #self.slider.valueChanged.connect(self.position_Changed)
        self.slider.sliderMoved.connect(self.set_position)

        self.dial=QDial(self)
        self.dial.move(80,250)
        self.dial.setRange(0,100)
        self.dial.setValue(50)
        self.dial.resize(300,300)
        self.dial.setNotchesVisible(True)
        self.dial.sliderMoved.connect(self.volumeChanged)

        self.loud=QLabel("Select new song", self)
        self.loud.setGeometry(210,400,150,50)


    def btn_clicked(self):
        files=QFileDialog.getOpenFileNames(None, 'Get Audio', filter='Audio Files (*.mp3 *.ogg *.wav)')
        url=QUrl.fromLocalFile(files[0][0])
        self.playlist.addMedia(QMediaContent(url))
        self.player.setPlaylist(self.playlist)
        self.playlist.setCurrentIndex(0)
        self.player.play()

    def volumeChanged(self):
        self.player.setVolume(self.dial.value())
        self.loud.setText(str(self.dial.value()))
        #print(self.dial.value())
    

    #음악이 play 되면서 자동으로 바뀜
    def position_Changed(self, position):
        #self.player.setPosition(self.slider.value())
        global now
        now=position
        self.where.setText(str(int(now*100/howlong)))
        self.where1.setText(str(int(now*100/howlong)))
        self.where2.setText(str(int(now*100/howlong)))
        self.loud.setText(str(self.dial.value()))
        self.slider.setValue(position)


    #slider 값 변경시 설정됨.
    def set_position(self, position):
        self.player.setPosition(position)

    def go_front(self):
        global now, howlong
        print("front")
        print(time.time())
        if(howlong-now>1000):
            self.player.setPosition(now+1000)
        else:
            self.player.setPosition(howlong)

    def go_back(self):
        global now
        print("backward")
        print(time.time())
        if(now>1000):
            self.player.setPosition(now-1000)
        else:
            self.slider.setPosition(0)


    def duration_Changed(self, msec):
        global howlong
        howlong=msec
        self.slider.setRange(0,msec)



#event loop +화면 출력 객체 생성
if __name__=="__main__":
    app=QApplication(sys.argv)
    myWindow=MyWindow()
    myWindow.show()
    #label=QLabel("Music Player")
    #label.show()

    #event loop 진입. 코드 계속 반복.
    app.exec_()