import sys
import numpy as np
import pyaudio
import pyqtgraph as pg 
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QMenu, QFileDialog, QWidget, QPushButton, QVBoxLayout, QGridLayout, QInputDialog, QTextEdit
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
import wave
import speech_recognition as sr

format = pyaudio.paFloat32
channels = 1
rate = 16000
chunk = 512
start = 0
N = 512
filename = "file.wav"
record_seconds = 3

class audioAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        modeMenu = menubar.addMenu('Mode')

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Esc')
        exitAct.triggered.connect(self.close)
     
        recordAct = QAction('Record', self)
        recordAct.setShortcut('Ctrl+R')
        recordAct.triggered.connect(self.record)

        rtMicAct = QAction('Realtime microphone analyzer', self)
        rtMicAct.setShortcut('Ctrl+A')
        rtMicAct.triggered.connect(self.spectrum)

        recogAct = QAction('Speech Recognition', self)
        recogAct.setShortcut('Ctrl+O')
        recogAct.triggered.connect(self.speechRecog)
        
        fileMenu.addAction(exitAct)

        modeMenu.addAction(recordAct)
        modeMenu.addAction(rtMicAct)
        modeMenu.addAction(recogAct)

        self.setGeometry(446, 156, 1028, 768)
        self.setWindowTitle('Audio Analyzer')    
        self.show()
    
    def speechRecog(self):
        def convertAudio(self):
            r = sr.Recognizer()
            sound = filename
            with sr.AudioFile(sound) as source:
                sound = r.listen(source)
            try:
                text = r.recognize_google(sound)
                textedit.setText(text)

            except Exception as e:
                print(e)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,"Open file", "","Audio File (*.wav)", options=options)
        vbox = QVBoxLayout()

        wid = QWidget(self)
        self.setCentralWidget(wid)

        textedit = QTextEdit()
        textedit.setFont(QFont("Segoe UI", 15))
        vbox.addWidget(textedit)

        btn = QPushButton("Speech to text")
        vbox.addWidget(btn)
        btn.clicked.connect(convertAudio)

        wid.setLayout(vbox)
        
    def spectrum(self):
        # Spectrum  
        SpecTrum = specTrum()
        self.setCentralWidget(SpecTrum)

    def record(self):            
        def recordAction(self):
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format = format,
                channels = channels,
                rate = rate,
                input = True,
                frames_per_buffer = chunk)
            frames = []          

            # Enter time
            i, okPressed = QInputDialog.getInt(None, "Record time","Second:", 3, 0, 100, 1)
            record_seconds = i

            # Start recording
            for i in range(0, int(rate / chunk * record_seconds)):
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("Finished recording")

            # Save file
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getSaveFileName(None ,"Save file","","Audio File (*.wav)", options=options)

            waveFile = wave.open(filename, 'wb')
            waveFile.setnchannels(channels)
            waveFile.setsampwidth(audio.get_sample_size(format))
            waveFile.setframerate(rate)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

        wid = QWidget(self)
        self.setCentralWidget(wid)

        recordBtn = QPushButton()
        recordBtn.setToolTip('Start Recording')
        recordBtn.setShortcut('R')
        recordBtn.setFixedSize(30, 30)
        recordBtn.setIcon(QtGui.QIcon('record.png'))
        recordBtn.clicked.connect(recordAction)
        
        grid = QGridLayout()
        grid.addWidget(recordBtn)        

        vbox = QVBoxLayout()
        SpecTrum = specTrum()
        vbox.addWidget(SpecTrum)
        vbox.addLayout(grid)      

        wid.setLayout(vbox)

        

class specTrum(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #PyAudio
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format = format,
            channels = channels,
            rate = rate,
            input = True,
            output = False,
            frames_per_buffer = chunk)

        #PlotWidget
        self.plotitem = self.getPlotItem()
        self.plotitem.setMouseEnabled(x = False, y = False) 
        self.plotitem.setYRange(0, 10, padding = 0)
        self.plotitem.setXRange(0, 2000, padding = 0)
        self.plotSpectrum = self.plotitem.plot()
        
        #Label
        self.specAxis = self.plotitem.getAxis("bottom")
        self.specAxis.setLabel("Frequency (Hz)")        

        #Update plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def update(self):
        data = self.input()
        freqlist = np.fft.fftfreq(N, d = 1.0 / rate)
        x = np.fft.fft(data)
        amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in x]
        self.plotSpectrum.setData(freqlist, amplitudeSpectrum)

    def input(self):
        data = self.stream.read(chunk)
        data = np.frombuffer(data, np.float32)
        return data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    audioAnalyzer = audioAnalyzer()
    sys.exit(app.exec_())
