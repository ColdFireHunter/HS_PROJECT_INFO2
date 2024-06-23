import time
import network
import espnow
import ubinascii

class ESP_COM:
    
    __bcast_mac = b'\xff\xff\xff\xff\xff\xff'  # Broadcast MAC address

    def __init__(self):
        # Initialize WLAN module in station mode
        self.wireless = network.WLAN(network.STA_IF)
        self.wireless.active(True)
        self.wireless.disconnect()
        
        # Initialize ESP-NOW
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.config(timeout_ms=10)  # Set timeout for ESP-NOW operations
        
        # Add broadcast peer
        self.add_bcast()

    def get_mac(self):
        """Return the MAC address of the ESP device."""
        mac = ubinascii.hexlify(self.wireless.config('mac'), ':').decode('utf-8')
        return mac

    def add_bcast(self):
        """Add the broadcast MAC address to the ESP-NOW peers."""
        return self.e.add_peer(self.__bcast_mac)

    def received_message(self):
        """Check for received messages and return the message as a string."""
        mac, message = self.e.recv()
        if message:
            output = message.decode('utf-8')
        else:
            output = ""
        return output

    def check_received(self):
        """Check if any message has been received."""
        return self.e.any()

    def send_message(self, payload):
        """Send a message to the broadcast MAC address."""
        try:
            self.e.send(self.__bcast_mac, payload)
            return True
        except:
            return False
        else:
            return False
