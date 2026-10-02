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
        ip = self.searchAtemIp()
        if ip:
            self.switcher.connect(ip)
            connected = self.switcher.waitForConnection()
            if(connected):

                self.connected = True 

                print("PGM:", self.getProgramNumber())
                print("PVW:", self.getPreviewNumber())
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


    def change_program_auto(self):
        if self.connected:
            self.switcher.execAutoME(0)

    def getPreviewNumber(self):
        if self.connected:
            return self.switcher.previewInput[0].videoSource.value
        
    def getProgramNumber(self):
        if self.connected:
            return self.switcher.programInput[0].videoSource.value
        