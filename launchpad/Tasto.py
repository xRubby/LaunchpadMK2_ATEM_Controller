class Tasto:
    def __init__(self, valore: int, colore: int, canale_switcher: int, tipo: str):
        self.valore = valore
        self.colore = colore
        self.canale_switcher = canale_switcher
        self.tipo = tipo

    def getValore(self):
        return self.valore
    
    def getCanaleSwitcher(self):
        return self.canale_switcher
    
    def getColore(self):
        return self.colore
    
    def getTipo(self):
        return self.tipo