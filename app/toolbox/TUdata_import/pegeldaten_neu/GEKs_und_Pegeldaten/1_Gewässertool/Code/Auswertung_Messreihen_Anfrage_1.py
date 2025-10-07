# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 10:16:57 2024

@author: Vincent
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import linregress

#%% initialisieren
# Pfad zu deinem Ordner mit den CSV-Dateien
ordner_pfad = r"P:/Projekte/SpreeWasserN_1346/Daten/Dateneingang/TUB_Cloud/Hydrologie/Oberflaechengewaesser/WasserstÃ¤nde/Daten LfU/erste Anfrage/"
ergebnisse = [] # Liste zur Speicherung der Ergebnisse

#%% Durch alle CSV-Dateien im Ordner iterieren
for datei in os.listdir(ordner_pfad):
    if datei.endswith(".csv"):
        print(f"Verarbeite Datei: {datei}")
        datei_pfad = os.path.join(ordner_pfad, datei)
        
        # Lesen der Datei und Identifikation der Header-Zeile
        with open(datei_pfad, "r", encoding="latin1") as file:
            lines = file.readlines()
        
        # Metadaten aus den Kopfzeilen extrahieren
        messstellenname = None
        pkz = None
        header_index = None
        for i, line in enumerate(lines):
            if "Messstellenname" in line:
                messstellenname = line.split(":")[1].strip()
            if "Pegelkennziffer (PKZ)" in line:
                pkz = line.split(":")[1].strip()
            if "ETRS 89_3_Ost" in line:
                rechtswert = float(line.split(":")[1].strip())
            if "ETRS 89_3_Nord" in line:
                hochwert = float(line.split(":")[1].strip())                
            if line.strip().startswith("Datum"):
                header_index = i
                break  # Header gefunden, Schleife kann beendet werden
        
        # Sicherstellen, dass die Header-Zeile gefunden wurde
        if header_index is None:
            print(f"Kein gültiger Header in Datei: {datei}")
            continue
        
        print(f"Header-Zeile gefunden bei Zeile {header_index + 1}. Lese die Daten ab dieser Zeile.")
        
        # Einlesen der Daten ab der Header-Zeile
        daten = pd.read_csv(datei_pfad, skiprows=header_index, sep=";", encoding="latin1")
        
        print("Daten erfolgreich eingelesen. Verarbeite die Datumswerte.")
        
        # Konvertierung der Datums-Spalte
        daten["Datum"] = pd.to_datetime(daten["Datum"], format="%d.%m.%Y", errors="coerce")
        
        # Sicherstellen, dass Datum erfolgreich konvertiert wurde
        daten = daten.dropna(subset=["Datum"])
        
        if daten.empty:
            print(f"Keine gültigen Daten in Datei {datei}. Überspringe diese Datei.")
            continue
        
        # Versuche, die 'Wert[cm]' Spalte in numerische Werte umzuwandeln
        daten["Wert[cm]"] = pd.to_numeric(daten["Wert[cm]"], errors="coerce")
        
        # Entfernen von Zeilen mit ungültigen Werten (NaN)
        daten = daten.dropna(subset=["Wert[cm]"])
        
        print(f"Berechne die Dauer der Messreihe für Datei {datei}.")
        
        # Berechnung der Dauer der Messreihe
        startdatum = daten["Datum"].min()
        enddatum = daten["Datum"].max()
        dauer_tage = (enddatum - startdatum).days
        dauer_jahre = dauer_tage / 365.25
        
        # Berechnung von Minimalwert, Maximalwert und Mittelwert der Jahresmittelwerte für 2010-2019 und 1990-1999
        daten["Jahr"] = daten["Datum"].dt.year
        
        # Jahresmittelwerte berechnen
        jahresmittelwerte = daten.groupby("Jahr")["Wert[cm]"].mean()
        
        # Minimalwert und Maximalwert
        min_wert = daten["Wert[cm]"].min()
        max_wert = daten["Wert[cm]"].max()
        
        # Mittelwerte für 2010-2019 und 1990-1999
        jahresmittel_2010_2019 = jahresmittelwerte[(jahresmittelwerte.index >= 2010) & (jahresmittelwerte.index <= 2019)].mean()
        jahresmittel_1990_1999 = jahresmittelwerte[(jahresmittelwerte.index >= 1990) & (jahresmittelwerte.index <= 1999)].mean()
        
        # Wenn keine Daten für den Zeitraum 2010-2019 vorhanden sind, setze NaN
        if np.isnan(jahresmittel_2010_2019):
            jahresmittel_2010_2019 = 'NaN'
        
        # Standardabweichung
        std_abw = daten["Wert[cm]"].std()
        
        # Linearen Trend der Jahresmittelwerte für 2000-2019
        jahresmittel_2000_2019 = jahresmittelwerte[(jahresmittelwerte.index >= 2000) & (jahresmittelwerte.index <= 2019)]
        if len(jahresmittel_2000_2019) > 1:
            trend = linregress(jahresmittel_2000_2019.index.values, jahresmittel_2000_2019.values)
            trend_slope = trend.slope  # Steigung des Trends
        else:
            trend_slope = 'NaN'
        
        # Ergebnisse speichern
        ergebnisse.append({
            "Messstellenname": messstellenname,
            "Pegelkennziffer (PKZ)": pkz,
            "Rechtswert": rechtswert,
            "Hochwert": hochwert,
            "Dauer (Tage)": dauer_tage,
            "Dauer (Jahre)": dauer_jahre,
            "Startdatum": startdatum,
            "Enddatum": enddatum,
            "Min-Wert [cm]": min_wert,
            "Max-Wert [cm]": max_wert,
            "Mittelwert 2010-2019 [cm]": jahresmittel_2010_2019,
            "Mittelwert 1990-1999 [cm]": jahresmittel_1990_1999,
            "Standardabweichung [cm]": std_abw,
            "Trend-Slope 2000-2019": trend_slope

        })
        
        # Ausgabe von Zwischenergebnissen
        print(f"Dauer für {messstellenname} (PKZ {pkz}): {dauer_jahre:.2f} Jahre")
        print(f"Minimalwert: {min_wert:.2f} cm, Maximalwert: {max_wert:.2f} cm")
        print(f"Mittelwert 2010-2019: {jahresmittel_2010_2019}, Mittelwert 1990-1999: {jahresmittel_1990_1999:.2f} cm")
        print(f"Standardabweichung: {std_abw:.2f} cm")
        print(f"Trend-Slope 2000-2019: {trend_slope}")
        print(f"Startdatum: {startdatum}, Enddatum: {enddatum}")
    
    else:
        print(f"Überspringe nicht-CSV-Datei: {datei}")

#%% Kombinieren und speichern
# Kombiniere alle Ergebnisse in ein DataFrame
print("Kombiniere alle Ergebnisse in ein DataFrame.")
ergebnis_df = pd.DataFrame(ergebnisse)

# Pfad zum Speichern der CSV-Datei
speicher_pfad = r"P:\Projekte\SpreeWasserN_1346\Daten\Excel-Tabellen\Hydrologie\Wasserstände\Auswertung\Auswertung_Pegelstaende.csv"

# Ergebnis speichern
ergebnis_df.to_csv(speicher_pfad, sep="\t",index=False, encoding="utf-16")
print(f"Ergebnis gespeichert in '{speicher_pfad}'.")
print(ergebnis_df)
