import time
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
import capture
import test_single
import shutil
class VideoBox(QWidget):

    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    video_url = ""

    def __init__(self, video_url="", video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        QWidget.__init__(self)
        self.video_url = video_url
        self.video_type = video_type  # 0: offline  1: realTime
        self.auto_play = auto_play
        self.status = self.STATUS_INIT  # 0: init 1:playing 2: pause
        self.resize(600, 700)
        self.setWindowTitle("动作识别系统")
        self.setStyleSheet("background-color: rgb(39, 134, 217);")
        # 组件展示
        self.pictureLabel = QLabel(self)
        init_image = QPixmap("00001.jpeg").scaled(self.width(), self.height())
        self.pictureLabel.setPixmap(init_image)
        self.pictureLabel.setFixedSize(500, 300)
        self.pictureLabel.move(50, 100)
        self.pictureLabel.setStyleSheet("QLabel{background:white;}")

        self.resultLabel = QLabel(self)
        self.resultLabel.setFixedSize(500, 300)
        self.resultLabel.move(50, 400)
        self.resultLabel.setStyleSheet("background-color: rgb(39, 134, 217);")
        self.resultLabel.setStyleSheet("QLabel{color:rgb(255,255,255);font-size:70px;font-weight:bold;font-family:微软黑体;}""QLabel{background-color: rgb(39, 134, 217);}")
        self.resultLabel.setAlignment(Qt.AlignCenter)

        self.openButton = QPushButton(self)
        self.openButton.setText("打开视频")
        self.openButton.move(100,30)
        self.openButton.setStyleSheet("background-color:rgb(255,255,255);color:rgb(0, 0, 0);font-weight:bold;")
        self.openButton.clicked.connect(self.openvideo)


        self.playButton = QPushButton(self)
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.move(270, 30)
        self.playButton.setStyleSheet("background-color:rgb(255,255,255);color:rgb(0, 0, 0);font-weight:bold;")
        self.playButton.clicked.connect(self.switch_video)

        self.preButton = QPushButton(self)
        self.preButton.setText("识别动作")
        self.preButton.move(360,30)
        self.preButton.setStyleSheet("background-color:rgb(255,255,255);color:rgb(0, 0, 0);font-weight:bold;")

        self.preButton.clicked.connect(self.recognition)

        # timer 设置
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_video_images)

        # video 初始设置
        self.playCapture = VideoCapture()
        if self.video_url != "":
            self.playCapture.open(self.video_url)
            fps = self.playCapture.get(CAP_PROP_FPS)
            self.timer.set_fps(fps)
            self.playCapture.release()
            if self.auto_play:
                self.switch_video()
            # self.videoWriter = VideoWriter('*.mp4', VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, size)

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def show_video_images(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cvtColor(frame, COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cvtColor(frame, COLOR_GRAY2BGR)

                temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
                temp_pixmap = QPixmap.fromImage(temp_image)
                self.pictureLabel.setPixmap(temp_pixmap)
                self.pictureLabel.setAlignment(Qt.AlignCenter)
            else:
                print("read failed, no frame data")
                success, frame = self.playCapture.read()
                if not success and self.video_type is VideoBox.VIDEO_TYPE_OFFLINE:
                    print("play finished")  # 判断本地文件播放完毕
                    self.reset()
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                return
        else:
            print("open file or capturing device error, init again")
            self.reset()

    def switch_video(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.status is VideoBox.STATUS_INIT:
            self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is VideoBox.STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is VideoBox.STATUS_PAUSE:
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (VideoBox.STATUS_PLAYING,
                       VideoBox.STATUS_PAUSE,
                       VideoBox.STATUS_PLAYING)[self.status]
    def openvideo(self):
        videoName, videoType = QFileDialog.getOpenFileName(self, "打开视频", "", "*.avi;;*.png;;All Files(*)")

        capture.handlevideo(videoName)
        self.video_url = videoName
        self.switch_video()
        self.resultLabel.setText(" ")
    def recognition(self):
        result = test_single.model()[0]
        print(result)
        if result==0:
              self.resultLabel.setText("画眼影")
              shutil.rmtree("action/")
              print("great")
        elif result ==11:
            self.resultLabel.setText("打台球")
            shutil.rmtree("action/")
        elif result ==9:
            self.resultLabel.setText("卧推")
            shutil.rmtree("action/")
        else:
            print(result)
            self.resultLabel.setText("无识别")
        # else:
        #     print("fault")

class Communicate(QObject):

    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()
    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


if __name__ == "__main__":
   app = QApplication(sys.argv)
   box = VideoBox()
   box.show()
   sys.exit(app.exec_())
