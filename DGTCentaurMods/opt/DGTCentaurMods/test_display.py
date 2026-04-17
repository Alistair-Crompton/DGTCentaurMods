import sys
import os
import time
from PIL import Image, ImageDraw

# Pfad zu den Klassen hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

def run_test(driver_name):
    print(f"\n--- Starte Test für Treiber: {driver_name.upper()} ---")
    try:
        if driver_name == "v1":
            from waveshare import epd2in9 as driver
            epd = driver.EPD()
            print("Initialisiere V1 (Full Update)...")
            epd.init(epd.lut_full_update)
        elif driver_name == "v2":
            from waveshare import epd2in9_V2 as driver
            epd = driver.EPD()
            print("Initialisiere V2...")
            epd.init()
        elif driver_name == "d":
            from waveshare import epd2in9d as driver
            epd = driver.EPD()
            print("Initialisiere D (Standard)...")
            epd.init()
        else:
            print("Unbekannter Treiber-Name!")
            return

        print("Lösche Display (Clear 0xFF)...")
        epd.Clear(0xFF)
        
        print("Erstelle Testbild...")
        # Weißes Bild erstellen
        image = Image.new('1', (epd.width, epd.height), 255) 
        draw = ImageDraw.Draw(image)
        
        # Einen Rahmen und Text zeichnen
        draw.rectangle((5, 5, epd.width-5, epd.height-5), outline=0)
        draw.text((20, 100), f"CENTAUR {driver_name.upper()}", fill=0)
        draw.text((20, 130), "TEST ERFOLGREICH!", fill=0)
        
        print("Übertrage Bild an Display...")
        epd.display(epd.getbuffer(image))
        
        print("Warte 10 Sekunden (Bild sollte jetzt sichtbar sein)...")
        time.sleep(10)
        
        print("Versetze Display in Deep Sleep...")
        epd.sleep()
        print("Test beendet.")
        
    except Exception as e:
        print(f"FEHLER bei Treiber {driver_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_test(sys.argv[1].lower())
    else:
        print("\nBitte Treiber angeben!")
        print("Nutzung: python3 test_display.py [v1|v2|d]")
        print("Beispiel: python3 test_display.py v1")
