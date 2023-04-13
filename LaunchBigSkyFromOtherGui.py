'''
#written by Alex Brinson (brinson@mit.edu, alexjbrinson@gmail.com) on behalf of EMA Lab
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import serial
import time
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import os
import serial.tools.list_ports
#print(serial.tools.list_ports.comports()[0][0])
possibleDevices=[comport.device for comport in serial.tools.list_ports.comports()]
print(possibleDevices)


app=QtWidgets.QApplication([])
window = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
buttons=[]
#Testing different possible serial ports to see if any of them is a Big Sky laser. If ">cg" evokes a temperature readout, we found a live one.
serialConnected = False
for i in range(10):
  buttons+=[QtWidgets.QPushButton('launch com %d'%i)]
  processes+=[QtCore.QProcess()]
  layout.addWidget(buttons[i])
  try:
    ser = serial.Serial("COM"+str(i),9600,timeout=1)
  except:
    print("i="+str(i)+" not this one")
    print(buttons[i])
    buttons[i].setEnabled(False)
  else:
    print("i="+str(i)+" maybe this one?")
    ser.flush(); ser.write(b'>cg\n')
    response = ser.read(140).decode('utf-8'); print("response:", response)
    if 'temp'in response:
      print("yeah this one.");
      temp=float(response.strip('\r\ntemp.CG d'))#
      tiempo = time.strftime("%d %b %Y %H:%M:%S",time.localtime())#
      
      serialConnected=True
      break
window.setLayout(layout)
window.show()
app.exec()
'''

#written by Alex Brinson (brinson@mit.edu, alexjbrinson@gmail.com) on behalf of EMA Lab
import sys
import serial
import time
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import os
import serial.tools.list_ports
#print(serial.tools.list_ports.comports()[0][0])
possibleDevices=[comport.device for comport in serial.tools.list_ports.comports()]
print(possibleDevices)


from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit,
                                QVBoxLayout, QWidget)
from PyQt5.QtCore import QProcess
import sys
import subprocess

class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    layout = QVBoxLayout()
    self.buttons=[]
    self.processes={}
    for i in range(10):
      self.buttons+=[QPushButton('launch com %d'%i)]
      layout.addWidget(self.buttons[i])
      self.buttons[i].pressed.connect(lambda i=i: self.start_process(i))
      try:
        ser = serial.Serial("COM"+str(i),9600,timeout=1)
        print('trying com port %d'%i)
      except:
        print("i="+str(i)+" not this one")
        self.buttons[i].setEnabled(False)
      else:
        print("i="+str(i)+" maybe this one?")
        ser.flush(); ser.write(b'>sn\n')
        response = ser.read(140).decode('utf-8'); print("response:", response)
        if 'number'in response:
          print("yeah this one."); ser.close()

    # self.btn = QPushButton("Execute")
    # self.btn.pressed.connect(self.start_process)
    # self.text = QPlainTextEdit()
    # self.text.setReadOnly(True)
    # self.btn2 = QPushButton("Execute2")
    # self.btn2.pressed.connect(self.start_process2)
    self.text = QPlainTextEdit()
    
    layout.addWidget(self.text)

    window = QWidget()
    window.setLayout(layout)

    self.setCentralWidget(window)
    window.show()
  def message(self, s):
    self.text.appendPlainText(s)

  def start_process(self, j):
    self.message("Executing process %d."%j)
    self.processes[j] = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
    self.processes[j].start("python", ['BigSkyControllerAmbitious.py'])
app=QApplication(sys.argv)
w=MainWindow()
w.show()
app.exec_()
#'''