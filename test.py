import PyATEMMax


switcher = PyATEMMax.ATEMMax()

found = False

for i in range(1, 255):
    ip = f"192.168.1.{i}"

    print(f"Checking {ip}", end="\r")

    switcher.ping(ip)

    if switcher.waitForConnection(
        infinite=False,
        waitForFullHandshake=False
    ):
        print(f"\nATEM switcher found at {ip}")
        found = True
        break

    switcher.disconnect()


if not found:
    print("\nATEM switcher not found")
    switcher.disconnect()
    exit()


# Il ping ha già stabilito la connessione.
# Non facciamo switcher.connect(ip)!

# Aspettiamo che lo stato iniziale sia disponibile
switcher.waitForConnection()

print("PVW:", switcher.previewInput[0].videoSource.value)
print("PGM:", switcher.programInput[0].videoSource.value)


try:
    while True:
        pgm = switcher.programInput[0].videoSource
        pvw = switcher.previewInput[0].videoSource

        print(
            f"PVW: {pvw.name} ({pvw.value}) | "
            f"PGM: {pgm.name} ({pgm.value})"
        )

except KeyboardInterrupt:
    print("\nChiusura...")

finally:
    switcher.disconnect()
