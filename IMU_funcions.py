### Bibliotheken
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


### Landen Peaks laden
def load_landing_peaks_for_subject(csv_path, subject_letter):
    """
    Lädt die LandingTimes aus einer CSV-Datei und erstellt ein Dictionary für ein bestimmtes Subjekt (A, B, C, D).
    """

    df = pd.read_csv(csv_path)                  # Einlesen der CSV-Datei mit Landing Peaks

    landing_peaks = {}                          # Dictionary für Landing Peaks initialisieren

    for _, row in df.iterrows():                # Iteration über jede Zeile der DataFrame
        filename = row["Filename"]              # Dateiname aus der Zeile extrahieren
        landing_time = row["LandingTime_s"]

        # Nur Dateien des gewünschten Subjekts berücksichtigen
        if f"_{subject_letter}_" in filename:                   # Beispiel: "Pre_A_Li_1.csv" --> Teile in ["Pre", "A", "Li", "1.csv"]
            parts = filename.replace(".csv", "").split("_")
            if len(parts) == 4:
                phase, _, side, number = parts
                key = f"{side}_{number}_{phase}"                # Erstellen des Schlüssels im Format "Li_1_Pre"
                landing_peaks[key] = round(landing_time, 3)     # auf 3 Nachkommastellen runden

    return landing_peaks


### Funktionen Datei struktur
def Data_structure (C_Daten_file_map, landing_peaks, columns_to_extract):
    """
    Gibt die Datenstruktur zurück, die alle relevanten Daten enthält.
    """
    data = {}

    for key, filepath in C_Daten_file_map.items():
        df = pd.read_csv(filepath, delimiter=';', encoding='utf-8', decimal=',', skiprows=3)
        df["time"] = df["time"] - df["time"].iloc[0]

        # Peak-Zeit ermitteln
        peak_time = landing_peaks[key]
        cutoff_time = peak_time + 3.0           

        # Filter anwenden: alle Zeilen bis 3 Sekunden nach Peak
        df = df[df["time"] <= cutoff_time].reset_index(drop=True)

        # Relevante Spalten auswählen
        df_selected = df[columns_to_extract].copy()

        # In Datenstruktur speichern
        data[key] = {
            "df": df_selected,
            "landing_peak_time": peak_time
        }
    
    return data


### Plot parameter festlegen
def get_keys_and_direction(seite, phase):
    """
    Gibt die relevanten Keys und die Richtung (RT oder LT) für die angegebene Seite und Phase zurück.
    """

    if seite not in ("LT", "RT"):
        raise ValueError("Seite muss 'LT' oder 'RT' sein.")
    if phase not in ("Pre", "Post"):
        raise ValueError("Phase muss 'Pre' oder 'Post' sein.")

    keys_map = {
        ("RT", "Pre"): ["Re_1_Pre", "Re_2_Pre", "Re_3_Pre"],
        ("LT", "Pre"): ["Li_1_Pre", "Li_2_Pre", "Li_3_Pre"],
        ("RT", "Post"): ["Re_1_Post", "Re_2_Post", "Re_3_Post"],
        ("LT", "Post"): ["Li_1_Post", "Li_2_Post", "Li_3_Post"]
    }

    keys = keys_map[(seite, phase)]
    direction = seite  # 'RT' oder 'LT'

    return keys, direction


### Farben für die Plots
def get_colors():
    """
    Gibt eine Liste von Farben für die Plots zurück.
    """
    colors = ['blue', 'red', 'green']
    color_peak = 'black'
    color_stable = 'grey'

    return colors, color_peak , color_stable 


### Stabilen Zeitpunkt finden
def find_stable_time(time, signal, peak_time, slope_threshold, min_consecutive):
    """
    Gibt den ersten Zeitpunkt zurück, ab dem die Steigung für `min_consecutive` Punkte
    in Folge unterhalb `slope_threshold` bleibt.
    """
    # Nur Daten nach dem Peak betrachten
    mask = time > peak_time
    time_post = time[mask].reset_index(drop=True)           # zeit mit maske filtern und Index zurücksetzen
    signal_post = signal[mask].reset_index(drop=True)       # Signal mit maske filtern und Index zurücksetzen

    if len(time_post) < min_consecutive:                    # Wenn nicht genug Datenpunkte nach dem Peak vorhanden sind
        return np.nan

    # Steigungen berechnen
    slopes = np.gradient(signal_post, time_post)            # Berechnung der Steigung des Signals (steigung pro sekunde)        
    is_stable = np.abs(slopes) < slope_threshold            # Überprüfen, ob die Steigung unter dem Schwellenwert liegt --> dann steigung klein genug und stabil (Boolean Array)

    # Finde erste Phase mit `min_consecutive` stabilen Werten
    count = 0
    for i in range(len(is_stable)):
        if is_stable[i]:                                    # Wenn is_stable[i] True ist, dann ist die Steigung unterhalb des Schwellenwerts und count erhöhen
            count += 1
            if count >= min_consecutive:                    # Stabiler Zeitpunkt gefunden weil count >= min_consecutive  
                # Index am Anfang des stabilen Fensters
                window_start_index = i - min_consecutive + 1 # erstes Element des stabilen Fensters
                return time_post[window_start_index]         # Rückgabe des Zeitpunkts des stabilen Fensters in "time"
        else:
            count = 0                                       # Wenn die Steigung nicht stabil ist, Zähler zurücksetzen

    return np.nan

### Funktion für Boxplots
def plot_boxplot(DATA, title, y_label, data_key, folder_pictures_):
    """
    Erstellt Boxplots für die Zeitdifferenzen zwischen den Seiten und Phasen.
    """
    # Liste für DataFrame-Zeilen
    rows = []

    for key, values in DATA.items():
        if data_key in values and not np.isnan(values[data_key]):
            side = "Li" if key.startswith("Li") else "Re"
            phase = "Pre" if "Pre" in key else "Post"
            rows.append({
                "key": key,
                "side": side,
                "phase": phase,
                data_key: values[data_key]
            })

    df_plot = pd.DataFrame(rows)

    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df_plot[df_plot["phase"] == "Pre"], x="side", y=data_key)
    plt.title(title + "Links vs. Rechts (Pre)")
    plt.ylabel(y_label)
    plt.xlabel("Bein")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(folder_pictures_ + data_key + "zeitdifferenz_pre_link_rechts.png", dpi=300)
    plt.show()

    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df_plot[df_plot["phase"] == "Post"], x="side", y=data_key)
    plt.title(title + "Links vs. Rechts (Post)")
    plt.ylabel(y_label)
    plt.xlabel("Bein")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(folder_pictures_ + data_key + "zeitdifferenz_post_link_rechts.png", dpi=300)
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_plot, x="phase", y=data_key, hue="side")
    plt.title(title + "Pre vs. Post (Links & Rechts)")
    plt.ylabel(y_label)
    plt.xlabel("Phase")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Bein")
    plt.tight_layout()
    plt.savefig(folder_pictures_ + data_key + "zeitdifferenz_pre_post_link&rechts.png", dpi=300)
    plt.show()


### Funktion zur Berechnung der Standardabweichung nach stabilem Zeitpunkt
def calculate_std_post_stable(data, keys, RT_joint, LT_joint, window_seconds=3.0):
    """
    Berechnet die Standardabweichung des Sprunggelenks nach dem stabilen Zeitpunkt 
    und speichert sie als EINZELWERT in der Datenstruktur.

    """
    for key in keys:
        df = data[key]["df"]
        time = df["time"]
        stable_time = data[key]["stable_time"]

        # Gelenkwinkel je nach Seite wählen
        if key.startswith("Re"):
            joint = RT_joint
        elif key.startswith("Li"):
            joint = LT_joint


        if joint not in df.columns:
            std_value = np.nan
        else:
            # Signal nach stable_time im definierten Zeitfenster
            mask = (time >= stable_time) & (time <= stable_time + window_seconds)   # Zeitfenster von 3 Sekunden nach dem stabilen Zeitpunkt
            signal = df[joint][mask]
            std_value = np.std(signal)

        # Als einzelner Wert speichern
        data[key]["std von " + joint[3:]] = std_value       # als "std von Ankle Dorsiflexion (deg)"



### Funkktion zum Berechnen des Durchschnitts
def calculate_mean_stable_time(DATA, KEYS, Parameter):
    """
    Berechnet den Durchschnitt des Parameters für die angegebenen Keys.
    """
    re_pre = []
    re_post = []
    li_pre = []
    li_post = []

    for key in KEYS:
        if key.startswith("Re"):
            if "Pre" in key:
                re_pre.append(key)
            elif "Post" in key:
                re_post.append(key)
        elif key.startswith("Li"):
            if "Pre" in key:
                li_pre.append(key)
            elif "Post" in key:
                li_post.append(key)

    # Durchschnittliche stabile Zeiten berechnen
    re_pre_mean = np.mean([DATA[key][Parameter] for key in re_pre ])
    re_post_mean = np.mean([DATA[key][Parameter] for key in re_post ])
    li_pre_mean = np.mean([DATA[key][Parameter] for key in li_pre ])
    li_post_mean = np.mean([DATA[key][Parameter] for key in li_post ])

    return re_pre_mean, re_post_mean, li_pre_mean, li_post_mean


### Werte der Tabelle in CSV-Datei schreiben
def write_time_differences_to_csv(csv_path, re_pre, re_post, li_pre, li_post, Person):
    """
    Speichert die vier Mittelwerte der Time Difference in eine CSV-Datei.
    """

    # Neue Daten vorbereiten
    new_data = {
        "Sprünge": [Person + "_Re_Pre", Person + "_Re_Post", Person + "_Li_Pre", Person + "_Li_Post"],
        "Time Difference": [re_pre, re_post, li_pre, li_post]
    }

    new_df = pd.DataFrame(new_data)

    # Bestehende Datei lesen, wenn sie existiert
    
    existing_df = pd.read_csv(csv_path, sep=";", encoding="utf-8", decimal=",")
        
        # Überschreibe nur die Zeilen mit gleichen "Sprünge"-Werten oder hänge an
    for i, row in new_df.iterrows():
        if row["Sprünge"] in existing_df["Sprünge"].values:
                existing_df.loc[existing_df["Sprünge"] == row["Sprünge"], "Time Difference"] = row["Time Difference"]
        else:
                existing_df = pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True)


    # Speichern
    existing_df.to_csv(csv_path, sep=";", index=False, encoding="utf-8", decimal=",")
    print(f"✅ Werte wurden in '{csv_path}' gespeichert.")