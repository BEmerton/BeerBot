import sensor, image, time, math

import pyb

import ultrasonic

from pyb import Pin, Timer, Servo, LED


red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)

# Use [(128, 255)] for tracking a white line
# Use [(0, 64)] for  tracking a black line
#GRAYSCALE_THRESHOLD = [(20, 80, -30, 30, -60, 0)]    #Blue
# GRAYSCALE_THRESHOLD = [(80, 100, -20, 5, 40, 65)]       #Yellow
GRAYSCALE_THRESHOLD = [(25, 100, -70, -10, -20, 30)]    #Green

ROIS = [ # [ROI, weight]
        (0, 100, 160, 20, 0.7),
        (0, 075, 160, 20, 0.3),
        (0, 050, 160, 20, 0.1)
       ]

# Compute the weight divisor
weight_sum = 0
for r in ROIS: weight_sum += r[4]

# Camera setup
sensor.reset()                          # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565)     # use rgb.
sensor.set_framesize(sensor.QQVGA)      # use QQVGA for speed.
sensor.skip_frames(10)                  # Let new settings take affect.
sensor.set_whitebal(False)
clock = time.clock()                    # Tracks FPS.


pin1 = Pin('P0', Pin.OUT_PP, Pin.PULL_NONE)
pin2 = Pin('P1', Pin.OUT_PP, Pin.PULL_NONE)
pin3 = Pin('P2', Pin.OUT_PP, Pin.PULL_NONE)
pin4 = Pin('P3', Pin.OUT_PP, Pin.PULL_NONE)

pin1.value(0)
pin2.value(0)
pin3.value(0)
pin4.value(0)

sensor1_trigPin = pyb.Pin.board.P4
sensor1_echoPin = pyb.Pin.board.P5

sensor1 = ultrasonic.Ultrasonic(sensor1_trigPin, sensor1_echoPin)

tim = Timer(4, freq=20000) # Frequency in Hz
# Generate a 1KHz square wave on TIM4 with 50% and 75% duty cycles on channels 1 and 2, respectively.

def led_control(x):
    if   (x)>=-5: red_led.off()
    elif (x)<-5: red_led.on()
    if   (x)<=-5 or (x)>=5: green_led.off()
    elif (x)<5 and (x)>-5: green_led.on()
    if   (x)<5: blue_led.off()
    elif (x)>=5: blue_led.on()

def stop_motion():
    ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=0)  #left wheel
    ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=0)  #right wheel

    print("Robot Stopped at", distance1, "inches")
    distance2 = sensor1.distance_in_inches()

    while(distance2<=4):
        distance2 = sensor1.distance_in_inches()
        print("Robot Stopped at", distance2, "inches")
        pyb.delay(1000)

while(True):

    distance1 = sensor1.distance_in_inches()

    if distance1<= 3:
        stop_motion()

    clock.tick()                        # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot()             # Take a picture and return the image.

    centroid_sum = 0
    for r in ROIS:
        blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4])
        merged_blobs = img.find_markers(blobs)                      # merge overlapping blobs

        if merged_blobs:
            # Find the index of the blob with the most pixels.
            most_pixels = 0
            largest_blob = 0
            for i in range(len(merged_blobs)):
                if merged_blobs[i][4] > most_pixels:
                    most_pixels = merged_blobs[i][4]    # [4] is pixels.
                    largest_blob = i

            # Draw a rect around the blob.
            img.draw_rectangle(merged_blobs[largest_blob][0:4])     # rect
            img.draw_cross(merged_blobs[largest_blob][5],           # cx
                           merged_blobs[largest_blob][6])           # cy

            # [5] of the blob is the x centroid - r[4] is the weight.
            centroid_sum += merged_blobs[largest_blob][5] * r[4]

    center_pos = (centroid_sum / weight_sum) # Determine center of line.

    deflection_angle = 0

    deflection_angle = -math.atan((center_pos-80)/60)

    # Convert angle in radians to degrees.
    deflection_angle = math.degrees(deflection_angle)

    #led_control(deflection_angle)

    speed = deflection_angle/2

    if deflection_angle<=30 or deflection_angle>=-30:
        pin1.value(1)
        pin2.value(0)
        pin3.value(0)
        pin4.value(1)
        ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=85-speed)  #left wheel
        ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=85+speed)  #right wheel

    if deflection_angle>30:
        #ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=0)  #left wheel
        #ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=0)  #right wheel
        pin1.value(0)
        pin2.value(1)
        ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=95)  #left wheel
        ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=95)  #right


    if deflection_angle<-30:
        #ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=0)  #left wheel
        #ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=0)  #right wheel
        pin3.value(1)
        pin4.value(0)
        ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=95)  #left wheel
        ch2 = tim.channel(2, Timer.PWM, pin=Pin("P8"), pulse_width_percent=95)  #right wheel


    #print("Turn Angle: %f" % deflection_angle)

    #print(clock.fps())
