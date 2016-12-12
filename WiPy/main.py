from machine import ADC

from WiPyFloat import Float


adc = ADC()
actual = Float()
current = Float()
divisor = Float()
divisor.load("928.3333")


while(True):
	apin = adc.channel(pin='GP4')
	
	intVal = apin()  # read value, 0-4095
	strVal = str(intVal)
	#current.load(strVal)
	
	actual = Float.divide(strVal,divisor)
	
	
	print("ADC value: ", intVal)
	print("Actual value:", actual)