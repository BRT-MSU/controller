#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc1 = Roboclaw("/dev/ttyACM2",115200)
rc2 = Roboclaw("/dev/ttyACM3",115200)


#def displayspeed():
#	enc1 = rc.ReadEncM1(address)
#	enc2 = rc.ReadEncM2(address)
#	speed1 = rc.ReadSpeedM1(address)
#	speed2 = rc.ReadSpeedM2(address)
#
#	print("Encoder1:"),
#	if(enc1[0]==1):
#		print enc1[1],
#		print format(enc1[2],'02x'),
#	else:
#		print "failed",
#	print "Encoder2:",
#	if(enc2[0]==1):
#		print enc2[1],
#		print format(enc2[2],'02x'),
#	else:
#		print "failed " ,
#	print "Speed1:",
#	if(speed1[0]):
#		print speed1[1],
#	else:
#		print "failed",
#	print("Speed2:"),
#	if(speed2[0]):
#		print speed2[1]
#	else:
#		print "failed "

rc1.Open()
rc2.Open()
address1 = 0x80
address2 = 0x80

version1 = rc1.ReadVersion(address1)
version2 = rc2.ReadVersion(address2)
if version1[0]==False:
	print "GETVERSION1 Failed"
elif version2[0]==False:
        print "GETVERSION2 Failed"

else:
	print repr(version[1])

for k in range(30):
	rc1.SpeedM1(address1,12000)
	rc1.SpeedM2(address1,-12000)
	rc2.SpeedM1(address2,12000)
	rc2.SpeedM2(address2,-12000)
	for i in range(0,200):
		#displayspeed()
		time.sleep(0.01)
	rc1.SpeedM1(address1,0)
	rc1.SpeedM2(address1,0)
  	rc2.SpeedM1(address2,0)
   	rc2.SpeedM2(address2,0)
	time.sleep(1)
	rc1.SpeedM1(address1,12000)
	rc1.SpeedM2(address1,-12000)
	rc2.SpeedM1(address2,12000)
	rc2.SpeedM2(address2,-12000)
	for i in range(0,200):
		#displayspeed()
		time.sleep(0.01)
rc1.SpeedM1(address1,0)
rc1.SpeedM2(address1,0)
rc2.SpeedM1(address2,0)
rc2.SpeedM2(address2,0)
rc1.flushInput()
rc2.flushInput()
