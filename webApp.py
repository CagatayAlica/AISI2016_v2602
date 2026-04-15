import streamlit as st
import ezdxf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import openseespy.opensees as ops
from fpdf import FPDF
import tempfile
import numpy as np
import json
import os
import time
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import io
import InputBlock.Definitions as defs
import InputBlock.Unit
import InputBlock.Section
import InputBlock.Material
import Buckling.Program.Organizer as org

# Manually add the site-packages path if Windows is struggling to find the DLLs
dll_path = r"C:\Users\cagatay.alica\AppData\Local\Programs\Python\Python313\Lib\site-packages\openseespy\opensees"
if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
# ======================================================================================================================
# === BASIC CONFIGURATION ===
# ======================================================================================================================

st.set_page_config(page_title="Lipped C-Beam FSM", layout="wide")

# --- SIDEBAR INPUTS ---
st.sidebar.image("arkitech_logo.jpg", width=100)
st.sidebar.header("Design Case :triangular_ruler:", divider="gray")

st.sidebar.title("Navigation")
options = ["FSM Buckling",
           "Beam Solver",
           "Truss Solver",
           "Container Fitting",
           "Strip Width Calculator",
           "Strap Bracing"]
app_mode = st.sidebar.radio("Go to", options)

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
    init_fy = 50.0
else:
    init_a, init_b, init_t, init_c, init_r, init_fy = 90.0, 45.0, 1.2, 10.0, 2.5, 355.0

# --- 4. DISPLAY THE NUMBER INPUTS ---
# The 'disabled' parameter is set to True if unit is Imperial
st.sidebar.subheader(f"Units in {select_unit.name}")
if is_imperial:
    defs.fy = st.sidebar.number_input("Yield Stress (fy)", value=init_fy)
    defs.A = st.sidebar.number_input("Web Height (A)", value=init_a, disabled=is_imperial)
    defs.B = st.sidebar.number_input("Flange Width (B)", value=init_b, disabled=is_imperial)
    defs.C = st.sidebar.number_input("Lip Length (C)", value=init_c, disabled=is_imperial)
    defs.t = st.sidebar.number_input("Thickness (t)", value=init_t, disabled=is_imperial)
    defs.R = st.sidebar.number_input("Inner Radius (R)", value=init_r, disabled=is_imperial)
    st.sidebar.info("💡 Manual inputs are locked in Imperial mode. Use the selection list above.")
else:
    init_a, init_b, init_t, init_c, init_r, init_fy = 90.0, 45.0, 1.2, 10.0, 2.5, 355.0
    defs.fy = st.sidebar.number_input("Yield Stress (fy)", value=init_fy)
    defs.A = st.sidebar.number_input("Web Height (A)", value=init_a)
    defs.B = st.sidebar.number_input("Flange Width (B)", value=init_b)
    defs.C = st.sidebar.number_input("Lip Length (C)", value=init_c)
    defs.t = st.sidebar.number_input("Thickness (t)", value=init_t)
    defs.R = st.sidebar.number_input("Inner Radius (R)", value=init_r)


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

# ======================================================================================================================
# Defining the required functions
# ======================================================================================================================
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

# --- Beam SOLVER (Placeholder) ---
def save_to_section_library(name, data_dict, filename="section_library.json"):
    library = {}

    # Check if file exists AND is not empty
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            with open(filename, 'r') as f:
                library = json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted/empty, we start with an empty library
            library = {}
    else:
        # File doesn't exist or is 0 bytes
        library = {}

    # Add or update the section
    library[name] = data_dict

    with open(filename, 'w') as f:
        json.dump(library, f, indent=5)

def load_section_library(filename="section_library.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def run_beam_solver(beam_Length, support_data, point_loads, uniform_loads):
    """
    Runs OpenSees analysis for a given set of loads.
    :param beam_Length:
    :param support_data: supp_data
    :param point_loads: pload_data
    :param uniform_loads: uload_data
    :return: (df_results [0], max_vals [1], res_x [2], res_axial [3], res_shear [4], res_moment [5], res_disp [6])
    """

    # 1. GENERATE NODES (Including sub-discretization for smooth curves)
    # Create nodes at points of interest
    poi = [0.0, beam_Length] + support_data['x'].tolist() + point_loads['x'].tolist() + \
          uniform_loads['x_start'].tolist() + uniform_loads['x_end'].tolist()

    # Add extra points every 100mm to make diagrams smooth
    extra_points = np.linspace(0, beam_Length, int(beam_Length / 100)).tolist()
    raw_nodes = poi + extra_points

    node_coords = sorted(list(set([round(x, 2) for x in raw_nodes if 0 <= x <= beam_Length])))

    # 2. OPENSEES SOLVER
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)

    for i, x in enumerate(node_coords):
        ops.node(i + 1, x, 0.0)

    # Boundary Conditions
    for _, s in supp_data.iterrows():
        # 1. Find the index of the node closest to the support X-coordinate
        # This prevents errors if there are small rounding differences
        idx = int(np.argmin([abs(x - s['x']) for x in node_coords]))

        # 2. OpenSees tags are 1-based. Force to standard Python int.
        n_tag = int(idx + 1)

        # 3. Apply fixity based on the type string
        try:
            if s['type'] == 'Pin':
                ops.fix(n_tag, 1, 1, 0)
            elif s['type'] == 'Roller':
                ops.fix(n_tag, 0, 1, 0)
            elif s['type'] == 'Fixed':
                ops.fix(n_tag, 1, 1, 1)
        except Exception as e:
            st.error(f"Failed to apply support at x={s['x']}: {e}")

    ops.geomTransf('Linear', 1)
    for i in range(len(node_coords) - 1):
        ops.element('elasticBeamColumn', i + 1, i + 1, i + 2, 1000.0, E_mod, I_val, 1)

    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)

    # Point Loads
    for _, p in pload_data.iterrows():
        n_tag = int(np.argmin([abs(x - p['x']) for x in node_coords]) + 1)
        force_n = float(p['mag']) * 1000

        if p['axis'] == 'Y':
            ops.load(n_tag, 0.0, force_n, 0.0)  # [Fx, Fy, M] -> Fy is index 2
        else:
            ops.load(n_tag, force_n, 0.0, 0.0)  # [Fx, Fy, M] -> Fx is index 1

    # Uniform Loads
    for _, u in uload_data.iterrows():
        mag_val = float(u['mag'])
        for i in range(len(node_coords) - 1):
            if node_coords[i] >= u['x_start'] and node_coords[i + 1] <= u['x_end']:
                if u['axis'] == 'Y':
                    # '-beamUniform' second argument is transverse load
                    ops.eleLoad('-ele', i + 1, '-type', '-beamUniform', mag_val)
                else:
                    # Axial loads usually require '-beamUniform' with axial component defined
                    # or using '-beamPoint' for distributed axial if needed.
                    # Standard beamUniform in OpenSees typically handles transverse.
                    # For distributed axial, we apply it as an elemental axial force.
                    ops.eleLoad('-ele', i + 1, '-type', '-beamUniform', 0.0, mag_val)

    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-6, 10)
    ops.algorithm('Linear')
    ops.integrator('LoadControl', 1.0)
    ops.analysis('Static')
    ops.analyze(1)

    # --- 3. EXTRACT RESULTS ---
    res_x, res_axial, res_shear, res_moment, res_disp = [], [], [], [], []
    element_results = []  # New list for CSV data

    for i, x in enumerate(node_coords):
        res_x.append(x)
        res_disp.append(ops.nodeDisp(i + 1, 2))

        if i < len(node_coords) - 1:
            # force = [Fx1, Fy1, M1, Fx2, Fy2, M2]
            f = ops.eleResponse(i + 1, 'force')

            # 1. Store for plotting
            res_axial.append(-f[0] / 1000)
            res_shear.append(f[1] / 1000)
            res_moment.append(-f[2] / 1e6)

            # 2. Store for CSV Export
            element_results.append({
                "Element_ID": i + 1,
                "Node_Start": i + 1,
                "Node_End": i + 2,
                "X_Start_mm": x,
                "X_End_mm": node_coords[i + 1],
                "Axial_Start_kN": -f[0] / 1000,
                "Shear_Start_kN": f[1] / 1000,
                "Moment_Start_kNm": -f[2] / 1e6,
                "Axial_End_kN": f[3] / 1000,
                "Shear_End_kN": -f[4] / 1000,
                "Moment_End_kNm": f[5] / 1e6
            })
        else:
            # Handling the very last node for plotting
            f_last = ops.eleResponse(i, 'force')
            res_axial.append(f_last[3] / 1000)
            res_shear.append(-f_last[4] / 1000)
            res_moment.append(f_last[5] / 1e6)

    # Create the DataFrame
    df_export = pd.DataFrame(element_results)

    # --- FIND PEAK VALUES AND LOCATIONS ---
    # We use absolute maximums for structural design capacity checks
    idx_max_disp = np.argmax(np.abs(res_disp))
    idx_max_axial = np.argmax(np.abs(res_axial))
    idx_max_shear = np.argmax(np.abs(res_shear))
    idx_max_moment = np.argmax(np.abs(res_moment))

    max_vals = {
        "Max Displacement": {"val": res_disp[idx_max_disp], "x": res_x[idx_max_disp], "unit": "mm"},
        "Max Axial": {"val": res_axial[idx_max_axial], "x": res_x[idx_max_axial], "unit": "kN"},
        "Max Shear": {"val": res_shear[idx_max_shear], "x": res_x[idx_max_shear], "unit": "kN"},
        "Max Moment": {"val": res_moment[idx_max_moment], "x": res_x[idx_max_moment], "unit": "kNm"}
    }
    return df_export, max_vals, res_x, res_axial, res_shear, res_moment, res_disp

def plot_beam_results(results_df, L, supp_df, pload_df, uload_df):
    # Create 4 rows now. Row 1 is the Schematic.
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.2, 0.25, 0.25, 0.3],  # Schematic is smaller
        subplot_titles=("Beam Schematic", "Displacement (mm)", "Shear Force (kN)", "Bending Moment (kNm)")
    )

    # --- ROW 1: BEAM SCHEMATIC ---
    # Main Beam Line
    fig.add_trace(go.Scatter(x=[0, beam_L], y=[0, 0], mode='lines',
                             line=dict(color='white', width=6), hoverinfo='skip'), row=1, col=1)

    # Draw Supports with Geometry
    for _, s in supp_data.iterrows():
        px = s['x']
        if s['type'] == 'Pin':
            # Triangle for Pin
            fig.add_trace(go.Scatter(x=[px - 60, px, px + 60, px - 60], y=[-0.5, 0, -0.5, -0.5],
                                     fill="toself", line=dict(color='lightgray'), hoverinfo='skip'), row=1, col=1)
        elif s['type'] == 'Roller':
            # Circle for Roller
            fig.add_trace(go.Scatter(x=[px], y=[-0.25], mode='markers',
                                     marker=dict(symbol='circle-open', size=14, color='lightgray'), hoverinfo='skip'),
                          row=1, col=1)
            fig.add_shape(type="line", x0=px - 70, y0=-0.5, x1=px + 70, y1=-0.5, line=dict(color="gray", width=2),
                          row=1, col=1)

    # Draw Point Loads as Proper Arrows
    for _, p in pload_data.iterrows():
        fig.add_annotation(
            x=p['x'], y=0, ax=p['x'], ay=1.5,  # ay is the length of the arrow
            xref="x1", yref="y1", text="",
            showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor="#FF4B4B"
        )

    # 4. Draw Uniform Loads (Distributed Arrows)
    for _, u in uload_data.iterrows():
        # Draw the top boundary line of the UDL
        fig.add_shape(type="line", x0=u['x_start'], y0=0.6, x1=u['x_end'], y1=0.6,
                      line=dict(color="orange", width=2, dash='dot'), row=1, col=1)
        # Draw small arrows every 200mm along the UDL
        udl_steps = np.linspace(u['x_start'], u['x_end'], max(2, int((u['x_end'] - u['x_start']) / 300)))
        for step_x in udl_steps:
            fig.add_annotation(x=step_x, y=0, ax=step_x, ay=0.6, xref="x1", yref="y1",
                               text="", showarrow=True, arrowhead=1, arrowsize=1, arrowwidth=1, arrowcolor="orange")

    # --- ROWS 2-4: RESULTS (Previous Logic) ---
    fig.add_trace(
        go.Scatter(x=results_df['x'], y=results_df['disp'], fill='tozeroy', line=dict(color='royalblue'), name="Disp"),
        row=2, col=1)
    fig.add_trace(
        go.Scatter(x=results_df['x'], y=results_df['shear'], line=dict(color='firebrick', shape='hv'), fill='tozeroy',
                   name="Shear"), row=3, col=1)
    fig.add_trace(go.Scatter(x=results_df['x'], y=results_df['moment'], fill='tozeroy', line=dict(color='forestgreen'),
                             name="Moment"), row=4, col=1)

    # Global Layout Cleanup
    fig.update_layout(height=900, template="plotly_dark", hovermode="x unified")
    fig.update_yaxes(visible=False, row=1, col=1)  # Hide Y-axis for the schematic only

    return fig

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

def generate_pdf_report(section_name, max_vals, fig):
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Beam Analysis Report", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Profile: {section_name}", ln=True, align='C')
    pdf.ln(10)

    # Summary Table
    pdf.set_font("Arial", "B", 11)
    pdf.cell(60, 10, "Parameter", 1, 0, 'C')
    pdf.cell(60, 10, "Max Value", 1, 0, 'C')
    pdf.cell(60, 10, "Location (x)", 1, 1, 'C')

    pdf.set_font("Arial", "", 10)
    units = {"Max Displacement": "mm", "Max Shear": "kN", "Max Moment": "kNm"}

    for label, data in max_vals.items():
        unit = units.get(label, "")
        # This is where it was crashing:
        pdf.cell(60, 10, label, 1)
        pdf.cell(60, 10, f"{data['val']:.2f} {unit}", 1)  # data['val'] is now a float
        pdf.cell(60, 10, f"{data['x']:.0f} mm", 1, 1)  # data['x'] is now a float

    pdf.ln(10)

    # Embed the Plotly Figure (including the new arrows)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.write_image(tmp.name, engine="kaleido", width=1100, height=850)
        pdf.image(tmp.name, x=10, w=190)

    return pdf.output(dest='S').encode('latin-1')

# --- Truss SOLVER (Placeholder) ---
def generate_truss_pdf(nodes, elements, project_name="Truss Analysis"):
    buffer = io.BytesIO()
    # Set page to A4 Landscape
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # --- 1. DRAW FRAME ---
    c.setLineWidth(2)
    c.rect(20, 20, width - 40, height - 40)  # Outer border

    # --- 2. TECHNICAL DATA TABLE (Top Right) ---
    table_w = 150
    table_h = 60
    tr_x = width - 20 - table_w
    tr_y = height - 20 - table_h

    c.setLineWidth(1)
    c.rect(tr_x, tr_y, table_w, table_h)

    # Table Grid Lines
    c.line(tr_x, tr_y + 40, tr_x + table_w, tr_y + 40)
    c.line(tr_x, tr_y + 20, tr_x + table_w, tr_y + 20)

    c.setFont("Helvetica-Bold", 9)
    # Row 1
    c.drawString(tr_x + 5, tr_y + 47, "Total Nodes:")
    c.setFont("Helvetica", 9)
    c.drawString(tr_x + 90, tr_y + 47, str(len(nodes)))

    # Row 2
    c.setFont("Helvetica-Bold", 9)
    c.drawString(tr_x + 5, tr_y + 27, "Total Elements:")
    c.setFont("Helvetica", 9)
    c.drawString(tr_x + 90, tr_y + 27, str(len(elements)))

    # Row 3
    c.setFont("Helvetica-Bold", 9)
    c.drawString(tr_x + 5, tr_y + 7, "Units:")
    c.setFont("Helvetica", 9)
    c.drawString(tr_x + 90, tr_y + 7, "Metric (mm/kN)")

    # --- 3. DRAW TITLE BLOCK (Bottom Right) ---
    tb_width = 200
    tb_height = 80
    start_x = width - 20 - tb_width
    start_y = 20

    c.setLineWidth(1)
    c.rect(start_x, start_y, tb_width, tb_height)  # Title block box
    c.line(start_x, start_y + 40, start_x + tb_width, start_y + 40)  # Middle divider

    c.setFont("Helvetica-Bold", 10)
    c.drawString(start_x + 5, start_y + 65, "PROJECT:")
    c.setFont("Helvetica", 10)
    c.drawString(start_x + 5, start_y + 50, project_name)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(start_x + 5, start_y + 25, "DATE:")
    import datetime
    c.drawString(start_x + 40, start_y + 25, str(datetime.date.today()))

    # --- 4. DRAW TRUSS GEOMETRY ---
    # Find scaling factors to fit truss in the page
    all_x = [n[0] for n in nodes]
    all_y = [n[1] for n in nodes]

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    truss_w = max_x - min_x
    truss_h = max_y - min_y

    # Scale to fit (leaving margin for the title block)
    scale = min((width - 100) / truss_w, (height - 150) / truss_h)

    offset_x = 50 - min_x * scale
    offset_y = 120 - min_y * scale  # Shifted up to avoid title block

    c.setLineWidth(1.5)
    c.setStrokeColorRGB(0, 0, 0)  # Black lines
    for el in elements:
        x1, y1 = el[0][0] * scale + offset_x, el[0][1] * scale + offset_y
        x2, y2 = el[1][0] * scale + offset_x, el[1][1] * scale + offset_y
        c.line(x1, y1, x2, y2)

    # --- 5. ADDING NODE and LINE NUMBERS ---
    # Draw Nodes as small circles
    for n in nodes:
        nx, ny = n[0] * scale + offset_x, n[1] * scale + offset_y
        c.circle(nx, ny, 2, stroke=1, fill=1)

        # --- 5.1 DRAW TRUSS ELEMENTS & ELEMENT NUMBERS ---
        c.setLineWidth(1)
        c.setStrokeColorRGB(0, 0, 0)

        for i, el in enumerate(elements):
            x1, y1 = el[0][0] * scale + offset_x, el[0][1] * scale + offset_y
            x2, y2 = el[1][0] * scale + offset_x, el[1][1] * scale + offset_y

            # Draw the line
            c.line(x1, y1, x2, y2)

            # Calculate Midpoint for Member Label
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2

            # Draw Member Number (Small box or circle for clarity)
            c.setFont("Helvetica-Oblique", 7)
            c.setFillColorRGB(0.2, 0.2, 0.8)  # Blueish for members
            c.drawString(mx + 2, my + 2, f"M{i}")

        # --- 5.2 DRAW NODES & NODE NUMBERS ---
        c.setFillColorRGB(0, 0, 0)  # Back to black
        for i, n in enumerate(nodes):
            nx, ny = n[0] * scale + offset_x, n[1] * scale + offset_y

            # Draw Node dot
            c.circle(nx, ny, 1.5, stroke=1, fill=1)

            # Draw Node Number (Slightly offset)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0.8, 0, 0)  # Reddish for nodes
            c.drawString(nx + 4, ny + 4, str(i))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def parse_dxf_truss(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        lines = []
        nodes = set()

        for e in msp.query('LINE'):
            # Get coordinates
            start = (round(e.dxf.start.x, 2), round(e.dxf.start.y, 2))
            end = (round(e.dxf.end.x, 2), round(e.dxf.end.y, 2))

            lines.append((start, end))
            nodes.add(start)
            nodes.add(end)

        return list(nodes), lines
    except Exception as e:
        st.error(f"Error reading CAD file: {e}")
        return None, None

# --- Container fitting (Placeholder) ---
def gravity_pack(container_w, container_h, rects):
    """
    Tries to place rectangles in the lowest available 'pocket'
    to close longitudinal gaps.
    """
    # Sort by height descending to fill the bottom efficiently first
    sorted_rects = sorted(rects, key=lambda x: x[1], reverse=True)
    packed_rects = []

    # We maintain a list of 'occupied' areas to check for overlaps
    occupied_areas = []

    for w, h, name in sorted_rects:
        placed = False
        # Scan Y from bottom up, then X from left to right
        for y in range(0, container_h - h + 1, 10):  # step by 10mm for speed
            for x in range(0, container_w - w + 1, 10):
                # Check if this position overlaps any already packed rect
                overlap = False
                for ox, oy, ow, oh in occupied_areas:
                    if not (x + w <= ox or x >= ox + ow or y + h <= oy or y >= oy + oh):
                        overlap = True
                        break

                if not overlap:
                    packed_rects.append((x, y, w, h, name))
                    occupied_areas.append((x, y, w, h))
                    placed = True
                    break
            if placed: break

    return packed_rects

# --- Coil width calculator (Placeholder) ---
def calculate_coil_width(shape_type, D, B, t, R, C=0):
    # Arc length for one 90-degree bend (centerline)
    arc_length = (np.pi / 2) * (R + t / 2)

    if shape_type == "U-Shape":
        # Segments: (D - 2*(R+t)) + 2*(B - (R+t))
        # Bends: 2
        straights = (D - 2 * (R + t)) + 2 * (B - (R + t))
        total_width = straights + (2 * arc_length)

    elif shape_type == "Lipped C-Shape":
        # Segments: (D - 2*(R+t)) + 2*(B - 2*(R+t)) + 2*(C - (R+t))
        # Bends: 4
        straights = (D - 2 * (R + t)) + 2 * (B - 2 * (R + t)) + 2 * (C - (R + t))
        total_width = straights + (4 * arc_length)

    return round(total_width, 2)

def plot_section(shape_type, D, B, t, R, C=0):
    # Calculate centerline dimensions for plotting
    d_cl = D - t
    b_cl = B - t / 2
    c_cl = C - t / 2

    fig = go.Figure()

    if shape_type == "U-Shape":
        # Coordinates for U: (x, y)
        x = [b_cl, 0, 0, b_cl]
        y = [d_cl, d_cl, 0, 0]
    else:
        # Coordinates for Lipped C: (x, y)
        x = [b_cl - c_cl, b_cl, b_cl, 0, 0, b_cl, b_cl, b_cl - c_cl]
        y = [d_cl, d_cl, d_cl - c_cl, d_cl - c_cl, 0, 0, c_cl, c_cl]
        # Note: This is a simplified stick-model for visualization
        x = [b_cl - c_cl, b_cl, b_cl, 0, 0, b_cl, b_cl, b_cl - c_cl]
        y = [d_cl, d_cl, 0, 0, d_cl, d_cl, d_cl - c_cl]  # Simple C-shape path
        # Better path for C:
        x = [b_cl - c_cl, b_cl, b_cl, 0, 0, b_cl, b_cl, b_cl - c_cl]
        y = [d_cl, d_cl, 0, 0, d_cl, d_cl, d_cl - c_cl]  # This needs ordering

        # Correct path for Lipped C:
        x = [b_cl, b_cl - c_cl, b_cl, b_cl, 0, 0, b_cl, b_cl, b_cl - c_cl]  # Re-ordered below

    # Standard Lipped C path logic
    if shape_type == "Lipped C-Shape":
        x = [b_cl - c_cl, b_cl, b_cl, 0, 0, b_cl, b_cl, b_cl - c_cl]
        y = [d_cl, d_cl, 0, 0, 0, 0, c_cl, c_cl]  # Fix for drawing logic
        # Actual sequence: Top Lip -> Top Flange -> Web -> Bottom Flange -> Bottom Lip
        x = [b_cl, b_cl, 0, 0, b_cl, b_cl]
        y = [d_cl - c_cl, d_cl, d_cl, 0, 0, c_cl]

    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#1f77b4', width=t * 2)))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#212121",
        plot_bgcolor="#212121",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False)
    )
    return fig

# ======================================================================================================================
# === PLATFORMS ===
# ======================================================================================================================

if app_mode == "FSM Buckling":
    # --- PUT ALL YOUR EXISTING FSM CODE HERE ---
    #st.image("arkitech_logo.jpg", width=100)
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
            st.write(f'**Stress :** fy = {defs.fy}')
            st.write(f'**Local Mode:** λ = {values[0][2]:.3f}')
            if len(values) > 1:
                st.write(f'**Distortional Mode:** λ = {values[1][2]:.3f}')

            # ... Saving the data ...

            st.subheader("💾 Add to Section Library")
            section_name = selected_name + '_fy:' + str(defs.fy) if is_imperial else sec.descp_Plot + '_fy:' + str(defs.fy)

            if st.button("Save Section Properties"):
                # Example data to save from your analysis
                props = {
                        "Unit":select_unit.name,
                        "Section":section_name,
                        "DesignFor": values[0][0],  # AXIAL or BENDING
                        "Stress": defs.fy,
                        "Properties":sec.toJSON,
                        "Local_Factor":values[0][2],
                        "Distortional_Factor": values[1][2],
                }
                save_to_section_library(section_name, props)
                st.success(f"Section '{section_name}' added to library!")

elif app_mode == "Beam Solver":
    st.title("🚀 Continuous Beam Solver")

    col_b1, col_b2 = st.columns([1, 2])

    with col_b1:
        st.subheader("Section & Geometry")
        library = load_section_library()

        if library:
            selected_section = st.selectbox("Select Section", options=list(library.keys()))
            sec_props = library[selected_section]
            # Use property keys from your JSON; ensure units are consistent (N, mm)
            I_val = sec_props.get("Iy", 1e6)
            E_mod = 203000  # Standard for Steel (MPa)
        else:
            st.warning("Library empty. Using defaults.")
            I_val = st.number_input("Moment of Inertia (mm4)", value=1000000.0)
            E_mod = 203000

        beam_L = st.number_input("Total Beam Length (mm)", value=6000.0)

        # --- DYNAMIC INPUT TABLES ---
        st.divider()
        st.subheader("1. Supports")
        supp_data = st.data_editor(
            pd.DataFrame([
                {'x': 0.0, 'type': 'Pin'},
                {'x': beam_L, 'type': 'Roller'}
            ]),
            column_config={
                "x": st.column_config.NumberColumn("Location (mm)", min_value=0.0, max_value=beam_L),
                "type": st.column_config.SelectboxColumn(
                    "Support Type",
                    options=["Pin", "Roller"],
                    required=True
                )
            },
            num_rows="dynamic", key="supp_editor"
        )

        # --- INPUT LOADS ---
        st.subheader("2. Point Loads")
        pload_data = st.data_editor(
            pd.DataFrame([{'x': 1500.0, 'case': 'Dead', 'axis': 'Y', 'mag': -10.0}]),
            column_config={
                "case": st.column_config.SelectboxColumn("Load Case", options=["Dead", "Live", "Roof Live", "Wind_1", "Wind_2", "Snow", "Earthquake"], required=True),
                "axis": st.column_config.SelectboxColumn("Axis", options=["X", "Y"], required=True),
                "mag": st.column_config.NumberColumn("Magnitude (kN)", format="%.2f")
            },
            num_rows="dynamic", key="pload_editor"
        )

        st.subheader("3. Uniform Loads")
        uload_data = st.data_editor(
            pd.DataFrame([{'x_start': 0.0, 'x_end': beam_L, 'case': 'Dead', 'axis': 'Y', 'mag': -5.0},
                          {'x_start': 0.0, 'x_end': beam_L / 2.0, 'case': 'Live', 'axis': 'Y', 'mag': -4.0}]),
            column_config={
                "case": st.column_config.SelectboxColumn("Load Case", options=["Dead", "Live", "Roof Live", "Wind_1", "Wind_2", "Snow", "Earthquake"], required=True),
                "axis": st.column_config.SelectboxColumn("Axis", options=["X", "Y"], required=True),
                "mag": st.column_config.NumberColumn("Magnitude (kN/m)", format="%.2f")
            },
            num_rows="dynamic", key="uload_editor"
        )
    text_position_list = []
    with col_b2:
        if st.button("Run Analysis"):
            # Opensees solver function
            analysis_for_combination = run_beam_solver(beam_L, supp_data, pload_data, uload_data)

            # Store in session state for the PDF report
            st.session_state.max_vals = analysis_for_combination[1] #max_vals

            # 4. PLOT 4-TIER DIAGRAM
            # Create Subplots (5 rows now)
            fig = make_subplots(
                rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                row_heights=[0.2, 0.2, 0.2, 0.2, 0.2],
                subplot_titles=("Beam Schematic", "Axial Force (kN)", "Shear Force (kN)", "Bending Moment (kNm)",
                                "Deflection (mm)")
            )
            fig.update_yaxes(range=[-1.5, 2.0], row=1, col=1, visible=False)
            fig.update_layout(height=1100, template="plotly_dark", hovermode="x unified")

            # --- ROW 1: SCHEMATIC ---
            # Draw the Beam
            fig.add_trace(go.Scatter(x=[0, beam_L], y=[0, 0], mode='lines',
                                     line=dict(color='white', width=6), showlegend=False), row=1, col=1)

            # Draw Supports
            for _, s in supp_data.iterrows():
                px = s['x']
                if s['type'] == 'Pin':
                    # Triangle for Pin
                    fig.add_trace(go.Scatter(x=[px - 80, px, px + 80, px - 80], y=[-0.5, 0, -0.5, -0.5],
                                             fill="toself", line=dict(color='lightgray'), mode='lines',
                                             showlegend=False), row=1, col=1)
                elif s['type'] == 'Roller':
                    # Triangle with two circles under it
                    fig.add_trace(go.Scatter(x=[px - 80, px, px + 80, px - 80], y=[-0.3, 0, -0.3, -0.3],
                                             fill="toself", line=dict(color='lightgray'), mode='lines',
                                             showlegend=False), row=1, col=1)
                    fig.add_trace(go.Scatter(x=[px - 40, px + 40], y=[-0.45, -0.45], mode='markers',
                                             marker=dict(symbol='circle', size=8, color='white'), showlegend=False),
                                  row=1, col=1)

            # --- DIMENSION LINE LOGIC ---
            # 1. Collect all critical X-points
            crit_points = [0, beam_L]
            for _, s in supp_data.iterrows():
                crit_points.append(s['x'])

            # 2. Sort and remove duplicates
            crit_points = sorted(list(set(crit_points)))

            # 3. Draw dimension strings between points
            dim_y = -1.2  # Vertical position for the dimension line

            for i in range(len(crit_points) - 1):
                x1 = crit_points[i]
                x2 = crit_points[i + 1]
                dist = x2 - x1

                # Only draw if there is a measurable distance
                if dist > 1:
                    # Main Horizontal Line
                    fig.add_shape(type="line", x0=x1, y0=dim_y, x1=x2, y1=dim_y,
                                  line=dict(color="gray", width=1, dash="dot"), row=1, col=1)

                    # Vertical Tick Marks (the 'slashes')
                    for tick_x in [x1, x2]:
                        fig.add_shape(type="line", x0=tick_x, y0=dim_y - 0.1, x1=tick_x, y1=dim_y + 0.1,
                                      line=dict(color="gray", width=2), row=1, col=1)

                    # Dimension Text (Centered between ticks)
                    fig.add_annotation(
                        x=(x1 + x2) / 2, y=dim_y - 0.2,
                        text=f"{dist:.0f} mm",
                        showarrow=False, font=dict(color="gray", size=10),
                        xref="x1", yref="y1"
                    )


            # Draw Arrows with Text Values
            for _, p in pload_data.iterrows():
                mag = p['mag']
                axis = p['axis']
                case = p['case']

                if axis == 'Y':
                    tail_y = 1.2 if mag < 0 else -1.2
                    color = "#FF4B4B" if mag < 0 else "#32CD32"
                    # Arrow
                    fig.add_annotation(x=p['x'], y=0, ax=p['x'], ay=tail_y, xref="x1", yref="y1", axref="x1", ayref="y1",
                                       showarrow=True, arrowhead=2, arrowcolor=color, arrowwidth=3)
                    # Value Text
                    fig.add_annotation(x=p['x'], y=tail_y * 1.2, text=f"<b>{abs(mag)} kN {case}</b>",
                                       showarrow=False, font=dict(color=color, size=12))
                else:
                    tail_x = p['x'] - (400 if mag > 0 else -400)
                    color = "cyan"
                    fig.add_annotation(x=p['x'], y=0, ax=tail_x, ay=0, xref="x1", yref="y1", axref="x1", ayref="y1",
                                       showarrow=True, arrowhead=2, arrowcolor=color, arrowwidth=3)
                    fig.add_annotation(x=tail_x, y=0.3, text=f"<b>{abs(mag)} kN {case}</b>",
                                       showarrow=False, font=dict(color=color, size=12))

            # Uniform Load Sketch (Vertical only for Y-axis)
            for _, u in uload_data.iterrows():
                if u['axis'] == 'Y':
                    h = 0.3 if u['mag'] < 0 else -0.3
                    fig.add_shape(type="rect", x0=u['x_start'], y0=0, x1=u['x_end'], y1=h,
                                  fillcolor="rgba(255,165,0,0.2)", line=dict(width=1), row=1, col=1)

            # 4. Draw Uniform Loads as Spaced Arrows

            for _, u in uload_data.iterrows():
                mag = u['mag']
                axis = u['axis']
                case =u['case']
                color = "orange"


                # 1. DRAW TRANSPARENT RECTANGLE
                # If Y-axis, box is above/below beam. If X-axis, box sits on the beam.
                box_h = 0.5 if axis == 'Y' else 0.2
                fig.add_shape(type="rect",
                              x0=u['x_start'], y0=box_h if mag < 0 else 0,
                              x1=u['x_end'], y1=0 if mag < 0 else -box_h,
                              fillcolor="rgba(255, 165, 0, 0.15)",  # Transparent Orange
                              line=dict(color=color, width=1, dash='dot'), row=1, col=1)

                # 2. DRAW SPACED ARROWS
                num_arrows = max(2, int(abs(u['x_end'] - u['x_start']) / 500) + 1)
                arrow_positions = np.linspace(u['x_start'], u['x_end'], num_arrows)

                for x_pos in arrow_positions:
                    if axis == 'Y':
                        # Vertical Arrows

                        tail_y = 0.8 if mag < 0 else -0.8
                        fig.add_annotation(x=x_pos, y=0, ax=x_pos, ay=tail_y,
                                           xref="x1", yref="y1", axref="x1", ayref="y1",
                                           showarrow=True, arrowhead=1, arrowcolor=color)
                    else:
                        # Horizontal Arrows (Along the beam axis)
                        # If mag > 0, points Right. If mag < 0, points Left.
                        head_x = x_pos
                        tail_x = x_pos - (300 if mag > 0 else -300)
                        fig.add_annotation(x=head_x, y=0, ax=tail_x, ay=0,
                                           xref="x1", yref="y1", axref="x1", ayref="y1",
                                           showarrow=True, arrowhead=1, arrowcolor=color)

                # 3. ADD VALUE TEXT
                text_y = 1.2 if mag < 0 else -1.2
                text_x = (u['x_start'] + u['x_end']) / 2
                text_position = [text_x, text_y]

                if text_position in text_position_list:
                    text_y = text_y + 0.3 if mag < 0 else text_y - 0.3
                    text_position = [text_x, text_y]
                text_position_list.append(text_position)

                fig.add_annotation(x=text_x, y=text_y,
                                   text=f"<b>{abs(mag)} kN/m ({axis})  {case}</b>",
                                   showarrow=False, font=dict(color=color, size=11), xref="x1", yref="y1")

            # --- ADD AXIAL TRACE (Row 2) ---
            res_x = analysis_for_combination[2]
            res_axial = analysis_for_combination[3]
            res_shear = analysis_for_combination[4]
            res_moment = analysis_for_combination[5]
            res_disp = analysis_for_combination[6]

            fig.add_trace(go.Scatter(
                x=res_x, y=res_axial,
                fill='tozeroy',
                line=dict(color='orange', shape='hv', width=2),
                name="Axial Force"
            ), row=2, col=1)

            # Row 2: Disp
            fig.add_trace(go.Scatter(x=res_x, y=res_disp, fill='tozeroy', name="Disp", line=dict(color='cyan')), row=5,
                          col=1)
            # Row 3: Shear
            fig.add_trace(
                go.Scatter(x=res_x, y=res_shear, fill='tozeroy', name="Shear", line=dict(color='red', shape='hv')),
                row=3, col=1)
            # Row 4: Moment
            fig.add_trace(go.Scatter(x=res_x, y=res_moment, fill='tozeroy', name="Moment", line=dict(color='lime')),
                          row=4, col=1)

            fig.update_yaxes(range=[-1.5, 2.0], row=1, col=1, visible=False)
            fig.update_layout(height=1100, template="plotly_dark", hovermode="x unified")

            st.plotly_chart(fig, use_container_width=True)

            # Store the figure in session state so it's accessible for download
            st.session_state.current_fig = fig
            st.session_state.max_m = max(res_moment, key=abs)
            st.session_state.max_d = max(res_disp, key=abs)
            # Only show download button if analysis has been run
            if 'current_fig' in st.session_state:
                # Pass 'max_vals' directly so the PDF function can access ['val'] and ['x']
                pdf_bytes = generate_pdf_report(
                    selected_section,
                    st.session_state.max_vals,  # Change 'summary' to this
                    st.session_state.current_fig
                )

                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Report_{selected_section}.pdf",
                    mime="application/pdf"
                )

            st.subheader("📊 Critical Design Values")
            m1, m2, m3 = st.columns(3)
            max_vals = analysis_for_combination[1]
            m1.metric("Max Moment", f"{max_vals['Max Moment']['val']:.2f} kNm",
                      help=f"Located at x = {max_vals['Max Moment']['x']:.0f} mm")
            m2.metric("Max Shear", f"{max_vals['Max Shear']['val']:.2f} kN",
                      help=f"Located at x = {max_vals['Max Shear']['x']:.0f} mm")
            m3.metric("Max Deflection", f"{max_vals['Max Displacement']['val']:.2f} mm",
                      help=f"Located at x = {max_vals['Max Displacement']['x']:.0f} mm")

            # --- ADD PEAK ANNOTATIONS ---
            # Define which row corresponds to which result for the loop
            plot_configs = [
                {"val_key": "Max Displacement", "row": 2, "color": "cyan", "unit": "mm"},
                {"val_key": "Max Shear", "row": 3, "color": "red", "unit": "kN"},
                {"val_key": "Max Moment", "row": 4, "color": "lime", "unit": "kNm"}
            ]

            for config in plot_configs:
                data = max_vals[config['val_key']]

                fig.add_annotation(
                    x=data['x'],
                    y=data['val'],
                    text=f"MAX: {data['val']:.2f} {config['unit']}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=config['color'],
                    ax=0,  # Arrow tail x-offset
                    ay=-40 if data['val'] >= 0 else 40,  # Offset arrow based on sign
                    row=config['row'],
                    col=1,
                    font=dict(color=config['color'], size=12)
                )

            st.divider()
            st.subheader("💾 Export Analysis Data")
            df_export = analysis_for_combination[0]
            # Convert DataFrame to CSV string
            csv_data = df_export.to_csv(index=False).encode('utf-8')

            st.download_button(
                    label="📥 Download Element Forces (CSV)",
                    data=csv_data,
                    file_name='beam_element_forces.csv',
                    mime='text/csv',
                    help="Click to download the end forces for every 100mm element."
                )

            # Optional: Show a preview of the table
            with st.expander("Preview Element Data"):
                    st.dataframe(df_export.head(1000))

elif app_mode == "Truss Solver":
    #st.image("arkitech_logo.jpg", width=100)
    st.title(":sauropod: Truss Geometry Loader")

    # In a real scenario, you can use st.file_uploader or a fixed path
    dxf_file = "SectionLibraries/SampleTruss.dxf"

    if st.button("Load Geometry from CAD"):
        nodes, elements = parse_dxf_truss(dxf_file)

        if nodes and elements:
            fig_truss = go.Figure()

            # Plot Elements (Lines)
            for i, el in enumerate(elements):
                fig_truss.add_trace(go.Scatter(
                    x=[el[0][0], el[1][0]],
                    y=[el[0][1], el[1][1]],
                    mode='lines',
                    line=dict(color='gray', width=2),
                    name=f"Element {i}",
                    showlegend=False
                ))

            # Plot Nodes (Points)
            node_x = [n[0] for n in nodes]
            node_y = [n[1] for n in nodes]
            fig_truss.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(size=8, color='red'),
                text=[f"N{i}" for i in range(len(nodes))],
                textposition="top center",
                name="Nodes"
            ))

            fig_truss.update_layout(
                template="plotly_dark",
                paper_bgcolor="#212121",
                plot_bgcolor="#212121",
                yaxis=dict(scaleanchor="x", scaleratio=1),  # Maintain aspect ratio
                title="Truss Geometry extracted from CAD"
            )

            st.plotly_chart(fig_truss, use_container_width=True)
            st.success(f"Successfully loaded {len(nodes)} nodes and {len(elements)} elements.")
            # Export the drawing plot:
            if 'nodes' in locals() and nodes:
                st.divider()
                st.subheader("Export Drawing")

                proj_title = st.text_input("Project Title", value="Arkitech Truss System")

                # The Export Button
                pdf_data = generate_truss_pdf(nodes, elements, proj_title)

                st.download_button(
                    label="📄 Download Technical Drawing (PDF)",
                    data=pdf_data,
                    file_name="Truss_Drawing.pdf",
                    mime="application/pdf"
                )

elif app_mode == "Container Fitting":
    #st.image("arkitech_logo.jpg", width=100)
    st.title("📦 2D Container Fitting")

    st.sidebar.subheader("📥 Bulk Import")
    #uploaded_file = st.sidebar.file_uploader("Upload CSV Packing List", type=["csv"])
    uploaded_file = 'packing_list.csv'

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Validate columns
        required_cols = {'width', 'height', 'quantity'}
        if required_cols.issubset(df.columns):
            if st.sidebar.button("Process & Load List"):
                new_rects = []
                for _, row in df.iterrows():
                    # Create the quantity of rects specified in the row
                    for i in range(int(row['quantity'])):
                        name = row['name'] if 'name' in df.columns else f"Rect"
                        new_rects.append((row['width'], row['height'], f"{name}_{i}"))

                st.session_state.rect_list = new_rects
                st.sidebar.success(f"Loaded {len(new_rects)} rectangles!")
        else:
            st.sidebar.error("CSV must have columns: width, height, quantity")

    col_in, col_viz = st.columns([1, 2])

    with col_in:
        st.subheader("Container Dimensions")
        c_w = st.number_input("Container Width (W)", value=2400)
        c_h = st.number_input("Container Height (H)", value=6000)

        st.divider()
        st.subheader("Add Rectangles")
        r_w = st.number_input("Rect Width", value=600)
        r_h = st.number_input("Rect Height", value=1200)
        r_qty = st.number_input("Quantity", min_value=1, value=5)

        if st.button("Add to List"):
            if 'rect_list' not in st.session_state:
                st.session_state.rect_list = []
            for _ in range(r_qty):
                st.session_state.rect_list.append((r_w, r_h, f"R_{len(st.session_state.rect_list)}"))

        if st.button("Clear All", type="secondary"):
            st.session_state.rect_list = []

    with col_viz:
        if 'rect_list' in st.session_state and st.session_state.rect_list:
            result = gravity_pack(c_w, c_h, st.session_state.rect_list)

            fig = go.Figure()

            # Draw Container
            fig.add_shape(type="rect", x0=0, y0=0, x1=c_w, y1=c_h, line=dict(color="White", width=2))

            # Draw Packed Rectangles
            for x, y, w, h, name in result:
                fig.add_trace(go.Scatter(
                    x=[x, x + w, x + w, x, x],
                    y=[y, y, y + h, y + h, y],
                    fill="toself",
                    name=name,
                    mode='lines',
                    line=dict(color="RoyalBlue"),
                    text=f"{name}: {w}x{h}"
                ))

            fig.update_layout(
                template="plotly_dark",
                xaxis=dict(range=[-100, c_w + 100], scaleanchor="y", scaleratio=1),
                yaxis=dict(range=[-100, c_h + 100]),
                height=700,
                showlegend=False,
                title="Packing Plan"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"Packed {len(result)} out of {len(st.session_state.rect_list)} items.")

elif app_mode == "Strip Width Calculator":
    #st.image("arkitech_logo.jpg", width=100)
    st.title("🧮 Strip Coil Width Calculator")

    col_in, col_res = st.columns([1, 1])

    with col_in:
        st.subheader("Profile Geometry")
        shape = st.selectbox("Select Shape", ["Lipped C-Shape", "U-Shape"])

        # Dimensions
        D = defs.A
        B = defs.B
        t = defs.t
        R = defs.R

        # K-Factor Input (Defaulting to 0.33 for CFS)
        k_factor = st.slider("K-Factor (Neutral Axis)", 0.2, 0.5, 0.33,
                             help="0.33 is standard for cold-formed steel; 0.5 is theoretical center.")

        C = 0.0
        if shape == "Lipped C-Shape":
            C = defs.C
            # --- CALCULATION ---
            arc_length = (np.pi / 2) * (R + (k_factor * t))
            if shape == "U-Shape":
                straights = (D - 2 * (R + t)) + 2 * (B - (R + t))
                total_width = straights + (2 * arc_length)
            else:
                straights = (D - 2 * (R + t)) + 2 * (B - 2 * (R + t)) + 2 * (C - (R + t))
                total_width = straights + (4 * arc_length)

            # --- VISUALIZATION ---
            st.metric(label="Required Coil Width", value=f"{total_width:.2f} mm")

            # Add the Section Plot here
            section_fig = plot_section(shape, D, B, t, R, C)
            st.plotly_chart(section_fig, use_container_width=True)

            st.info(f"K-Factor ({k_factor}) applied to {shape}")

    with col_res:
        # --- CALCULATION LOGIC ---
        # The neutral axis radius = R + (K * t)
        arc_length = (np.pi / 2) * (R + (k_factor * t))

        if shape == "U-Shape":
            # Segments: 1 Web + 2 Flanges
            # Formula subtracts 2*(R+t) from Web and 1*(R+t) from Flanges
            straights = (D - 2 * (R + t)) + 2 * (B - (R + t))
            total_width = straights + (2 * arc_length)
        else:
            # Lipped C: 1 Web + 2 Flanges + 2 Lips
            straights = (D - 2 * (R + t)) + 2 * (B - 2 * (R + t)) + 2 * (C - (R + t))
            total_width = straights + (4 * arc_length)

        # Display Result
        st.metric(label="Required Coil Width", value=f"{total_width:.2f} mm")

        # Breakdown Table
        st.table({
            "Component": ["Bends", "Straight Segments", "Neutral Axis Pos"],
            "Value": [
                "2" if shape == "U-Shape" else "4",
                f"{straights:.2f} mm",
                f"{(k_factor * t):.3f} mm from inside"
            ]
        })

        st.caption("Note: Calculation uses the Centerline (Mean Line) method adjusted by the K-factor.")

elif app_mode == "Strap Bracing":
    st.title("🏗️ Flat Strap Bracing (AISI S213-07)")

    # --- 1. LIBRARY INTEGRATION ---
    library = load_section_library()  # Using the function from our previous step
    if library:
        section_names = list(library.keys())
        selected_stud = st.selectbox("Select Boundary Stud from Library", section_names)
        # 1. Access the main section dict
        section_data = library[selected_stud]

        # 2. Access the 'Properties' sub-dictionary
        properties_dict = section_data.get("Properties", {})

        # 3. Access the values for dimensions
        A_stud = properties_dict.get("A", 90.0)
        B_stud = properties_dict.get("B", 45.0)
        C_stud = properties_dict.get("C", 10.0)
        t_stud = properties_dict.get("t", 1.20)
        R_stud = properties_dict.get("R", 2.50)
    else:
        st.warning("Library is empty. Please enter stud properties manually.")
        t_stud = st.number_input("Manual Stud Thickness (mm)", value=1.2)
        fy_stud = st.number_input("Manual Stud Fy (MPa)", value=350)


    col_in, col_res = st.columns([1, 1])

    with col_in:
        st.subheader("Panel Geometry")
        W_panel = st.number_input("Wall Panel Width (mm)", value=3000.0)
        H_panel = st.number_input("Wall Panel Height (mm)", value=2400.0)

        st.divider()
        st.subheader("Strap Properties")
        W_strap = st.number_input("Strap Width (mm)", value=100.0)
        t_strap = st.number_input("Strap Thickness (mm)", value=1.2)
        Fy = st.number_input("Yield Stress Fy (MPa)", value=345.0)

        st.divider()
        if library:
            selected_stud = st.selectbox("Select Boundary Stud (from Library)", options=list(library.keys()))
            stud_props = library[selected_stud]
        else:
            st.warning("No library found. Using default stud dimensions.")
            stud_props = {"Depth": 90, "Thickness": 1.2}

    # --- 2. CALCULATIONS ---
    # Diagonal length and angle
    L_diag = np.sqrt(W_panel ** 2 + H_panel ** 2)
    theta_rad = np.arctan(H_panel / W_panel)
    theta_deg = np.degrees(theta_rad)

    # Nominal Strength (AISI S213 C5.2.1)
    Ag = W_strap * t_strap
    Pn = (Ag * Fy) / 1000  # Convert to kN

    # Resistance/Safety Factors (LRFD/ASD)
    phi_t = 0.90  # LRFD
    omega_t = 1.67  # ASD

    with col_res:
        st.subheader("Results")
        st.metric("Nominal Strength (Pn)", f"{Pn:.2f} kN")

        c1, c2 = st.columns(2)
        c1.metric("LRFD (φPn)", f"{Pn * phi_t:.2f} kN")
        c2.metric("ASD (Pn/Ω)", f"{Pn / omega_t:.2f} kN")

        st.info(f"**Angle:** {theta_deg:.1f}° | **Length:** {L_diag:.1f} mm")

    # --- 3. SKETCH ---
    st.divider()
    st.subheader("Panel Sketch")

    fig_strap = go.Figure()

    # Draw Wall Frame
    fig_strap.add_shape(type="rect", x0=0, y0=0, x1=W_panel, y1=H_panel,
                        line=dict(color="gray", width=2))

    # Draw Tension Straps (X-Bracing)
    fig_strap.add_trace(go.Scatter(x=[0, W_panel], y=[0, H_panel], mode='lines',
                                   line=dict(color="orange", width=4, dash='dash'), name="Active Strap"))
    fig_strap.add_trace(go.Scatter(x=[0, W_panel], y=[H_panel, 0], mode='lines',
                                   line=dict(color="rgba(150,150,150,0.5)", width=2), name="Compression Strap"))

    fig_strap.update_layout(
        template="plotly_dark",
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True
    )

    st.plotly_chart(fig_strap, use_container_width=True)
