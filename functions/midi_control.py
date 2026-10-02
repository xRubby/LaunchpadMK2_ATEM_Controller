import mido
import time
import asyncio
import os
from typing import List

from functions.atem_control import AtemControl

from launchpad.Tasto import Tasto


#from APIs.youtube_api import isLive


green_color = 123
red_color = 6
white_color = 3
no_color = 0

program = None
preview = None

atem_switcher = AtemControl()

credentials_file = 'credentials.json'

def find_launchpad():
    input_name = None
    output_name = None
    
    for name in mido.get_input_names(): # type: ignore
        if "Launchpad MK2" in name:
            input_name = name
            break
    
    for name in mido.get_output_names(): # type: ignore
        if "Launchpad MK2" in name:
            output_name = name
            break
    
    return input_name, output_name

def create_tasti() -> List[Tasto]:

    tasti = []

    for i, canale_switcher in zip(range(81, 89), range(1, 9)):
        tasti.append(Tasto(i, white_color, canale_switcher, "Video Source"))

    tasti.append(Tasto(61, white_color, 3010, "Video Source"))  #MP1
    tasti.append(Tasto(62, white_color, 3020, "Video Source"))  #MP2

    tasti.append(Tasto(41, red_color, 0, "Cut"))
    tasti.append(Tasto(42, red_color, 0, "Auto"))

    return tasti

def getTastoByValore(tasti: List[Tasto], valore: int) -> Tasto | None:

    for tasto in tasti:
        if tasto.getValore() == valore:
            return tasto
    return None

def get_tasto_canale_switch_by_numero(tasti: List[Tasto], numero_canale: int) -> Tasto | None:

    for tasto in tasti:
        if tasto.getTipo() == "Video Source" and tasto.canale_switcher == numero_canale:
            return tasto
    return None


def keyboard_led(outport, tasti: List[Tasto], type="create"):
    if type in "create":
        for tasto in tasti:
            outport.send(mido.Message('note_on', note=tasto.getValore(), velocity=tasto.getColore()))
            time.sleep(0.1)
    elif type in "delete":
        for tasto in tasti:
            outport.send(mido.Message('note_off', note=tasto.getValore(), velocity=no_color))
            time.sleep(0.1)

        if os.path.exists(credentials_file):
            for i, j in zip(range(107, 103, -1), range(108,112)):
                outport.send(mido.Message('control_change', control=i, value=no_color))
                outport.send(mido.Message('control_change', control=j, value=no_color))
                time.sleep(0.1)

def cambia_colore_tasto(outport, tasto: Tasto, colore_str = white_color):
    outport.send(mido.Message('note_on', note=tasto.getValore(), velocity=colore_str))

def change_selected_camera(inport, outport, atem_switcher: AtemControl, tasti: List[Tasto], note_value: int):
    global program, preview

    try:
        tasto = getTastoByValore(tasti, note_value)
        
        if tasto is None:
            return

        elif tasto.getTipo() == "Video Source":
            if preview and preview != program:
                outport.send(mido.Message('note_on', note=preview.getValore(), velocity=white_color))

            new_preview = getTastoByValore(tasti, note_value)

            assert preview is not None and new_preview is not None
            if new_preview.getValore() != preview.getValore():
                try:
                    print(f"Cambio preview a: {new_preview.getCanaleSwitcher()}")
                    atem_switcher.change_preview(new_preview.getCanaleSwitcher())
                    outport.send(mido.Message('note_on', note=note_value, velocity=green_color if new_preview != program else red_color))
                    preview = new_preview
                except Exception as e:
                    print(f"Errore durante il cambio di preview: {e}")
                
        elif tasto.getTipo() in ("Cut", "Auto"):
            if program:
                outport.send(mido.Message('note_on', note=program.getValore(), velocity=green_color))
            elif preview == program:
                return
            
            new_program = preview
            if new_program is not None:
                try:
                    match note_value:
                        case 41:
                            atem_switcher.change_program(new_program.getCanaleSwitcher())
                        case 42:
                            atem_switcher.change_program_auto()
                    outport.send(mido.Message('note_on', note=new_program.getValore(), velocity=red_color))

                    preview = program
                    program = new_program
                    
                except Exception as e:
                    print(f"Errore durante il cambio di program: {e}")

    except Exception as e:
        print(f"Errore: {e}")

async def check_live_status(outport):
    try:
        if os.path.exists(credentials_file):
            while True:
                live_status = False #await isLive()
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
        global last_note_selected, program, preview

        tasti = create_tasti()
        keyboard_led(outport, tasti, "create")
        program_numero = atem_switcher.getProgramNumber()
        preview_numero = atem_switcher.getPreviewNumber()

        program = get_tasto_canale_switch_by_numero(tasti, program_numero) if program_numero else get_tasto_canale_switch_by_numero(tasti, 1)
        preview = get_tasto_canale_switch_by_numero(tasti, preview_numero) if preview_numero else get_tasto_canale_switch_by_numero(tasti, 1)

        cambia_colore_tasto(outport, preview, green_color) if preview is not None else None
        cambia_colore_tasto(outport, program, red_color) if program is not None else None

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
        keyboard_led(outport, tasti, "delete")
        print(f"Task 'midi_input' cancellato")