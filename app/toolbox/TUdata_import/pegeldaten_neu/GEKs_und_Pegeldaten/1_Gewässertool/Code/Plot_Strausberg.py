# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 08:45:19 2024

@author: Vincent
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

#%% Import Data
# Path to your CSV file
file_path = "P:/Projekte/SpreeWasserN_1346/Daten/Dateneingang/TUB_Cloud/Hydrologie/Oberflaechengewaesser/WasserstÃ¤nde/Daten LfU/zweite Anfrage/Strausberg,FÃ¤hre_5860200_W_TagWerte.csv"
df = pd.read_csv(file_path, sep=";", skiprows=lambda x: x < 12, encoding="ISO-8859-1")
df['DateTime'] = pd.to_datetime(df['Datum'], dayfirst=True)

# Set the new DateTime column as the index and drop the original 'Datum' and 'Uhrzeit' columns
df.set_index('DateTime', inplace=True)
df.drop(columns=['Datum', 'Uhrzeit'], inplace=True)

# Convert "Wert_cm" to numeric, in case it has any non-numeric entries
df['Wert [cm]'] = pd.to_numeric(df['Wert [cm]'], errors='coerce')

# Display basic information and the first few rows
print(df.info())
print(df.head())

# Example analysis: Calculate basic statistics
print("\nStatistics for Water Level Data (Wert_cm):")
print(df['Wert [cm]'].describe())

# Calculate the duration of the time series in years
time_span = (df.index[-1] - df.index[0]).days / 365.25
print(f"Duration of the time series: {time_span:.2f} years")

# Calculate annual mean values
annual_mean = df['Wert [cm]'].resample('Y').mean()

# Dekadenweise Mittelwerte berechnen und nur den Mittelwert pro Dekade auswählen
decadal_mean = annual_mean.resample('10Y').mean()
# Spaltennamen anpassen, um das Format wie "H_mean_80", "H_mean_90", etc. zu erreichen
decadal_mean.columns = ["H_mean"]
decadal_mean.index = [f"H_mean_{str(year)[:3]}0" for year in decadal_mean.index.year]

# Ergebnis transponieren, um Jahrzehnte als Spaltenköpfe zu haben
decadal_mean_transposed = decadal_mean.T

# Ergebnis anzeigen
print(decadal_mean_transposed)

#%% Plotting the annual mean values
plt.close('all')
plt.figure(figsize=(10, 6))
plt.plot(annual_mean.index.year, annual_mean.values, marker='o', linestyle='-', color='b', label='Annual Mean Water Level (cm)')
plt.xlabel('Year')
plt.ylabel('Water Level (cm)')
end=df.index[-1]
plt.title(f'Annual Mean Water Levels at Strausberg, Fähre, end of data: {end}')
plt.legend()
plt.grid()
plt.show()

# Define the directory and filename for saving the plot
save_dir = "P:/Projekte/SpreeWasserN_1346/Daten/Excel-Tabellen/Hydrologie/Wasserstände/Abbildungen"
base_filename = os.path.splitext(os.path.basename(file_path))[0]  # Extracts the base name without extension
save_path = os.path.join(save_dir, f"{base_filename}_Annual_Mean_Water_Level.png")

# Save the plot
plt.savefig(save_path, dpi=300)  # Save the plot with high resolution

#%% Plot time series
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Wert_cm'], label='Water Level (cm)', color='b')
plt.xlabel('Date')
plt.ylabel('Water Level (cm)')
plt.title('Water Level Measurement at Strausberg, Fähre')
plt.legend()
plt.show()
