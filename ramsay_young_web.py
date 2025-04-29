
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

# Constants
R = 8.314  # J/mol·K
atm_pressure = 760  # mmHg (fixed atmospheric pressure)

# Antoine equation constants for water
A = 8.07131
B = 1730.63
C = 233.426

def boiling_point_from_pressure(pressure_mmHg):
    # Antoine equation rearranged to solve for T (in °C)
    return (B / (A - math.log10(pressure_mmHg))) - C

# Streamlit UI
st.image("ramsay_young.png", caption="Ramsay and Young Apparatus", use_column_width=True)
st.title("Ramsay-Young Simulator for Water")
st.markdown("**Control Inlet Pressure to Determine Boiling Points Automatically**")

if "data" not in st.session_state:
    st.session_state.data = []

inlet_pressure = st.sidebar.number_input("Set Inlet Pressure (mmHg)", min_value=100.0, max_value=760.0, value=750.0, step=1.0)

delta_h = atm_pressure - inlet_pressure  # mmHg
display_pressure = inlet_pressure  # corrected pressure inside the system

boiling_temp = boiling_point_from_pressure(display_pressure)

st.metric(label="Difference in Manometer Height (mmHg)", value=f"{delta_h:.2f}")
st.metric(label="Corrected Pressure (mmHg)", value=f"{display_pressure:.2f}")
st.metric(label="Boiling Temperature (°C)", value=f"{boiling_temp:.2f}")

if st.button("Add Data Point"):
    # Save 1/T vs ln(P) for plotting later
    st.session_state.data.append({
        "Pressure (mmHg)": display_pressure,
        "Boiling Temperature (°C)": boiling_temp
    })

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.write("### Collected Data", df)

    # Prepare for Clausius-Clapeyron plot
    df["1/T (1/K)"] = 1 / (df["Boiling Temperature (°C)"] + 273.15)
    df["ln(P)"] = np.log(df["Pressure (mmHg)"])

    fig, ax = plt.subplots()
    ax.scatter(df["1/T (1/K)"], df["ln(P)"], color='blue')
    ax.set_xlabel("1/T (1/K)")
    ax.set_ylabel("ln(P)")
    ax.set_title("Clausius-Clapeyron Plot")
    st.pyplot(fig)

    # Linear fit to find slope = -ΔHvap/R
    slope, intercept = np.polyfit(df["1/T (1/K)"], df["ln(P)"], 1)
    delta_H_vap = -slope * R / 1000  # kJ/mol

    st.success(f"Estimated ΔHvap (Enthalpy of Vaporization) = {delta_H_vap:.2f} kJ/mol")
