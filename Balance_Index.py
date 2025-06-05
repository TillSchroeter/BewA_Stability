import pandas as pd
import numpy as np

def normalize_series(series):
    """Min-Max-Normalisierung einer Pandas Series"""
    min_val = series.min()
    max_val = series.max()
    if min_val == max_val:
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)

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
