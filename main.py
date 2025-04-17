from tkgpio import TkCircuit

configuration = {
    "width"         : 400, 
    "height"        : 500, 
    "leds"          : [{"x": 50, "y": 50, "name": "LED1", "pin":14}],
    "buttons"       : [{"x": 50, "y": 150, "name": "PUB1", "pin":21}],
   "light_sensors"  : [{"x": 50, "y": 200, "name": "Light Sensor", "pin": 8}],
    "motors"        : [{"x": 100, "y": 50, "name": "DC Motor", "forward_pin": 22, "backward_pin": 23}],
    "servos"        : [{"x": 100, "y": 100, "name": "Servomotor", "pin": 24, "min_angle": -90, "max_angle": 90, "initial_angle": 20}]
}

circuit = TkCircuit(configuration)

@circuit.run
def main(): 
    from gpiozero import LED, Button, Motor, AngularServo, LightSensor
    import firebase_admin
    from firebase_admin import credentials, db
    import threading
    import time
    
    SERVICE_ACCOUNT_KEY_PATH = './serviceKey.json'
    DATABASE_URL = 'https://ghazal1-31047-default-rtdb.firebaseio.com'
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})

    myLightSensor = LightSensor(8) 
    myLED = LED(14)
    myMotor = Motor(22,23) 
    myServo = AngularServo(24)
    
    # Button
    myButton = Button(21)
    def buttonDeactivated():
        updateButton(button_state=0)
    def buttonActivated():
       updateButton(button_state=1) 
    myButton.when_deactivated = buttonDeactivated
    myButton.when_activated = buttonActivated
    
     

    def updateButton(button_state):
        ref = db.reference('/monitor')
        ref.update({'button': button_state,})
    
    def updateLight(light):
        ref = db.reference('/monitor')
        ref.update({'light_sensor': light})

    def listenerDCMotor(event):
        myMotor.forward(event.data/100)
        print(f"DC = {event.data}")
        
    def listenerServo(event):
        myServo.angle = event.data 
        print(f"Servo = {event.data}")
        
    def listenerLED(event):
        myLED.value = event.data
        print(f"LED = {event.data}")
        
    def start_listeners():
        db.reference('control/dcmotor').listen(listenerDCMotor)
        db.reference('control/servo').listen(listenerServo)
        db.reference('control/led').listen(listenerLED)
    
    listener_thread = threading.Thread(target=start_listeners, daemon=True)
    listener_thread.start()
    
    updateButton(button_state=0)
    currentLight = int(myLightSensor.value*100)
    updateLight(light=currentLight)
    previousLight = -1
    
    while True:
        currentLight = int(myLightSensor.value*100)
        if currentLight != previousLight :
            updateLight(light=currentLight)
        time.sleep(0.2)
        previousLight = currentLight
        pass 