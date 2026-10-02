import mido
import time



devices_precedenti = set(mido.get_input_names())

while True:
    devices_attuali = set(mido.get_input_names())

    # Device collegati
    collegati = devices_attuali - devices_precedenti
    for device in collegati:
        print(f"Device MIDI collegato: {device}")

    # Device scollegati
    scollegati = devices_precedenti - devices_attuali
    for device in scollegati:
        print(f"Device MIDI scollegato: {device}")

    devices_precedenti = devices_attuali

    time.sleep(1)