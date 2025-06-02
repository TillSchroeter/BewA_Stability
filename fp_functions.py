import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as signal

def load_force_data(filepath):
    """
    Lädt CSV-Daten einer Kraftmessplatte, korrigiert den Zeitoffset 
    und extrahiert GRF-Komponenten.

    Parameters:
    - filepath (str): Pfad zur CSV-Datei

    Returns:
    - time (pd.Series): Zeitreihe (bei 0 beginnend)
    - grf_x (pd.Series): GRF in x-Richtung
    - grf_y (pd.Series): GRF in y-Richtung
    - grf_z (pd.Series): GRF in z-Richtung
    """
    df = pd.read_csv(filepath, delimiter=';', encoding='utf-8', decimal=',', skiprows=3)
    time = df["time"]
    time = time - time.iloc[0]  # Offset entfernen

    grf_x = df["Force plate group-Ground reaction force-x (N)"]
    grf_y = df["Force plate group-Ground reaction force-y (N)"]
    grf_z = df["Force plate group-Ground reaction force-z (N)"]

    return time, grf_x, grf_y, grf_z
