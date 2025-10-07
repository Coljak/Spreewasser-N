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
import matplotlib.pyplot as plt
import re  # für die Bereinigung des Messstellennamens


#%% initialisieren
# Pfad zu deinem Ordner mit den CSV-Dateien
ordner_pfad = r"P:/Projekte/SpreeWasserN_1346/Daten/Dateneingang/TUB_Cloud/Hydrologie/Oberflaechengewaesser/WasserstÃ¤nde/Daten LfU/zweite Anfrage/"
ergebnisse = [] # Liste zur Speicherung der Ergebnisse

#%% Durch alle CSV-Dateien im Ordner iterieren
for datei in os.listdir(ordner_pfad):
    if datei.endswith(".csv"):
        print(f"Verarbeite Datei: {datei}")
        datei_pfad = os.path.join(ordner_pfad, datei)
        
        # Lesen der Datei und Identifikation der Header-Zeile
        with open(datei_pfad, "r", encoding="latin1") as file:
            lines = file.readlines()
        
        lines = [line.replace(';;;', '') for line in lines]
        lines = [line.replace(',', '.') for line in lines]

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
                rechtswert = float(line.split(":")[1].strip().replace(',','.'))
            if "ETRS 89_3_Nord" in line:
                hochwert = float(line.split(":")[1].strip().strip().replace(',','.'))             
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
        if "Wert [cm]" in daten.columns:
            daten["Wert[cm]"] = pd.to_numeric(daten["Wert [cm]"], errors="coerce")
            
        if "Relativer Wert [cm]" in daten.columns:
            daten["Wert[cm]"] = pd.to_numeric(daten["Relativer Wert [cm]"], errors="coerce")
        
        if "Aggregiertes Mittel [cm]" in daten.columns:
            daten["Wert[cm]"] = pd.to_numeric(daten["Aggregiertes Mittel [cm]"], errors="coerce")
            
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

        # Gruppieren nach Jahr und Monat und den Mittelwert berechnen
        monatsmittelwerte = daten.groupby(daten['Datum'].dt.to_period('M'))['Wert[cm]'].mean()
        monatsmittelwerte.index = monatsmittelwerte.index.to_timestamp()
        
        # Messstellennamen bereinigen (Sonderzeichen entfernen)
        messstellenname_bereinigt = re.sub(r'[^\w\s]', '', messstellenname)  # Alle Sonderzeichen ersetzen
        messstellenname_bereinigt = messstellenname_bereinigt.replace(' ', '_')  # Leerzeichen durch Unterstriche ersetzen

        # Plotten der Monatsmittelwerte
        plt.figure(figsize=(12, 6))
        plt.plot(monatsmittelwerte.index, monatsmittelwerte.values, marker='o', linestyle='', label='Monatsmittelwerte')
        plt.title(f'Pegel {messstellenname_bereinigt} \n PKZ: {pkz}', fontsize=16)
        plt.xlabel('Monat', fontsize=14)
        plt.ylabel('Wert [cm]', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.show()
        # Pfad zum Speichern des Plots
        
        # Dynamischer Dateiname erstellen
        startdatum_str = startdatum.strftime('%Y-%m-%d').replace('-', '_')
        enddatum_str = enddatum.strftime('%Y-%m-%d').replace('-', '_')
        
        dateiname = f"{messstellenname_bereinigt}_{pkz}_{startdatum_str}_bis_{enddatum_str}.png"
        dateiname_bereinigt= dateiname.replace(' ', '_')
        save_path = rf"P:\Projekte\SpreeWasserN_1346\Daten\Excel-Tabellen\Hydrologie\Wasserstände\Auswertung\Plots\{dateiname_bereinigt}"

        plt.savefig(save_path, dpi=300, bbox_inches='tight')  # Speichert den Plot mit hoher Auflösung
        plt.close()  # Schließt den Plot, um Speicher zu sparen
        print(f"Plot wurde erfolgreich gespeichert unter: {save_path}")

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
            "Messstellenname": messstellenname_bereinigt,
            "PKZ": pkz,
            "RW_m": rechtswert,
            "HW_m": hochwert,
            "T_d": dauer_tage,
            "T_a": dauer_jahre,
            "Startdate": startdatum,
            "Enddatum": enddatum,
            "Min_cm": min_wert,
            "Max_cm": max_wert,
            "MW_2010_2019_cm": jahresmittel_2010_2019,
            "MW_1990-1999 [cm]": jahresmittel_1990_1999,
            "Stdev [cm]": std_abw,
            "Trend-Slope 2000-2019": trend_slope,
            "Dateiname": dateiname_bereinigt

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
    print('***************************************')
#%% Kombinieren und speichern
# Kombiniere alle Ergebnisse in ein DataFrame
print("Kombiniere alle Ergebnisse in ein DataFrame.")
ergebnis_df = pd.DataFrame(ergebnisse)

# Pfad zum Speichern der CSV-Datei
speicher_pfad = r"P:\Projekte\SpreeWasserN_1346\Daten\Excel-Tabellen\Hydrologie\Wasserstände\Auswertung\Auswertung_Pegelstaende_2.csv"

# Ergebnis speichern
ergebnis_df.to_csv(speicher_pfad, sep="\t",index=False, encoding="utf-16")
print(f"Ergebnis gespeichert in '{speicher_pfad}'.")
print(ergebnis_df)
