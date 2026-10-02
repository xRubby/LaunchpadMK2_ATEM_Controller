import socket
import time
import PyATEMMax

ATEM_PORT = 9910

# Pacchetto "hello" del protocollo ATEM
HELLO = bytes([
    0x10, 0x14, 0x53, 0xAB, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x3A, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
])

class AtemControl:
    def __init__(self):
        self.switcher = PyATEMMax.ATEMMax()
        self.switcher.registerEvent(self.switcher.atem.events.disconnect, self.on_disconnected)
        self.switcher.registerEvent(self.switcher.atem.events.connect, self.on_connected)
        self.connected = False
        
    def search_atem_ip(self):
        """Manda l'hello a 192.168.1.x senza creare sessioni PyATEMMax"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2)

        for i in range(1, 255):
            sock.sendto(HELLO, (f"192.168.1.{i}", ATEM_PORT))

        deadline = time.time() + 2
        while time.time() < deadline:
            try:
                data, (ip, port) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            except ConnectionResetError:
                continue
            if port == ATEM_PORT:
                sock.close()
                return ip

        sock.close()
        return None

    def connect(self) -> bool:
        """ Prova a connettersi all'ATEM se un IP è stato trovato """
        ip = self.search_atem_ip()
        if ip:
            self.switcher.connect(ip)
            connected = self.switcher.waitForConnection()
            if(connected):
                self.connected = True 
                return True
            else:
                self.switcher.disconnect()
                return False
        else:
            return False
        
    def on_connected(self, params):
        print("ATEM Connesso")
        self.connected = True
        self.switcher.setTransitionStyle(0, "mix")
        self.switcher.setTransitionMixRate(0, 50)

    def disconnect(self):
        """ Disconnette l'ATEM solo se era connesso """
        if self.connected:
            self.switcher.disconnect()
            self.connected = False

    def on_disconnected(self, params):
        print("Disconnessione ATEM")
        self.connected = False

    def change_preview(self, input_number: int):
        """ Cambia la preview dell'ATEM con l'input specificato """
        if self.connected:
            self.switcher.setPreviewInputVideoSource(0, input_number)


    def change_program(self, input_number: int):
        """ Cambia la preview dell'ATEM con l'input specificato """
        if self.connected:
            self.switcher.execCutME(0)


    def change_program_auto(self):
        if self.connected:
            self.switcher.execAutoME(0)

    def getPreviewNumber(self) -> int | None:
        if self.connected:
            return self.switcher.previewInput[0].videoSource.value
        
    def getProgramNumber(self) -> int | None:
        if self.connected:
            return self.switcher.programInput[0].videoSource.value
        