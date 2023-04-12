#written by Alex Brinson (brinson@mit.edu, alexjbrinson@gmail.com) on behalf of EMA Lab
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import serial
import time
import numpy as np
import os
 
qtCreatorFile = "GuiBigSkyWidget.ui" # Enter file here.
 
Ui_Widget, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QWidget, Ui_Widget, cPort, label):
  def __init__(self):
    self.comPort = cPort
    global qSwitchMode, flashLampMode, activeStatus, shutterStatus, qSwitchStatus, frequency, fLampEnergy, fLampVoltage, qTriggerSetting
    global proposedVoltage, proposedEnergy, proposedFrequency
    global serialConnected, dangerMode
    global terminalEnabled, terminalLineCurrently
    global calibrationFilePresent, calibVolts, calibPower

    calibrationFilePresent=False #TODO: check for calibration file in gui directory

    #Testing different possible serial ports to see if any of them is a Big Sky laser. If ">cg" evokes a temperature readout, we found a live one.
    serialConnected = False
    for i in range(10):
      try:
        self.ser = serial.Serial("COM"+str(i),9600,timeout=1)
      except:
        print("i="+str(i)+" not this one")
      else:
        print("i="+str(i)+" maybe this one?")
        self.ser.flush(); self.ser.write(b'>cg\n')
        response = self.ser.read(140).decode('utf-8'); print("response:", response)
        if 'temp'in response:
          print("yeah this one.");
          temp=float(response.strip('\r\ntemp.CG d'))#
          tiempo = time.strftime("%d %b %Y %H:%M:%S",time.localtime())#
          
          serialConnected=True
          break

    dangerMode = True
    if serialConnected==False:
      print("Error: Laser not found. Ensure laser is on and check serial port connection.")
      fLampVoltage=-1
      #quit()

    #Initializing dummy values. These are updated to true laser settings once all widgets are connected, so they can be updated too.
    qSwitchMode = 0; flashLampMode = 0
    activeStatus = 0; shutterStatus = 0; qSwitchStatus = 0; qTriggerSetting = 0
    terminalEnabled = False
    proposedEnergy = 7; proposedVoltage = 500; proposedFrequency = 0

    # Creates gui object(?). Connects widget signals to functions defined lower down.
    # QtWidgets.QMainWindow.__init__(self)
    # Ui_MainWindow.__init__(self) #stack exchange said to replace both of these __inits__ with the line below
    super().__init__()
    self.setupUi(self)
    self.frequencyDoubleSpinBox.valueChanged.connect(self.setFrequency)
    self.frequencyDoubleSpinBox.editingFinished.connect(self.setFrequency)
    self.qSwitchRadioButton_0.clicked.connect(self.setQSwitchInternal)
    self.qSwitchRadioButton_1.clicked.connect(self.setQSwitchBurst)
    self.qSwitchRadioButton_2.clicked.connect(self.setQSwitchExternal)
    self.flashLampRadioButton_0.clicked.connect(self.setFlashLampInternal)
    self.flashLampRadioButton_1.clicked.connect(self.setFlashLampExternal)
    #self.flashLampVoltageLineEdit.textChanged.connect(self.setFlashLampVoltage_lineEdit)
    #self.flashLampVoltageHorizontalSlider.sliderReleased.connect(self.setFlashLampVoltage_hSlider)
    #self.flashLampEnergyDoubleSpinBox.valueChanged.connect(self.setFlashLampEnergy_spinBox)
    #self.flashLampEnergyHorizontalSlider.sliderReleased.connect(self.setFlashLampEnergy_hSlider)
    #self.lampActivationButton.clicked.connect(self.toggleActiveStatus)
    #self.shutterButton.clicked.connect(self.toggleShutterStatus)
    #self.qSwitchActivationButton.clicked.connect(self.toggleQSwitchStatus)
    #self.singlePulseButton.clicked.connect(self.singlePulse)
    self.lampActivationButton.clicked.connect(self.startLaser)#new#
    #self.fLampEnergyConfirmationButton.clicked.connect(self.confirmEnergySetting)
    self.flashLampVoltageLineEdit.returnPressed.connect(self.confirmVoltageSetting)
    self.frequencyConfirmationButton.clicked.connect(self.confirmFrequencySetting)
    #self.todo.returnPressed.connect(self.confirmEnergySetting)#new#
    #self.todo.returnPressed.connect(self.confirmVoltageSetting)#new#
    #self.frequencyDoubleSpinBox.returnPressed.connect(self.confirmFrequencySetting)#new#
    self.stopButton.clicked.connect(self.stopLaser)

    self.toggleInputButton.clicked.connect(self.enableTerminalInput)
    self.terminalInputLineEdit.textChanged.connect(self.updateTerminalCommand)
    self.terminalInputLineEdit.returnPressed.connect(self.sendTerminalCommand)
    self.terminalInputLabel.setEnabled(False); self.terminalInputLineEdit.setEnabled(False)

    #Checking for calibration file in local directory
    try:
      cwd = os.getcwd()
      if serialConnected:
        self.fetchSerial(); 
        calibData=np.loadtxt(cwd+"\\CalibrationDataBigSky"+str(self.comPort)+".csv",dtype="float",comments='#',delimiter=',')
      else: 
        calibData=np.loadtxt(cwd+"\\CalibrationDataBigSky.csv",dtype="float",comments='#',delimiter=',')
      calibVolts = calibData[:,0]; calibPower = calibData[:,1]
      calibrationFilePresent=True
    except:
      defaultCalibVolts=[800,900,950,1000,1050,1080]
      defaultCalibPower=[0.05,1.54,3.09,4.73,6.14,6.78]
    if calibrationFilePresent: print("calibration file loaded successfully")
    else: print("failed to load calibration file"); calibVolts=defaultCalibVolts; calibPower=defaultCalibPower

    #Initializing GUI values
    if serialConnected:
      self.fetchSerial(); self.label.setText("BIG SKY " + str(self.comPort) + " LASER CONTROL")
      self.update_fLampMode(self.ser)
      self.update_qSwitchMode(self.ser)
      #self.update_fLampValues(self.ser)
      self.update_fLampVoltage(self.ser)
      self.update_fLampEnergy(self.ser)
      #self.updateTemp(self.ser) #todo get this from serialport test
      self.temperatureOutput.setText(str(temp)+" C")#
      self.lastUpdateOutput.setText(str(tiempo))#
      self.updateFreq(self.ser)
    else: self.label.setText("Laser not found. This is a dummy GUI")

    #self.qSwitchActivationButton.setEnabled(activeStatus and shutterStatus)
    self.frequencyDoubleSpinBox.setEnabled(not(flashLampMode));
    self.frequencyConfirmationButton.setEnabled(not(flashLampMode))

    self.PowerEstimateValue.setText('%.2f'%np.interp(fLampVoltage,calibVolts,calibPower)+" W")

  def setFrequency(self):
    global proposedFrequency
    proposedFrequency = float(self.frequencyDoubleSpinBox.value())
    #TODO set frequency on hardware
    #print("frequencyDoubleSpinBox valueChanged")
    
  def confirmFrequencySetting(self):
    global proposedFrequency
    #toWrite = ">f{freq}\n".format(freq = str(0)+str(int(proposedFrequency*100)) if proposedFrequency<10 else str(int(proposedFrequency*100)) )
    toWrite = ">f{freq}\n".format(freq = str(int(proposedFrequency*100)) )
    self.terminalOutputTextBrowser.append(">f{freq}".format(freq = str(int(proposedFrequency*100)) ))#this is just a test feature
    if serialConnected:
      self.ser.flush(); self.ser.write(bytes(toWrite,"utf-8") ); response = self.ser.read(140).decode('utf-8'); frequency=float(response.strip('\r\nfreq. Hz'));
      self.frequencyDoubleSpinBox.setValue(frequency); print("frequency = {f}Hz".format(f=frequency))
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
      self.updateTemp(self.ser) 

  def updateFreq(self, serport):
    global frequency
    self.terminalOutputTextBrowser.append('>f')
    serport.flush();serport.write(b'>f\n')
    response = serport.read(140).decode('utf-8'); frequency=float(response.strip('\r\nfreq. Hz'));
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    print("frequency = {f}Hz".format(f=frequency))
    self.frequencyDoubleSpinBox.setValue(frequency)

  '''NOTE: These can only be changed while laser is in standby (>s). The GUI should now reproduce this behavior'''
  def setQSwitchInternal(self):
    global qSwitchMode; qSwitchMode = 0; print(">qsm0");
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>qsm0\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)#; self.updateTemp(self.ser)
      self.terminalOutputTextBrowser.append('>qsm0'); self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
  def setQSwitchBurst(self):
    global qSwitchMode; qSwitchMode = 1; print(">qsm1");
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>qsm1\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)#; self.updateTemp(self.ser)
      self.terminalOutputTextBrowser.append('>qsm1'); self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
  def setQSwitchExternal(self):
    global qSwitchMode; qSwitchMode = 2; print(">qsm2");
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>qsm2\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)#; self.updateTemp(self.ser)
      self.terminalOutputTextBrowser.append('>qsm2'); self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
  def setFlashLampInternal(self):
    global flashLampMode; flashLampMode = 0; print(">lpm0");
    self.frequencyDoubleSpinBox.setEnabled(not(flashLampMode)); self.frequencyConfirmationButton.setEnabled(not(flashLampMode))
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>lpm0\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)#; self.updateTemp(self.ser)
      self.terminalOutputTextBrowser.append('>lpm0'); self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
  def setFlashLampExternal(self):
    global flashLampMode; flashLampMode = 1; print(">lpm1");
    self.frequencyDoubleSpinBox.setEnabled(not(flashLampMode)); self.frequencyConfirmationButton.setEnabled(not(flashLampMode))
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>lpm1\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)#; self.updateTemp(self.ser)
      self.terminalOutputTextBrowser.append('>lpm1'); self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");

  '''def setFlashLampVoltage_lineEdit(self):
    global proposedVoltage, fLampVoltage
    proposedVoltage = self.flashLampVoltageLineEdit.text()
    #print("fLamp voltage spin box valueChanged")
    #self.flashLampVoltageHorizontalSlider.setValue(proposedVoltage)
  def setFlashLampVoltage_hSlider(self):
    global proposedVoltage
    proposedVoltage = int(self.flashLampVoltageHorizontalSlider.text())
    #print("fLampVoltage hSlider valueChanged")
    self.flashLampVoltageLineEdit.setValue(proposedVoltage)'''

  def confirmVoltageSetting(self):
    global proposedVoltage, fLampVoltage
    realUpdate=False
    try:
      proposedVoltage = int(self.flashLampVoltageLineEdit.text())
      if proposedVoltage<500 or proposedVoltage>1400:
        print("please enter an integer between 500 and 1400"); proposedVoltage = fLampVoltage
      else: realUpdate=True
    except: print("please enter an integer value."); proposedVoltage = fLampVoltage
    if realUpdate:
      toWrite = ">vmo{vol}\n".format( vol = str(0)+str(int(proposedVoltage)) if proposedVoltage<1000 else str(int(proposedVoltage)) )
      self.terminalOutputTextBrowser.append(toWrite.strip('\n'))
      if serialConnected:
        self.ser.flush(); self.ser.write(bytes(toWrite,"utf-8") );
        response = self.ser.read(140).decode('utf-8'); print("confirmVoltage response:",response)
        fLampVoltage=int(response.strip('\r\nvoltage m V'))
        print("voltage = {V}V".format(V=fLampVoltage))
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
        #self.flashLampVoltageHorizontalSlider.setValue(fLampVoltage)
        self.flashLampVoltageLineEdit.setText(str(fLampVoltage))
        self.update_fLampEnergy(self.ser)
        self.updateTemp(self.ser)
      else: fLampVoltage=proposedVoltage
      
      self.PowerEstimateValue.setText('%.2f'%np.interp(fLampVoltage,calibVolts,calibPower) + " W")
  
    else:
      self.flashLampVoltageLineEdit.setText(str(fLampVoltage))

  def toggleActiveStatus(self):
    global activeStatus, shutterStatus, qSwitchStatus, qSwitchMode
    activeStatus = 0 if activeStatus == 1 else 1
    #self.lampActivationButton.setText("Lamp Firing  Activated  ") if activeStatus else self.lampActivationButton.setText("Lamp Firing Deactivated")
    self.singlePulseButton.setEnabled(not(qSwitchStatus) and shutterStatus and activeStatus and (qSwitchMode==0))
    self.qSwitchRadioButton_0.setEnabled(not(activeStatus)); self.qSwitchRadioButton_1.setEnabled(not(activeStatus)); self.qSwitchRadioButton_2.setEnabled(not(activeStatus));
    self.flashLampRadioButton_0.setEnabled(not(activeStatus)); self.flashLampRadioButton_1.setEnabled(not(activeStatus))
    if activeStatus:
       print(">a"); self.lampActivationButton.setText("Lamp Firing  Activated  ")
       self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>a'+"</p>");

       if serialConnected:
        self.ser.flush(); self.ser.write(b'>a\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
    else:
      print(">s"); self.lampActivationButton.setText("Lamp Firing Deactivated")
      self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>s'+"</p>");
      shutterStatus = 0; #self.shutterButton.setText("Shutter Closed")
      qSwitchStatus = 0; #self.qSwitchActivationButton.setText("qSwitch Deactivated");
      if serialConnected:
        self.ser.flush(); self.ser.write(b'>s\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
    #self.qSwitchActivationButton.setEnabled(activeStatus and shutterStatus)

  def toggleShutterStatus(self):
    global activeStatus, shutterStatus, qSwitchStatus, qSwitchMode
    shutterStatus = 0 if shutterStatus == 1 else 1
    self.singlePulseButton.setEnabled(not(qSwitchStatus) and shutterStatus and activeStatus and (qSwitchMode==0))
    if shutterStatus:
      print(">r1"); #self.shutterButton.setText("Shutter  Open  ")
      self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>r1'+"</p>");
      if serialConnected:
        self.ser.flush(); self.ser.write(b'>r1\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
    else:
      print(">r0"); #self.shutterButton.setText("Shutter Closed")
      self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>r0'+"</p>");
      if serialConnected:
        self.ser.flush(); self.ser.write(b'>r0\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
    #self.qSwitchActivationButton.setEnabled(activeStatus and shutterStatus)

  def toggleQSwitchStatus(self):
    global activeStatus, shutterStatus, qSwitchStatus, qSwitchMode
    if qSwitchStatus:
      qSwitchStatus = 0; print(">sq"); self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>sq'+"</p>");
      #self.qSwitchActivationButton.setText("qSwitch Deactivated")
      if serialConnected:
        self.ser.flush(); self.ser.write(b'>sq\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")

    else:
      qSwitchStatus = 1; print(">pq"); self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>pq'+"</p>");
      #self.qSwitchActivationButton.setText("qSwitch  Activated  ")
      if serialConnected and dangerMode:
        self.ser.flush(); self.ser.write(b'>pq\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
        self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")

    #self.singlePulseButton.setEnabled(not(qSwitchStatus) and shutterStatus and activeStatus and (qSwitchMode==0))
  
  def singlePulse(self):
    print(">oq"); self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>oq'+"</p>");
    if serialConnected and dangerMode:
      self.ser.flush(); self.ser.write(b'>oq\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")

  def startLaser(self): #Single button to start lasing. Leaving lampfiring active with q-switch disabled could be damaging to laser.
    global activeStatus, shutterStatus, qSwitchStatus, qSwitchMode, terminalEnabled
    activeStatus = 1
    #self.lampActivationButton.setText("Laser Activated ") if activeStatus else self.lampActivationButton.setText("START")
    self.qSwitchRadioButton_0.setEnabled(not(activeStatus)); self.qSwitchRadioButton_1.setEnabled(not(activeStatus)); self.qSwitchRadioButton_2.setEnabled(not(activeStatus));
    self.flashLampRadioButton_0.setEnabled(not(activeStatus)); self.flashLampRadioButton_1.setEnabled(not(activeStatus))

    print(">a"); self.lampActivationButton.setText("Laser Activated")
    print(">r1"); #self.lampActivationButton.setText("Shutter Opened")
    print(">pq"); #self.lampActivationButton.setText("Qswitch Activated")
    self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>a'+"</p>");
    self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>r1'+"</p>");
    self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>pq'+"</p>");
    shutterStatus = 1; #self.shutterButton.setText("Shutter Closed")
    qSwitchStatus = 1; #self.qSwitchActivationButton.setText("qSwitch Deactivated");
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>a\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
      self.ser.flush(); self.ser.write(b'>r1\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
      self.ser.flush(); self.ser.write(b'>pq\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    self.lampActivationButton.setEnabled(not(activeStatus)) 

  def stopLaser(self): #This does the same thing as toggleActiveStatus if active status == 1. But it's redundant for safety, in case gui and laser get de-synced somehow.
    global activeStatus, shutterStatus, qSwitchStatus, qSwitchMode, terminalEnabled
    activeStatus = 0
    #self.lampActivationButton.setText("Lamp Firing  Activated  ") if activeStatus else self.lampActivationButton.setText("Lamp Firing Deactivated")
    #self.singlePulseButton.setEnabled(not(qSwitchStatus) and shutterStatus and activeStatus and (qSwitchMode==0))
    self.qSwitchRadioButton_0.setEnabled(not(activeStatus)); self.qSwitchRadioButton_1.setEnabled(not(activeStatus)); self.qSwitchRadioButton_2.setEnabled(not(activeStatus));
    self.flashLampRadioButton_0.setEnabled(not(activeStatus)); self.flashLampRadioButton_1.setEnabled(not(activeStatus))
    
    print(">s"); self.lampActivationButton.setText("START")
    self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>s'+"</p>");
    shutterStatus = 0; #self.shutterButton.setText("Shutter Closed")
    qSwitchStatus = 0; #self.qSwitchActivationButton.setText("qSwitch Deactivated");
    if serialConnected:
      self.ser.flush(); self.ser.write(b'>s\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    #self.qSwitchActivationButton.setEnabled(activeStatus and shutterStatus and not(terminalEnabled))
    self.lampActivationButton.setEnabled(not(activeStatus)) 

  def enableTerminalInput(self):
    global terminalEnabled, flashLampMode, qSwitchMode
    if terminalEnabled:
      terminalEnabled=False;
      self.stopLaser(); #self.lampActivationButton.setEnabled(True); #self.shutterButton.setEnabled(True)
      self.update_fLampMode(self.ser)
      self.update_qSwitchMode(self.ser)
      self.update_fLampVoltage(self.ser)
      self.update_fLampEnergy(self.ser)
      self.updateTemp(self.ser)
      self.updateFreq(self.ser)
    else:
      terminalEnabled=True;
      #self.lampActivationButton.setEnabled(False)#self.shutterButton.setEnabled(False); self.qSwitchActivationButton.setEnabled(False); self.singlePulseButton.setEnabled(False);
    self.terminalInputLabel.setEnabled(terminalEnabled); self.terminalInputLineEdit.setEnabled(terminalEnabled)
    self.qSwitchRadioButton_0.setEnabled(not(terminalEnabled)); self.qSwitchRadioButton_1.setEnabled(not(terminalEnabled)); self.qSwitchRadioButton_2.setEnabled(not(terminalEnabled))
    self.flashLampRadioButton_0.setEnabled(not(terminalEnabled)); self.flashLampRadioButton_1.setEnabled(not(terminalEnabled))
    frequencyBoolean = not(terminalEnabled) and not(flashLampMode)
    self.frequencyDoubleSpinBox.setEnabled(frequencyBoolean); self.FrequencyLabel.setEnabled(frequencyBoolean); self.frequencyConfirmationButton.setEnabled(frequencyBoolean)
    #self.flashLampEnergyLabel.setEnabled(not(terminalEnabled)); self.fLampEnergyConfirmationButton.setEnabled(not(terminalEnabled));
    #self.flashLampEnergyHorizontalSlider.setEnabled(not(terminalEnabled)); self.flashLampEnergyDoubleSpinBox.setEnabled(not(terminalEnabled));
    self.flashLampVoltageLabel.setEnabled(not(terminalEnabled)); self.fLampVoltageConfirmationButton.setEnabled(not(terminalEnabled));
    self.flashLampVoltageHorizontalSlider.setEnabled(not(terminalEnabled)); self.flashLampVoltageSpinBox.setEnabled(not(terminalEnabled));

  def fetchSerial(self):
    global self.comPort
    print(">sn"); self.terminalOutputTextBrowser.append("<p style='color: black'>"+'>sn'+"</p>");
    if serialConnected and dangerMode:
      self.ser.flush(); self.ser.write(b'>sn\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>")
    self.comPort = response.strip(' \r\ns/number') #TODO finish this line

  def updateTerminalCommand(self,text):
    global terminalLineCurrently
    terminalLineCurrently = text

  def sendTerminalCommand(self):
    global terminalLineCurrently

    #else:
    toWrite = '>'+terminalLineCurrently+'\n'
    print("sending to terminal:",toWrite) #TODO: finish this function
    self.terminalOutputTextBrowser.append("<p style='color: blue'>"+toWrite.strip('\n')+"</p>");
    if serialConnected:
      self.ser.flush(); self.ser.write(bytes(toWrite,"utf-8") );
      response = self.ser.read(140).decode('utf-8');
      self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    terminalLineCurrently = ''
    self.terminalInputLineEdit.setText(terminalLineCurrently)

  def updateTemp(self, serport): #def updateTemp(self, serport, command):
    self.terminalOutputTextBrowser.append('>cg')
    serport.flush();serport.write(b'>cg\n')
    response = serport.read(140).decode('utf-8'); temp=float(response.strip('\r\ntemp.CG d'))
    print("temperature = {T}C".format(T=temp))
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    tiempo = time.strftime("%d %b %Y %H:%M:%S",time.localtime())
    print("time = {t}".format(t=tiempo))
    self.temperatureOutput.setText(str(temp)+" C")
    self.lastUpdateOutput.setText(str(tiempo))

  def update_fLampVoltage(self, serport):
    global fLampVoltage
    self.terminalOutputTextBrowser.append('>v')
    serport.flush();serport.write(b'>v\n')
    response = serport.read(140).decode('utf-8'); fLampVoltage=int(response.strip('\r\nvoltage V'))
    print("voltage = {V}V".format(V=fLampVoltage))
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    #self.flashLampVoltageHorizontalSlider.setValue(fLampVoltage)
    self.flashLampVoltageLineEdit.setText(str(fLampVoltage))

    self.PowerEstimateValue.setText('%.2f'%np.interp(fLampVoltage,calibVolts,calibPower) + " W")
    
  def update_fLampEnergy(self, serport):
    global fLampEnergy
    self.terminalOutputTextBrowser.append('>ene')
    serport.flush();serport.write(b'>ene\n')
    response = serport.read(140).decode('utf-8'); fLampEnergy=float(response.strip('\r\nenergy J'))
    print("energy = {E}J".format(E=fLampEnergy))
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    #self.flashLampEnergyHorizontalSlider.setValue(int(10*fLampEnergy))
    self.flashLampEnergyValue.setText(str(fLampEnergy)+" J")

  def update_fLampMode(self, serport):
    global flashLampMode
    self.terminalOutputTextBrowser.append('>lpm')
    serport.flush();serport.write(b'>lpm\n')
    response = serport.read(140).decode('utf-8'); flashLampMode=int(response.strip('\r\nLP synch :  '))
    print("flashLampMode = {f}".format(f=flashLampMode))
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    #self.flashLampEnergyHorizontalSlider.setValue(int(10*fLampEnergy))
    if flashLampMode==0: self.flashLampRadioButton_0.setChecked(True)
    elif flashLampMode==1: self.flashLampRadioButton_1.setChecked(True)
    else: print("ERROR. flashLampMode makes no sense");serport.flush();serport.write(b'>s\n'); serport.read(140).decode('utf-8');

  def update_qSwitchMode(self, serport):
    global qSwitchMode
    self.terminalOutputTextBrowser.append('>qsm')
    serport.flush();serport.write(b'>qsm\n')
    response = serport.read(140).decode('utf-8'); qSwitchMode=int(response.strip('\r\nQS mode :  '))
    print("qSwitchMode = {q}".format(q=qSwitchMode))
    self.terminalOutputTextBrowser.append("<p style='color: green'>"+response.strip('\r\n')+"</p>");
    #self.flashLampEnergyHorizontalSlider.setValue(int(10*fLampEnergy))
    if qSwitchMode==0: self.qSwitchRadioButton_0.setChecked(True)
    elif qSwitchMode==1: self.qSwitchRadioButton_1.setChecked(True)
    elif qSwitchMode==2: self.qSwitchRadioButton_2.setChecked(True)
    else: print("ERROR. qSwitchMode makes no sense");serport.flush();serport.write(b'>s\n'); serport.read(140).decode('utf-8');

  def safeExit():
    print(">s")
    if serialConnected:
      #serport=self.ser
      #print(serport)
      self.ser.flush(); self.ser.write(b'>s\n'); response = self.ser.read(140).decode('utf-8'); print("response:", response)

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  app.aboutToQuit.connect(MyApp.safeExit)
  window = MyApp()
  window.show()
  sys.exit(app.exec_())