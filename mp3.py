import sys
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *

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

        self.slider=QSlider(Qt.Horizontal, self)
        self.slider.setRange(0,100)
        self.slider.move(40,50)
        self.slider.setValue(50)
        self.slider.resize(800, 40)
        #self.slider.valueChanged.connect(self.position_Changed)
        self.slider.sliderMoved.connect(self.set_position)

        self.dial=QDial(self)
        self.dial.move(50,100)
        self.dial.setRange(0,100)
        self.dial.setValue(50)
        self.dial.resize(500,500)
        self.dial.valueChanged.connect(self.volumeChanged)

    def btn_clicked(self):
        files=QFileDialog.getOpenFileNames(None, 'Get Audio', filter='Audio Files (*.mp3 *.ogg *.wav)')
        url=QUrl.fromLocalFile(files[0][0])
        self.playlist.addMedia(QMediaContent(url))
        self.player.setPlaylist(self.playlist)
        self.playlist.setCurrentIndex(0)
        self.player.play()

    def volumeChanged(self):
        self.player.setVolume(self.dial.value())
        print(self.dial.value())
    

    def position_Changed(self, position):
        #self.player.setPosition(self.slider.value())
        self.slider.setValue(position)

    def set_position(self, position):
        self.player.setPosition(position)

    def duration_Changed(self, msec):
        self.slider.setRange(0,msec)
        print(msec)



#event loop +화면 출력 객체 생성
if __name__=="__main__":
    app=QApplication(sys.argv)
    myWindow=MyWindow()
    myWindow.show()
    #label=QLabel("Music Player")
    #label.show()

    #event loop 진입. 코드 계속 반복.
    app.exec_()