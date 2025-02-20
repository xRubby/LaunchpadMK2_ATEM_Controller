import PyATEMMax

class AtemControl:
    def __init__(self):
        self.switcher = PyATEMMax.ATEMMax()
        self.switcher.registerEvent(self.switcher.atem.events.disconnect, self.on_disconnected)
        self.switcher.registerEvent(self.switcher.atem.events.connect, self.on_connected)
        self.connected = False
        
    def searchAtemIp(self):
        """ Scansiona gli IP nella rete 192.168.1.x per trovare l'ATEM """
        for i in range(1, 255):
            ip = f"192.168.1.{i}"

            self.switcher.ping(ip)
            if self.switcher.waitForConnection():
                print(f"ATEM switcher trovato su {ip}")
                return ip

        return None

    def connect(self) -> bool:
        """ Prova a connettersi all'ATEM se un IP è stato trovato """
        ip = "192.168.1.138"
        #ip = self.searchAtemIp()
        if ip:
            self.switcher.atem.defaultConnectionTimeout = 2.5
            self.switcher.connect(ip)
            connected = self.switcher.waitForConnection(infinite=False, waitForFullHandshake=False)
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

    def disconnect(self) -> bool:
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
            self.switcher.setProgramInputVideoSource(0, input_number)


    def getPreviewNumber(self):
        if self.connected:
            return
        
    def getProgramNumber(self):
        if self.connected:
            return
        