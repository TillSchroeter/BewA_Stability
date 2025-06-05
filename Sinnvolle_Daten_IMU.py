import pandas as pd
df = pd.read_csv("C_Daten/Pre_C_Re_3.csv",delimiter=';',encoding='utf-8',decimal=',', skiprows=3)  # 👈 Wichtig: Komma als Dezimaltrennzeichen

### Gelenkswinkel-Spalten
# Gelenkwinkel – linkes Bein
lt_hip_flexion = df["LT Hip Flexion (deg)"]
lt_hip_abduction = df["LT Hip Abduction (deg)"]
lt_hip_rotation_ext = df["LT Hip Rotation Ext (deg)"]
lt_knee_abduction = df["LT Knee Abduction (deg)"]
lt_knee_rotation_ext = df["LT Knee Rotation Ext (deg)"]
lt_knee_flexion = df["LT Knee Flexion (deg)"]
lt_knee_extension = df["Noraxon MyoMotion-Joints-Knee LT-Extension (deg)"]
lt_ankle_dorsiflexion = df["LT Ankle Dorsiflexion (deg)"]
lt_ankle_abduction = df["LT Ankle Abduction (deg)"]
lt_ankle_inversion = df["LT Ankle Inversion (deg)"]

# Gelenkwinkel – rechtes Bein
rt_hip_flexion = df["RT Hip Flexion (deg)"]
rt_hip_abduction = df["RT Hip Abduction (deg)"]
rt_hip_rotation_ext = df["RT Hip Rotation Ext (deg)"]
rt_knee_abduction = df["RT Knee Abduction (deg)"]
rt_knee_rotation_ext = df["RT Knee Rotation Ext (deg)"]
rt_knee_flexion = df["RT Knee Flexion (deg)"]
rt_knee_extension = df["Noraxon MyoMotion-Joints-Knee RT-Extension (deg)"]
rt_ankle_dorsiflexion = df["RT Ankle Dorsiflexion (deg)"]
rt_ankle_abduction = df["RT Ankle Abduction (deg)"]
rt_ankle_inversion = df["RT Ankle Inversion (deg)"]

# Torso-Pelvis-Winkel
torso_pelvic_flexion_fwd = df["Torso-Pelvic Flexion Fwd (deg)"]

lt_torso_pelvic_flexion_lat = df["LT Torso-Pelvic Flexion Lat (deg)"]
lt_torso_pelvic_axial = df["LT Torso-Pelvic Axial (deg)"]
rt_torso_pelvic_flexion_lat = df["RT Torso-Pelvic Flexion Lat (deg)"]
rt_torso_pelvic_axial = df["RT Torso-Pelvic Axial (deg)"]

upper_spine_tilt_fwd = df["Noraxon MyoMotion-Segments-Upper spine-Tilt Fwd (deg)"]
upper_spine_roll = df["Noraxon MyoMotion-Segments-Upper spine-Roll (deg)"]
lt_upper_spine_tilt_lat = df["Noraxon MyoMotion-Segments-Upper spine-LT Tilt Lat (deg)"]
rt_upper_spine_tilt_lat = df["Noraxon MyoMotion-Segments-Upper spine-RT Tilt Lat (deg)"]
lt_upper_spine_rotation = df["Noraxon MyoMotion-Segments-Upper spine-LT Rotation (deg)"]
rt_upper_spine_rotation = df["Noraxon MyoMotion-Segments-Upper spine-RT Rotation (deg)"]