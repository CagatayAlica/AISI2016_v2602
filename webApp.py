import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to", ["FSM Buckling", "Beam Solver"])


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

# beam solver
def plot_beam_bmd(L, P, a_dist):
    """
    L: Total length
    P: Point Load
    a_dist: Distance of load from left support
    """
    x = np.linspace(0, L, 100)
    b_dist = L - a_dist
    Ra = (P * b_dist) / L

    # Bending Moment Calculation
    m = np.where(x < a_dist, Ra * x, Ra * x - P * (x - a_dist))

    fig = go.Figure()
    # BMD Trace (Filled)
    fig.add_trace(go.Scatter(x=x, y=m, fill='tozeroy', name='Bending Moment', line=dict(color='red')))

    # Formatting
    fig.update_layout(
        title="Bending Moment Diagram (BMD)",
        xaxis_title="Length (L)",
        yaxis_title="Moment (M)",
        template="plotly_white",
        yaxis=dict(autorange="reversed")  # Standard practice to plot BMD on tension side
    )
    return fig

def draw_beam_sketch(L, a_dist, P):
    fig = go.Figure()

    # 1. Draw the Beam (The horizontal member)
    fig.add_trace(go.Scatter(
        x=[0, L], y=[0, 0],
        mode='lines',
        line=dict(color='blue', width=8),
        hoverinfo='none'
    ))

    # 2. Add THE ARROW for the Load
    fig.add_annotation(
        x=a_dist, y=0.1,         # Tip of the arrow
        ax=a_dist, ay=1.2,       # Tail of the arrow
        xref="x", yref="y",
        axref="x", ayref="y",
        text=f"P={P}kN",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="red",
        font=dict(color="red", size=14)
    )

    # 3. LEFT SUPPORT (Pin Support - Solid Triangle)
    fig.add_trace(go.Scatter(
        x=[0], y=[-0.12],
        mode='markers',
        marker=dict(symbol='triangle-up', size=25, color='gray'),
        name="Pin Support",
        hoverinfo='none'
    ))

    # 4. RIGHT SUPPORT (Sliding/Roller Support)
    # The Triangle
    fig.add_trace(go.Scatter(
        x=[L], y=[-0.12],
        mode='markers',
        marker=dict(symbol='triangle-up', size=25, color='gray'),
        name="Roller Support",
        hoverinfo='none'
    ))
    # The "Sliding" line under the triangle
    fig.add_trace(go.Scatter(
        x=[L-L*0.03, L+L*0.03], y=[-0.25, -0.25],
        mode='lines',
        line=dict(color='gray', width=3),
        hoverinfo='none'
    ))

    # Formatting the sketch
    fig.update_layout(
        height=300,
        showlegend=False,
        yaxis=dict(range=[-1, 2], visible=False, fixedrange=True),
        xaxis=dict(range=[-L*0.1, L*1.1], fixedrange=True, title="Beam Length (mm)"),
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white"
    )
    return fig

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

if app_mode == "FSM Buckling":
    # --- PUT ALL YOUR EXISTING FSM CODE HERE ---
    st.image("arkitech_logo.jpg", width=100)
    st.title("FSM Buckling Analysis")
    page_case = st.sidebar.selectbox("Case", ['AXIAL', 'BENDING'])
    # --- UI LAYOUT ---
    col1, col2 = st.columns([1, 2])

    with col1:
        # Add this at the top of your sidebar section
        # Place this at the very beginning of your script
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
            fig_fsm.add_trace(go.Scatter(
                x=lengths,
                y=factors,
                mode='lines+markers',
                name='Elastic Buckling',
                line=dict(color='#1f77b4', width=2)
            ))

            # --- Y-AXIS LIMIT LOGIC ---
            if values and len(values) > 0:
                y_min_val = values[0][2]  # The critical load factor
                y_start = y_min_val * 0.8  # Start slightly below min for better visibility
                y_end = y_min_val * 2.0  # Limit to 2x as requested

                # Apply the strict range
                fig_fsm.update_yaxes(range=[y_start, y_end], autorange=False)

            # --- LOGARITHMIC X-AXIS WITH VERTICAL GRIDS ---
            fig_fsm.update_xaxes(
                type="log",
                title="Half-Wavelength",
                showgrid=True,  # Enable Major Grid
                gridcolor='Gray',  # Color of vertical major lines
                gridwidth=1,
                minor=dict(
                    showgrid=True,  # Enable Minor Grid (The Log segments)
                    gridcolor='#444444',  # Color of vertical minor lines
                    gridwidth=0.5,
                    ticks="inside",
                    ticklen=5
                )
            )

            # --- Y-AXIS GRID ---
            fig_fsm.update_yaxes(
                title="Load Factor (λ)",
                showgrid=True,
                gridcolor='Gray',
                zeroline=True,
                zerolinecolor='Pink'
            )

            fig_fsm.update_layout(
                height=500,
                template="plotly_dark",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig_fsm, use_container_width=True)

            # Display details
            if is_imperial:
                st.write(f'Section : {selected_name}')
            else:
                st.write(sec.descp_Plot)
            st.write(f'Unit : {select_unit.name}')
            st.write(f'**Stress :** fy = {mat.name}')
            st.write(f'**Local Mode:** λ = {values[0][2]:.3f}')
            if len(values) > 1:
                st.write(f'**Distortional Mode:** λ = {values[1][2]:.3f}')

elif app_mode == "Beam Solver":
    st.image("arkitech_logo.jpg", width=100)
    st.title("Simple Beam Solver")

    col_b1, col_b2 = st.columns([1, 2])

    with col_b1:
        st.subheader("Beam Inputs")
        L = st.number_input("Total Length (mm)", value=3000.0)
        P = st.number_input("Point Load (kN)", value=10.0)
        a_dist = st.slider("Load Position (mm)", 0.0, L, L / 2)

        # Calculate Max Moment for display
        b_dist = L - a_dist
        max_m = (P * a_dist * b_dist) / L
        st.metric("Max Moment", f"{max_m:.2f} kNm")

    with col_b2:
        # Display the Sketch with the Arrow
        st.plotly_chart(draw_beam_sketch(L, a_dist, P), use_container_width=True)

        # Display the BMD
        st.plotly_chart(plot_beam_bmd(L, P, a_dist), use_container_width=True)