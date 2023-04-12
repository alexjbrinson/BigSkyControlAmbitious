import sys
import serial
print("test")


#Testing different possible serial ports to see if any of them is a Big Sky laser. If ">cg" evokes a temperature readout, we found a live one.
serialConnected = False
connectedserialPorts = []
for i in range(10):
  try:
    ser = serial.Serial("COM"+str(i),9600,timeout=1)
  except:
    print("i="+str(i)+" not this one")
  else:
    print("i="+str(i)+" maybe this one?")
    ser.flush(); ser.write(b'>sn\n')
    response = ser.read(140).decode('utf-8'); print("response:", response)
    if 'number'in response:
      print("yeah this one.");
      connectedserialPorts.append(i)
    if len(connectedserialPorts)>0: serialConnected=True
#exec(open("BigSKyControllerAmbitious.py").read())