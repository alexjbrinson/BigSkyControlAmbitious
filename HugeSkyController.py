import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
 QWidget, QAction, QTabWidget,QVBoxLayout, QGridLayout, QTabBar, QLineEdit, QTextBrowser)
#from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from BigSkyControllerAmbitious import SingleLaserController
import serial.tools.list_ports

class App(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('Big Sky Controller Hub')
    self.left = 0; self.width = 700
    self.top = 0 ; self.height = 200
    self.setGeometry(self.left, self.top, self.width, self.height)
    self.table_widget = MyTableWidget(self)
    self.setCentralWidget(self.table_widget)
    self.show()

class HomeTab(QWidget):
  def __init__(self,parent):
    super().__init__()
    possibleDevices=[comport.device for comport in serial.tools.list_ports.comports()]
    self.layout = QGridLayout(parent)
    self.buttons=[]
    self.devices=[]
    self.labelLineEdits=[]
    self.processes={}
    for i in range(10):#for dev in possibleDevices:
      try:
        ser = serial.Serial("COM"+str(i),9600,timeout=1)
        print('trying com port %d'%i)
      except:
        print("i="+str(i)+" not this one")
        #self.buttons[i].setEnabled(False)
        sn=-1
      else:
        print("i="+str(i)+" maybe this one?")
        ser.flush(); ser.write(b'>sn\n')
        response = ser.read(140).decode('utf-8'); print("response:", response)
        if 'number'in response:
          print("yeah this one."); ser.close()
          print(response)
          sn=1#TODO: fix
      self.devices+=[i]#dev
      self.buttons+=[QPushButton('launch COM%d ; SN%d'%(self.devices[i],sn))]
      self.labelLineEdits+=[QLineEdit('')]
      self.layout.addWidget(self.buttons[i], i,0)
      self.layout.addWidget(self.labelLineEdits[i], i,1)
    self.text = QTextBrowser()
    self.layout.addWidget(self.text)
    self.setLayout(self.layout)
    
class MyTableWidget(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.layout = QVBoxLayout(self)
    # Initialize tab screen
    self.tabs = QTabWidget()
    #self.tabs.resize(width,height)
    self.homeTab=HomeTab(self)
    print("test: ", len(self.homeTab.buttons))

    for i in range(len(self.homeTab.buttons)):
      self.homeTab.buttons[i].pressed.connect(lambda i=i: self.createTab(i))

    self.tabs.addTab(self.homeTab,"Home")
    #self.tabs.addTab(self.homeTab,"Home")
    
    # Add tabs
    #self.tabs.addTab(SingleLaserController(labelString='TEST'),"Tab 1")
    #print("test2: ", self.tabs.widget(1).size().height())
    #self.tabs.addTab(SingleLaserController(labelString='TEST2'),"Tab 2")
    self.tabs.setTabsClosable(True)
    self.tabs.tabCloseRequested.connect(self.closeTab)
    self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None) #removes close button from homeTab
    #self.tabs.tabBar().setTabButton(0, self.tabs.tabBar.RightSide, None)
    # Add tabs to widget
    self.layout.addWidget(self.tabs)

  def createTab(self, i):
    com=self.homeTab.devices[i]; labelString=self.homeTab.labelLineEdits[i].text()
    if labelString=='': labelString='test'+str(self.tabs.count())
    self.homeTab.text.append("Creating Gui for com%d, with label \'%s\'"%(com,labelString))
    self.tabs.addTab(SingleLaserController(cPort=com,labelString=labelString),labelString)
    self.homeTab.buttons[i].setEnabled(False)
  def closeTab(self,i):
    comport=self.tabs.widget(i).comPort
    self.homeTab.text.append("Closing tab %d aka com%d"%(i,comport))
    self.tabs.widget(i).safeExit()
    self.tabs.removeTab(i)
    for j in range(len(self.homeTab.buttons)): #I don't have a good way of identifying which tab number corresponds to which laser...
      if self.homeTab.devices[j]==comport:
        self.homeTab.buttons[j].setEnabled(True); break
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())