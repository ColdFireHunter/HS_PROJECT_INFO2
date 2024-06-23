from machine import Pin, PWM, I2C
import machine
import time
import espnowcom
import command_handler
import ledControl
import sensorControl
import soundControl
import sounds

debug_led = Pin(6, Pin.OUT, value=0)
debug_led.off()

buzzer = soundControl.Buzzer(pin=9)
sensor = sensorControl.SENSOR_CONTROL()
com = espnowcom.ESP_COM()
led = ledControl.LEDController()
com_handler = command_handler.CMDHandler(com,led,sensor,buzzer)
buzzer.add_song("STARUP", sounds.startup_sound)
buzzer.add_song("ALARM", sounds.alarm_sound)
print(com.get_mac())


while True:
    if com.check_received():
        try:
            received_message = com.received_message()
            source, command, payload = com_handler.decode_message(received_message)
            com_handler.handle_command(source, command, payload)
        except:
            print("MESSAGE TO OTHER DEVICE OR ERROR")