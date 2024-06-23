import time
import network
import espnow
import ubinascii

class ESP_COM:
    
    __bcast_mac = b'\xff\xff\xff\xff\xff\xff'
    
    def __init__(self):
        # Initialize WLAN module
        self.wireless = network.WLAN(network.STA_IF)
        self.wireless.active(True)
        self.wireless.disconnect()
        # Initialize ESP-NOW
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.config(timeout_ms=10)
        self.add_bcast()
    
    def get_mac(self):
        mac = ubinascii.hexlify(self.wireless.config('mac'), ':').decode('utf-8')
        return mac

    def add_bcast(self):
        return self.e.add_peer(self.__bcast_mac)
        
    def received_message(self):
        mac,message = self.e.recv()
        if message:
            output = message.decode('utf-8')
        else:
            output = ""
        return output
    
    def check_received(self):
        return self.e.any()
    
    def send_message(self,payload):
        try:
            self.e.send(self.__bcast_mac, payload)
            return True
        except:
            return False
        else:
            return False