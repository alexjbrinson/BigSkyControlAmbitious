import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import pyqtSlot
from BigSkyControllerAmbitious import SingleLaserController

class App(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('Big Sky Controller Hub')
    self.left = 0; self.width = 300
    self.top = 0 ; self.height = 200
    self.setGeometry(self.left, self.top, self.width, self.height)
    self.table_widget = MyTableWidget(self)
    self.setCentralWidget(self.table_widget)
    self.show()
    
class MyTableWidget(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.layout = QVBoxLayout(self)
    # Initialize tab screen
    self.tabs = QTabWidget()
    self.tabs.resize(300,200)
    
    # Add tabs
    self.tabs.addTab(SingleLaserController(labelString='TEST'),"Tab 1")
    self.tabs.addTab(SingleLaserController(labelString='TEST2'),"Tab 2")
    self.tabs.setTabsClosable(True)
    self.tabs.tabCloseRequested.connect(lambda index: self.closeTab(index))
    #self.tabs.tabBar().setTabButton(0, self.tabs.tabBar.RightSide, None)
    
    # Add tabs to widget
    self.layout.addWidget(self.tabs)
    #self.setLayout(self.layout)
    print(self.tabs)
  def closeTab(self,i):
    print("Test: closing tab %d"%i)
    self.tabs.widget(i).safeExit()
    self.tabs.removeTab(i)
    
  @pyqtSlot()
  def on_click(self):
    print("\n")
    for currentQTableWidgetItem in self.tableWidget.selectedItems():
      print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
