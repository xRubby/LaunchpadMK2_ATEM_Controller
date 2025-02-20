#main.py

import mido
import asyncio
from functions.midi_control import *

async def main():
    input_name, output_name = find_launchpad()

    if not input_name or not output_name:
        print("Launchpad MK2 non trovato!")
        return
    
    print(f"Connesso a Input: {input_name}, Output: {output_name}. Premi un tasto sul Launchpad.")

    try:
        inport = mido.open_input(input_name)
        outport = mido.open_output(output_name)

        keyboard_led(outport)
        
        live_check_task = asyncio.create_task(check_live_status(outport))
        midi_task = asyncio.create_task(process_midi_input(inport, outport))

        await asyncio.gather(live_check_task, midi_task)

    except KeyboardInterrupt:
        print("\nInterruzione ricevuta, chiusura in corso...")
    finally:
      
        live_check_task.cancel()
        midi_task.cancel()
        
        try:
            await live_check_task
        except asyncio.CancelledError:
            print("Il task del controllo live è stato cancellato.")

        try:
            await midi_task
        except asyncio.CancelledError:
            print("Il task di lettura MIDI è stato cancellato.")
        
        keyboard_led(outport, "delete")
        inport.close()
        outport.close()
        print("Connessioni MIDI chiuse.")

if __name__ == "__main__":

    try:
        asyncio.run(main())
    except asyncio.exceptions.CancelledError:
        print("Programma terminato")
    except KeyboardInterrupt:
        print("Programma terminato")