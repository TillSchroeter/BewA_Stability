import pandas as pd
import numpy as np

# Funktion zur Min, Max Normalisierung einer Serie
def normalize_series(series):

    min_val = series.min()
    max_val = series.max()
    if min_val == max_val:
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)


# Funktion zur Berechnung des Balance Index aus RMS und Zeitdifferenz
def compute_balance_index_from_dataframes(df_time, df_rms, output_path=None):
    # Spaltennamen vereinheitlichen
    df_time = df_time.rename(columns={"Sprünge": "Key"})
    df_rms = df_rms.rename(columns={"Kombination": "Key"})

    # Zusammenführen über "Key"
    df = pd.merge(df_time, df_rms, on="Key", how="inner")

    # Normalisierung
    df["Time_norm"] = normalize_series(df["Time Difference"])
    df["RMS_normed"] = normalize_series(df["RMS_norm"])

    # Balance-Index berechnen
    df["Balance_Index"] = np.sqrt(df["Time_norm"]**2 + df["RMS_normed"]**2)
    # df["Balance_Index"] = normalize_series(df["Balance_Index"])  # optional nochmal normalisieren

    # Speichern
    if output_path:
        df.to_csv(output_path, sep=';', decimal=',', index=False)

    return df[["Key", "Time Difference", "RMS_norm", "Balance_Index"]]



# CSV-Dateien einlesen
df_time = pd.read_csv("Time_Difference.csv", sep=';', decimal=',')
df_rms = pd.read_csv("cop_rms_normiert.csv", sep=';', decimal=',')

# Balance Index berechnen
result_df = compute_balance_index_from_dataframes(df_time, df_rms)
# Ergebnis auf 2 Dezimalstellen runden
result_df = result_df.round(2)

# Ergebnis anzeigen
print(result_df)

# Ergebnis in eine CSV-Datei speichern
result_df.to_csv("Balance_Index.csv", sep=';', decimal=',', index=False)




print ("--------------------------------------------------------------")




### Mitteln der Balance Indexe über rechts und links für Pre und Post. Und printen ohne speichern
# Spalte "Person_Phase" aus Key extrahieren → z. B. "A_Pre"
def extract_person_phase(key):
    parts = key.split("_")
    return f"{parts[0]}_{parts[2]}"

# Neue Spalte für Gruppierung erzeugen
result_df["Person_Phase"] = result_df["Key"].apply(extract_person_phase)

# Mitteln über Balance_Index pro Person und Phase (Li + Re zusammengefasst)
summary_df = result_df.groupby("Person_Phase")["Balance_Index"].mean().reset_index()

# Auf 2 Nachkommastellen runden
summary_df["Balance_Index"] = summary_df["Balance_Index"].round(2)

# Ausgabe
print(summary_df)




