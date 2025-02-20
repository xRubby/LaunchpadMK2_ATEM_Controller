import mido
import time
import asyncio
import os
from typing import List

from functions.atem_control import AtemControl

from launchpad.Tasto import Tasto


from APIs.youtube_api import isLive


green_color = 123
red_color = 6
white_color = 3
no_color = 0

program = 0
preview = 0
last_preview = 0

tasto_preview: Tasto = None
tasto_program: Tasto = None

atem_switcher = AtemControl()

credentials_file = 'credentials.json'

def find_launchpad():
    input_name = None
    output_name = None
    
    for name in mido.get_input_names():
        if "Launchpad MK2" in name:
            input_name = name
            break
    
    for name in mido.get_output_names():
        if "Launchpad MK2" in name:
            output_name = name
            break
    
    return input_name, output_name

def create_tasti() -> List[Tasto]:

    tasti = []

    for i, canale_switcher in zip(range(81, 89), range(1, 9)):
        tasti.append(Tasto(i,white_color,canale_switcher, "Video Source"))

    tasti.append(Tasto(41, red_color, 0, "Cut"))
    tasti.append(Tasto(42, red_color, 0, "Auto"))

    return tasti

def getTastoByValore(tasti: List[Tasto], valore: int) -> Tasto:

    for tasto in tasti:
        if tasto.getValore() == valore:
            return tasto
    return None


def keyboard_led(outport, type="create"):
    if type in "create":
        for i in range(81, 89):
            outport.send(mido.Message('note_on', note=i, velocity=white_color))
            time.sleep(0.1)

        for i in range(61, 65):
            outport.send(mido.Message('note_on', note=i, velocity=white_color))
            time.sleep(0.1)

        for i in range(41, 42):
            outport.send(mido.Message('note_on', note=i, velocity=red_color))
            time.sleep(0.1)
    elif type in "delete":
        for i in range(81, 89):
            outport.send(mido.Message('note_off', note=i, velocity=no_color))
            time.sleep(0.1)

        for i in range(61, 65):
            outport.send(mido.Message('note_off', note=i, velocity=no_color))
            time.sleep(0.1)

        for i in range(41, 42):
            outport.send(mido.Message('note_off', note=i, velocity=no_color))
            time.sleep(0.1)

        if os.path.exists(credentials_file):
            for i, j in zip(range(107, 103, -1), range(108,112)):
                outport.send(mido.Message('control_change', control=i, value=no_color))
                outport.send(mido.Message('control_change', control=j, value=no_color))
                time.sleep(0.1)

def change_selected_camera(inport, outport, atem_switcher: AtemControl, tasti: List[Tasto], note_value: int):
    global last_preview, program, preview, tasto_preview, tasto_program


    try:
        valid_notes = set(range(81, 89)) | set(range(61, 65))
        
        if note_value in valid_notes:

            tasto_preview = getTastoByValore(tasti, note_value)

            if preview and preview != program:
                outport.send(mido.Message('note_on', note=last_preview, velocity=white_color))
            
            last_preview = preview = note_value

            if last_preview != program:
                try:
                    atem_switcher.change_preview(tasto_preview.getCanaleSwitcher())
                    outport.send(mido.Message('note_on', note=note_value, velocity=green_color))
                except Exception as e:
                    print(f"Errore durante il cambio di preview: {e}")
                
            

        if note_value == 41:

            if program:
                outport.send(mido.Message('note_on', note=program, velocity=white_color))
            elif preview == 0 or preview == program:
                return
            program = preview
            tasto_program = getTastoByValore(tasti, program)
            try:
                atem_switcher.change_program(tasto_program.getCanaleSwitcher())
                outport.send(mido.Message('note_on', note=program, velocity=red_color))
            except Exception as e:
                print(f"Errore durante il cambio di preview: {e}")
    except Exception as e:
        print(f"Errore: {e}")

async def check_live_status(outport):
    try:
        if os.path.exists(credentials_file):
            while True:
                live_status = await isLive()
                if live_status:
                    for i in range(104, 112):
                        outport.send(mido.Message('control_change', control=i, value=green_color))
                else:
                    for i in range(104, 112):
                        outport.send(mido.Message('control_change', control=i, value=red_color))
            
                await asyncio.sleep(60)
        
    except asyncio.CancelledError:
        print(f"Task 'check_live_status' cancellato")

async def process_midi_input(inport, outport, atem_switcher: AtemControl):
    try:
        global last_note_selected

        tasti = create_tasti()
        while True:
            for msg in inport.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    print(f"Tasto premuto: Nota {msg.note}, Velocità {msg.velocity}")
                    change_selected_camera(inport, outport, atem_switcher, tasti, msg.note)
                elif msg.type == 'control_change':
                    if msg.value > 0:
                        print(f"Tasto superiore premuto: CC {msg.control}, Valore {msg.value}")
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print(f"Task 'midi_input' cancellato")