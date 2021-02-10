import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, request

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#define actuators GPIOs
kasaRelay = 13

# Define led pins as output
GPIO.setup(kasaRelay, GPIO.OUT)   

# turn leds OFF 
GPIO.output(kasaRelay, GPIO.LOW)

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    if deviceName == 'kasaRelay':
        actuator = kasaRelay
   
        if action == "otworz":
            GPIO.output(actuator, GPIO.HIGH)
            time.sleep(1.0)
            GPIO.output(actuator, GPIO.LOW)

   
    return render_template('index.html', )
if __name__ == "__main__":
   app.run(host='192.168.43.42', port=80, debug=True)