import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import time
import InputBlock.Definitions as defs
import InputBlock.Unit
import InputBlock.Section
import InputBlock.Material
import Buckling.Program.Organizer as org

st.set_page_config(page_title="Lipped C-Beam FSM", layout="wide")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Design Case :triangular_ruler:", divider="gray")
page_case = st.sidebar.selectbox("Case", ['AXIAL','BENDING'])
st.sidebar.header("Section Dimension 🏗️", divider="gray")
unit_system = st.sidebar.selectbox("Unit System", ["METRIC", "IMPERIAL"])
select_unit = InputBlock.Unit.Unit(unit_system)
print(select_unit)
print(unit_system)

# --- 1. LOAD DATA (Handling spaces/tabs) ---
# 1. Define the path to your file (No extension needed)
# Change 'DataFolder' and 'SectionDatabase' to your actual folder and filename
file_path = os.path.join("SectionLibraries", "AISI_Sections_C")

@st.cache_data # Cache so it doesn't read the disk every time you click a button
def load_database(path):
    if os.path.exists(path):
        # sep='\s+' handles any combination of tabs and spaces
        return pd.read_csv(path, sep='\s+')
    else:
        st.error(f"File not found at: {path}")
        return None

df_sections = load_database(file_path)

# Logic: If Imperial is selected, we disable manual typing
is_imperial = (unit_system == "IMPERIAL")

selected_name = st.sidebar.selectbox(
    "Choose a Standard Section",
    ["Manual Input"] + df_sections['Section'].tolist(),
    disabled=not is_imperial # Optional: only allow list selection if in Imperial mode
)

# --- 3. LOGIC TO SET VALUES ---
if selected_name != "Manual Input":
    section_data = df_sections[df_sections['Section'] == selected_name].iloc[0]
    init_a = float(section_data['D'])
    init_b = float(section_data['B'])
    init_t = float(section_data['t'])
    init_c = float(section_data['C'])
    init_r = float(section_data['R'])
else:
    init_a, init_b, init_t, init_c, init_r = 12.0, 4.0, 0.105, 0.885, 0.1875


# --- 4. DISPLAY THE NUMBER INPUTS ---
# The 'disabled' parameter is set to True if unit is Imperial
st.sidebar.subheader(f"Units in {select_unit.name}")
defs.fy = st.sidebar.number_input("Yield Stress (fy)", value=50.0 if is_imperial else 355.0)
defs.A = st.sidebar.number_input("Web Height (A)", value=init_a, disabled=is_imperial)
defs.B = st.sidebar.number_input("Flange Width (B)", value=init_b, disabled=is_imperial)
defs.C = st.sidebar.number_input("Lip Length (C)", value=init_c, disabled=is_imperial)
defs.t = st.sidebar.number_input("Thickness (t)", value=init_t, disabled=is_imperial)
defs.R = st.sidebar.number_input("Inner Radius (R)", value=init_r, disabled=is_imperial)


if is_imperial:
    st.sidebar.info("💡 Manual inputs are locked in Imperial mode. Use the selection list above.")


# ======================================================================================================================
# Steel material in selected unit
# ======================================================================================================================
mat = InputBlock.Material.Material(defs.name, defs.fy, defs.fu, select_unit)
print(mat)
# ======================================================================================================================
# Defining the section in selected unit
# ======================================================================================================================
sec = InputBlock.Section.C_Section(defs.A, defs.B, defs.C, defs.t, defs.R, 0, mat)
print(sec)


# --- FSM SOLVER (Placeholder) ---
def run_fsm_analysis():
    """
    This is where your Finite Strip Method logic goes.
    It usually involves:
    1. Discretizing the strips.
    2. Building the Stiffness (K) and Geometric Stiffness (Kg) matrices.
    3. Solving the eigenvalue problem: (K - λKg)Φ = 0
    """
    # Simulating a calculation delay
    time.sleep(1)

    step1 = org.Buckle(selected_unit=select_unit, section=sec, material=mat, case=page_case)

    return step1.x, step1.y, step1.values


# --- UI LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    # Add this at the top of your sidebar section
    # Place this at the very beginning of your script
    st.image("arkitech_logo.jpg", use_container_width=True, width=100)
    st.divider()  # Adds a nice line under the logo
    st.subheader("Analysis Controls")
    # THE BUTTON
    if st.button("🚀 Run Finite Strip Analysis"):
        with st.spinner('Calculating buckling modes...'):
            lengths, factors, values = run_fsm_analysis()
            st.success("Analysis Complete!")
            st.session_state['fsm_data'] = (lengths, factors, values)
    else:
        st.info("Adjust dimensions and click 'Run' to see buckling analysis.")

    # Top: Cross Section Plot
    # (Using the plotting logic from previous response)
    x_coords = sec.nodes[:, 1]
    y_coords = sec.nodes[:, 2]
    fig_sec = go.Figure(data=go.Scatter(x=x_coords, y=y_coords, line=dict(color='white', width=3)))
    fig_sec.update_layout(title="Section Geometry", height=300, yaxis=dict(scaleanchor="x"))
    st.plotly_chart(fig_sec, use_container_width=True)

with col2:
    # Bottom: FSM Signature Curve Plot
    if 'fsm_data' in st.session_state:
        st.subheader(f'FSM Signature Curve for {page_case} :part_alternation_mark:', divider="gray")
        lengths, factors, values = st.session_state['fsm_data']
        fig_fsm = go.Figure()
        fig_fsm.add_trace(go.Scatter(x=lengths, y=factors, mode='lines+markers', name='Elastic Buckling'))
        fig_fsm.update_xaxes(type="log", title="Half-Wavelength")
        fig_fsm.update_yaxes(title="Load Factor (λ)")
        fig_fsm.update_yaxes(range=[0, 2.5])  # Limits view from 0 to 2.5
        fig_fsm.update_layout(height=400)
        st.plotly_chart(fig_fsm, use_container_width=True)
        st.write(f'Buckling mode {values[0][1]}, load factor {values[0][2]:.3f}')
        st.write(f'Buckling mode {values[1][1]}, load factor {values[1][2]:.3f}')
