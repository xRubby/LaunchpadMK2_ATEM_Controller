import mido
import time
import asyncio
import os

from APIs.youtube_api import isLive

last_note_selected = 0
green_color = 123
red_color = 6
no_color = 0

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

def keyboard_led(outport, type="create"):
    if type in "create":
        for i in range(81, 89):
            outport.send(mido.Message('note_on', note=i, velocity=green_color))
            time.sleep(0.1)

        for i in range(61, 65):
            outport.send(mido.Message('note_on', note=i, velocity=green_color))
            time.sleep(0.1)
    elif type in "delete":
        for i in range(81, 89):
            outport.send(mido.Message('note_off', note=i, velocity=no_color))
            time.sleep(0.1)

        for i in range(61, 65):
            outport.send(mido.Message('note_off', note=i, velocity=no_color))
            time.sleep(0.1)
        if os.path.exists(credentials_file):
            for i, j in zip(range(107, 103, -1), range(108,112)):
                outport.send(mido.Message('control_change', control=i, value=no_color))
                outport.send(mido.Message('control_change', control=j, value=no_color))
                time.sleep(0.1)

def change_selected_camera(inport, outport, note_value):
    global last_note_selected

    try:
        if note_value in range(81, 89) or note_value in range(61, 65):
            if last_note_selected:
                outport.send(mido.Message('note_on', note=last_note_selected, velocity=green_color))
                last_note_selected = note_value
            else:
                last_note_selected = note_value

            outport.send(mido.Message('note_on', note=note_value, velocity=red_color))
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

async def process_midi_input(inport, outport):
    try:
        global last_note_selected
        while True:
            for msg in inport.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    print(f"Tasto premuto: Nota {msg.note}, Velocità {msg.velocity}")
                    change_selected_camera(inport, outport, msg.note)
                elif msg.type == 'control_change':
                    if msg.value > 0:
                        print(f"Tasto superiore premuto: CC {msg.control}, Valore {msg.value}")
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print(f"Task 'midi_input' cancellato")