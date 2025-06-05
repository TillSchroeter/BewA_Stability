import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import interp1d

# Einlesen der CSV-Daten und Rückgabe der Zeitreihe, vertikalen GRF und CoP x/y

def load_force_data(filepath):
    df = pd.read_csv(filepath, delimiter=';', encoding='utf-8', decimal=',', skiprows=3, low_memory=False)
    time = df["time"] - df["time"].iloc[0]
    grf_z = df["Force plate group-Ground reaction force-z (N)"]
    cop_x = df["Force plate group-Center of pressure-x (mm)"]
    cop_y = df["Force plate group-Center of pressure-y (mm)"]
    return time, grf_z, cop_x, cop_y

# Detektion der Landezeitpunkte (Peaks) über GRF > 2× Körpergewicht

def detect_landing_peaks(grf_z, time, mass, g=9.81):
    threshold = 2 * mass * g
    peaks, _ = find_peaks(grf_z, height=threshold)
    return peaks

# Speichern der Landezeitpunkte als CSV-Datei

def save_peak_times(results, output_file="landing_peaks.csv"):
    df = pd.DataFrame(results, columns=["Filename", "LandingTime_s"])
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✅ Landezeitpunkte gespeichert in: {output_file}")

# Normalisierung von Signalwerten ab dem Landepeak

def normalize_from_peak(signal, peak_index):
    return signal[peak_index:] - signal[peak_index]

# Zeitachse von Peak zu 0 setzen und auf 100 % normieren

def normalize_time_from_peak(time, peak_index):
    t = time[peak_index:] - time[peak_index]
    return t / t.max() * 100

# Interpolation der Signale auf 100 gleichverteilte Zeitpunkte

def resample_to_100(time, signal):
    f = interp1d(time, signal, kind='linear', fill_value='extrapolate')
    time_uniform = np.linspace(0, 100, 100)
    return f(time_uniform)

# Berechnung von Mittelwert, Minimum, Maximum und RMS eines Signals

def compute_cop_metrics(signal):
    mean = np.mean(signal)
    max_ = np.max(signal)
    min_ = np.min(signal)
    rms = np.sqrt(np.mean((signal - mean) ** 2))
    return mean, max_, min_, rms

# Plotten und Speichern der CoP-Signale (je 3 Sprüngen pro Zustand)

def plot_cop_signals(signals, times, colors, title_prefix, rms_values, ylabel, person_label):
    ymin = min([s.min() for s in signals]) - 5
    ymax = max([s.max() for s in signals]) + 5

    plt.figure(figsize=(15, 4))
    for i in range(3):
        plt.subplot(1, 3, i + 1)
        plt.plot(times[i], signals[i], color=colors[i], label=f'CoP {ylabel} {i+1}')
        mean, max_, min_, _ = compute_cop_metrics(resample_to_100(times[i], signals[i]))
        plt.axhline(y=mean, color=colors[i], linestyle='--', label='Mean')
        plt.axhline(y=max_, color=colors[i], linestyle=':', label='Max')
        plt.axhline(y=min_, color=colors[i], linestyle=':', label='Min')
        plt.title(f'Sprung {i+1} – RMS: {rms_values[i]:.2f}')
        plt.xlabel('Time / %')
        plt.ylabel(f'CoP {ylabel} / mm')
        plt.ylim(ymin, ymax)
        plt.grid()
        plt.legend()

        plt.tight_layout()
        title_parts = title_prefix.split()
        testphase = title_parts[0] 
        side = "Links" if "Li" in title_prefix else "Rechts"
        cop_label = f"CoP ({ylabel})"
        suptitle_text = f"Person {person_label} – {testphase} {side} {cop_label} – ⌀ RMS: {np.mean(rms_values):.2f}"
        plt.suptitle(suptitle_text, fontsize=12, y=0.96)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        os.makedirs("Plot_Bilder_CoP", exist_ok=True)
        filename = f"{person_label}_{title_prefix.replace(' ', '_')}_cop_{ylabel}.png"
        filepath = os.path.join("Plot_Bilder_CoP", filename)
        #plt.savefig(filepath, bbox_inches='tight', dpi=300)
        # plt.show()

# Verarbeitung und Visualisierung eines CoP-Datensatzes

def process_cop_set(cop_signals, time_signals, peak_indices, label, person):
    ylabel = 'x' if 'CoP X' in label else 'y'
    signals_norm = [normalize_from_peak(cop, peak) for cop, peak in zip(cop_signals, peak_indices)]
    times_norm = [normalize_time_from_peak(t, peak) for t, peak in zip(time_signals, peak_indices)]
    signals_100 = [resample_to_100(tn, sn) for tn, sn in zip(times_norm, signals_norm)]
    metrics = [compute_cop_metrics(s100) for s100 in signals_100]
    rms_values = [m[3] for m in metrics]
    plot_cop_signals(signals_norm, times_norm, ['blue', 'red', 'green'], label, rms_values, ylabel=ylabel, person_label=person)
    return rms_values

# -----------------------------
personen = {
    "A": 70,
    "B": 77,
    "C": 78,
    "D": 50
}

conditions = ["Pre", "Post"]
sides = ["Li", "Re"]
spruenge = ["1", "2", "3"]

landing_results = []
cop_rms_summary = []

for person, mass in personen.items():
    base_dir = f"{person}_Daten"
    print(f"\n===== Auswertung für Person {person} (Gewicht: {mass} kg) =====")

    for condition in conditions:
        for side in sides:
            times = []
            grfs = []
            copx = []
            copy = []
            peaks = []

            for nr in spruenge:
                filename = f"{condition}_{person}_{side}_{nr}.csv"
                filepath = os.path.join(base_dir, filename)

                try:
                    time, grf_z, cop_x, cop_y = load_force_data(filepath)
                    detected_peaks = detect_landing_peaks(grf_z, time, mass)
                    if len(detected_peaks) == 0:
                        print(f"⚠️ Kein Peak in Datei {filename} erkannt.")
                        continue

                    peak_index = detected_peaks[0]
                    landing_time = time[peak_index]
                    landing_results.append([filename, landing_time])

                    times.append(time)
                    grfs.append(grf_z)
                    copx.append(cop_x)
                    copy.append(cop_y)
                    peaks.append(peak_index)

                except Exception as e:
                    print(f"❌ Fehler bei Datei {filename}: {e}")

            if len(peaks) < 3:
                print(f"⚠️ Nicht genug gültige Sprünge für {condition}-{side} bei {person}")
                continue

            print(f"\n🔹 {condition}-{side} – CoP X")
            rms_x = process_cop_set(copx, times, peaks, f"{condition}-Testung {side} CoP X", person)

            print(f"\n🔹 {condition}-{side} – CoP Y")
            rms_y = process_cop_set(copy, times, peaks, f"{condition}-Testung {side} CoP Y", person)

            avg_rms_x = np.mean(rms_x)
            avg_rms_y = np.mean(rms_y)
            rms_norm = np.sqrt(avg_rms_x ** 2 + avg_rms_y ** 2)

            kombi_label = f"{person}_{side}_{condition}"
            cop_rms_summary.append([kombi_label, rms_norm])

save_peak_times(landing_results)

# Speichern der normierten RMS-Werte
rms_df = pd.DataFrame(cop_rms_summary, columns=["Kombination", "RMS_norm"])
rms_df["RMS_norm"] = rms_df["RMS_norm"].map(lambda x: f"{x:.2f}".replace(".", ","))
rms_df.to_csv("cop_rms_normiert.csv", index=False, sep=";", encoding="utf-8")
print("\n✅ Normierte RMS-Werte gespeichert in: cop_rms_normiert.csv")
