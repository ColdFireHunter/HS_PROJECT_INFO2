import time
from machine import UART, Timer
import espnowcom
import command_handler
import pcCOM
import variabels

buttons = [4,5,6,7]
com = espnowcom.ESP_COM()
com_handler = command_handler.CMDHandler(com)
pc_handler = pcCOM.UARTtoPC(1,115200,43,44,buttons)
espcom_timer = Timer(0)
send_timer = Timer(1)
button_timer = Timer(2)

#There is a bug with the if __name__ == "__main__" check while using ESPNOW (Crash with OSError) so we didn't use it in any file
#I reported the bug to the development team of micropython


def communicate_with_esp_pc(t):
    if com.check_received():
        received_message = com.received_message()
        source, command, payload = com_handler.decode_message(received_message)
        com_handler.handle_command(source, command, payload)
    
    # Check for incoming data
    if pc_handler.data_available():
        try:
            command, payload = pc_handler.receive_command()
            pc_handler.handle_pc_command(command,payload)
        except:
            pc_handler.send_command("NACK","")
        
        
    pc_handler.handle_pc_logic()
        
def send_commands(t):
    if variabels.SEARCH_SEND == 1 and variabels.SEND_ONCE == 0:
        variabels.SEND_ONCE = 1
        mac = com.get_mac()
        command = "SRCH"
        payload = ""
        buffer = com_handler.encode_message(mac,command,payload)
        com.send_message(buffer)
        
    if variabels.HRBT_SEND == 1 and variabels.SEND_ONCE == 0:
        variabels.SEND_ONCE = 1
        mac = variabels.mac_list[int(variabels.NEEDED_MAC_INDEX)]
        command = "HRBT"
        payload = ""
        buffer = com_handler.encode_message(mac,command,payload)
        com.send_message(buffer)
        
    if variabels.COLR_SEND == 1 and variabels.SEND_ONCE == 0:
        variabels.SEND_ONCE = 1
        mac = variabels.mac_list[int(variabels.NEEDED_MAC_INDEX)]
        command = "COLR"
        payload = com_handler.encode_to_hex_string(variabels.COLOR_PAYLOAD)
        buffer = com_handler.encode_message(mac,command,payload)
        com.send_message(buffer)
        
    if variabels.SENS_SEND == 1 and variabels.SEND_ONCE == 0:
        variabels.SEND_ONCE = 1
        mac = variabels.mac_list[int(variabels.NEEDED_MAC_INDEX)]
        command = "SENS"
        payload = ""
        buffer = com_handler.encode_message(mac,command,payload)
        com.send_message(buffer)
        
    if variabels.TONE_SEND == 1 and variabels.SEND_ONCE == 0:
        variabels.SEND_ONCE = 1
        mac = variabels.mac_list[int(variabels.NEEDED_MAC_INDEX)]
        command = "TONE"
        payload = variabels.TONE_PAYLOAD
        buffer = com_handler.encode_message(mac,command,payload)
        com.send_message(buffer)

espcom_timer.init(period=100, callback=communicate_with_esp_pc)
send_timer.init(period=100, callback=send_commands)
