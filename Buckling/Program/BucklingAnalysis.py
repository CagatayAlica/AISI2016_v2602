from typing import Dict
import mplcursors
from typing import Literal
import matplotlib.pyplot as plt
import numpy as np
from Buckling.pycufsm.fsm import strip
from Buckling.pycufsm.preprocess import stress_gen
from Buckling.pycufsm.types import BC, GBT_Con, Sect_Props

class Buckling:
    def __init__(self, material, section, case:Literal['AXIAL','BENDING'], unit):
        self.unit = unit.unit
        self.material = material
        self.section = section
        self.case = case
        self.values = None

    def runAnalysis(self) -> Dict[str, np.ndarray]:
        # Prepare the nodes and the elements for analysis
        CUFSM_Nodes = []
        CUFSM_Elements = []
        # Prepare the nodes and the elements for CUFSM software input ==> PY_Cufsm.txt
        CUFSM_Nodes_export = []
        CUFSM_Elements_export = []

        nodes = self.section.nodes
        x = nodes[:, 1]
        y = nodes[:, 2]

        if self.unit == 'METRIC':
            toInches = 1.0 / 25.4
            toKsi = 0.1450377377
        else:
            toInches = 1.0
            toKsi = 1.0

        for i in range(len(x)):
            CUFSM_Nodes.append([i + 1, float(x[i]) * toInches, float(y[i]) * toInches, 1, 1, 1, 1, self.material.fy * toKsi])
            CUFSM_Nodes_export.append([i + 1, float(x[i]) * toInches, float(y[i]) * toInches, 1, 1, 1, 1, self.material.fy * toKsi])

        for i in range(len(x) - 1):
            CUFSM_Elements.append([i + 1, i + 1, i + 2, self.section.t * toInches, 100])
            CUFSM_Elements_export.append([i + 1, i + 1, i + 2, self.section.t * toInches, 100])

        for i in CUFSM_Nodes:
            i[0] = i[0] - 1
            i[7] = 0
        for i in CUFSM_Elements:
            i[0] = i[0] - 1
            i[1] = i[1] - 1
            i[2] = i[2] - 1
            i[4] = 0

        header1 = "NODES:\n------------"
        header2 = "\nELEMENTS:\n------------"
        with open('PY_Cufsm.txt', 'w') as f:
            f.write(header1 + "\n")
            for item in CUFSM_Nodes_export:
                f.write(" ".join(map(str, item)) + "\n")
            f.write(header2 + "\n")
            for item in CUFSM_Elements_export:
                f.write(" ".join(map(str, item)) + "\n")

        # Define an isotropic material with E = 29,500 ksi and nu = 0.3
        props = np.array([np.array([0, 29500, 29500, 0.3, 0.3, 29500 / (2 * (1 + 0.3))])])

        # Define a lightly-meshed Cee shape
        # (1 element per lip, 2 elements per flange, 3 elements on the web)
        # Nodal location units are inches

        nodes = np.array(CUFSM_Nodes)
        thickness = self.section.t * toInches
        elements = np.array(CUFSM_Elements)

        # These lengths will generally provide sufficient accuracy for
        # local, distortional, and global buckling modes
        # Length units are inches
        lengths = np.array(
            [
                0.5,
                0.75,
                1,
                1.25,
                1.5,
                1.75,
                2,
                2.25,
                2.5,
                2.75,
                3,
                3.25,
                3.5,
                3.75,
                4,
                4.25,
                4.5,
                4.75,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                22,
                24,
                26,
                28,
                30,
                32,
                34,
                36,
                38,
                40,
                42,
                44,
                46,
                48,
                50,
                52,
                54,
                56,
                58,
                60,
                66,
                72,
                78,
                84,
                90,
                96,
                102,
                108,
                114,
                120,
                132,
                144,
                156,
                168,
                180,
                204,
                228,
                252,
                276,
                300,
            ]
        )

        # No special springs or constraints
        springs = np.array([])
        constraints = np.array([])

        # Values here correspond to signature curve basis and orthogonal based upon geometry
        GBT_con: GBT_Con = {
            "glob": [0],
            "dist": [0],
            "local": [0],
            "other": [0],
            "o_space": 1,
            "couple": 1,
            "orth": 2,
            "norm": 0,
        }

        # Simply-supported boundary conditions
        B_C: BC = "S-S"

        # For signature curve analysis, only a single array of ones makes sense here
        m_all = np.ones((len(lengths), 1))

        # Solve for 10 eigenvalues
        n_eigs = 10

        # Set the section properties for this simple section
        # Normally, these might be calculated by an external package
        sect_props: Sect_Props = {
            "cx": self.section.zgx * toInches,
            "cy": self.section.zgy * toInches,
            "x0": self.section.xo * toInches,
            "y0": 0.000,
            "phi": 0,
            "A": self.section.Ar  * toInches**2,
            "Ixx": self.section.Ix * toInches**4,
            "Ixy": 0,
            "Iyy": self.section.Iy * toInches**4,
            "I11": self.section.Ix  * toInches**4,
            "I22": self.section.Iy * toInches**4,
            "Cw": self.section.Cw * toInches**6,
            "J": self.section.It * toInches**4,
            "B1": 0,
            "B2": 0,
            "wn": np.array([]),
        }

        # Generate the stress points assuming 50 ksi yield and pure compression
        if self.case =='AXIAL':
            nodes_p = stress_gen(
                nodes=nodes,
                forces={
                    "P": sect_props['A'] * self.material.fy * toKsi,
                    "Mxx": 0,
                    "Myy": 0,
                    "M11": 0,
                    "M22": 0,
                    "restrain": False,
                    "offset": [-thickness / 2, -thickness / 2],
                },
                sect_props=sect_props,
            )
        else:
            nodes_p = stress_gen(
                nodes=nodes,
                forces={
                    "P": 0,
                    "Mxx": self.section.Wx  * toInches**3 * self.material.fy * toKsi,
                    "Myy": 0,
                    "M11": 0,
                    "M22": 0,
                    "restrain": False,
                    "offset": [-thickness / 2, -thickness / 2],
                },
                sect_props=sect_props,
            )

        # Perform the Finite Strip Method analysis
        signature, curve, shapes = strip(
            props=props,
            nodes=nodes_p,
            elements=elements,
            lengths=lengths,
            springs=springs,
            constraints=constraints,
            GBT_con=GBT_con,
            B_C=B_C,
            m_all=m_all,
            n_eigs=n_eigs,
            sect_props=sect_props,
        )

        # Return the important example results
        # The signature curve is simply a matter of plotting the
        # 'signature' values against the lengths
        # (usually on a logarithmic axis)
        return {
            "X_values": lengths,
            "Y_values": signature,
            "Y_values_allmodes": curve,
            "Orig_coords": nodes_p,
            "Elements":elements,
            "Deformations": shapes,
            "Section": self.section,
            "fy": self.material.fy,
            "Case": self.case,
            "m_a": m_all,
            "B_C":B_C
                }

    def find_minimas(self, xref, yref):
        arr = []
        for i in range(len(xref)):
            arr.append([xref[i], yref[i]])
        slopes = []
        minima = []
        maxima = []

        def checkSlope(x1, y1, x2, y2):
            slope = (y2 - y1) / (x2 - x1)
            slopes.append(slope)
            return slope

        def midpoint(xi, yi, xj, yj):
            midp = np.array([(xj + xi) / 2.0, (yj + yi) / 2.0])
            return midp

        for i in range(len(xref) - 1):
            checkSlope(xref[i], yref[i], xref[i + 1], yref[i + 1])

        # Minimas
        for i in range(len(slopes) - 1):
            if slopes[i] < 0 < slopes[i + 1]:
                minima.append(arr[i + 1])

        # Maximas
        for i in range(len(slopes) - 1):
            if slopes[i] > 0 > slopes[i + 1]:
                maxima.append(arr[i + 1])

        # Uncertain minimas
        for i in range(len(slopes) - 2):
            # left side
            if slopes[i] < 0 and slopes[i + 2] < 0 and slopes[i + 1] < slopes[i + 2]:
                if slopes[i] > slopes[i + 1] and slopes[i + 1] < slopes[i + 2]:
                    point = midpoint(arr[i + 1][0], arr[i + 1][1], arr[i + 0][0], arr[i + 0][1])
                    minima.append(point)
            # right side
            elif slopes[i] > 0 and slopes[i + 2] > 0 and slopes[i + 2] > slopes[i + 1]:
                if slopes[i] > slopes[i + 1] and slopes[i + 1] < slopes[i + 2]:
                    point = midpoint(arr[i + 2][0], arr[i + 2][1], arr[i + 1][0], arr[i + 1][1])
                    minima.append(point)

        # print(f'Minimas : {minima}')
        # print(f'Maximas : {maxima}')
        return minima, maxima

    def plot_the_signaturecurve(self, name, stress, xval, yval, sec_x, sec_y, minimas, maximas, plot: bool, case):
        self.values = []
        if plot:
            # Create two subplots side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))  # 1 row, 2 columns
            max_values = []
            for i in range(len(maximas)):
                max_values.append(maximas[i][1])
            max_value = max(max_values)
            if self.unit == 'IMPERIAL':
                conv_length = 1
                conv_stress = 1
                unit_name = '[in]'
                stress_name = '[ksi]'
            else:
                conv_length = 25.4
                conv_stress = 0.145038
                unit_name = '[mm]'
                stress_name = '[MPa]'
            loadFactors = 'Critical Length and Load Factors\n'
            # Create the local and distortional values
            for index, minim in enumerate(minimas, start=1):
                # print(f"{index}. {minim}")
                if index == 1:
                    self.values.append([case, 'local', round(float(minim[1]),3)])
                if index == 2:
                    self.values.append([case, 'distortional', round(float(minim[1]),3)])

                if index == 1:
                    textAnno = f'Mode 1:\n{minim[0] * conv_length:.2f} {unit_name}, {minim[1]:.3f}'
                    props = dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.6)
                    ax1.text(minim[0], minim[1] * 0.9, textAnno, fontsize=10, bbox=props, verticalalignment='top',
                             horizontalalignment='center')
                    loadFactors += f'Mode {index}: {minim[0] * conv_length:.3f} {unit_name}, {minim[1]:.3f}\n'
                if index == 2:
                    textAnno = f'Mode 2:\n{minim[0] * conv_length:.2f} {unit_name}, {minim[1]:.3f}'
                    props = dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.6)
                    ax1.text(minim[0], minim[1] * 0.9, textAnno, fontsize=10, bbox=props, verticalalignment='top',
                             horizontalalignment='center')
                    loadFactors += f'Mode {index}: {minim[0] * conv_length:.3f} {unit_name}, {minim[1]:.3f}\n'

            # Plot the data Signature Curve
            ax1.plot(xval, yval)
            ax1.set_ylim(0, max_value * 1.1)
            ax1.grid()
            ax1.set_title('SIGNATURE CURVE')
            ax1.set_xlabel('[in]')
            ax1.set_xscale('log')

            alternativeTitle = ''  # '2" x 2" x 1" x 1/8" - 33 mils'
            if case == 'AXIAL':
                ax1.set_ylabel('Load Factor - Pcr / Py')
                # Add a main title for the entire figure
                if alternativeTitle != '':
                    fig.suptitle(
                        f'Analysis for {alternativeTitle} {unit_name} - {stress / conv_stress:.2f} {stress_name}\n{case}, Pure compression.',
                        fontsize=12)
                else:
                    fig.suptitle(
                        f'Analysis for {name} {unit_name} - {stress / conv_stress:.2f} {stress_name}\n{case}, Pure compression.',
                        fontsize=12)
            else:
                ax1.set_ylabel('Load Factor - Mcr / My')
                # Add a main title for the entire figure
                if alternativeTitle != '':
                    fig.suptitle(
                        f'Analysis for {alternativeTitle} {unit_name} - {stress / conv_stress:.2f} {stress_name}\n{case}, Compression on top fiber.',
                        fontsize=12)
                else:
                    fig.suptitle(
                        f'Analysis for {name} {unit_name} - {stress / conv_stress:.2f} {stress_name}\n{case}, Compression on top fiber.',
                        fontsize=12)

            # Plot the data section
            ax2.plot(sec_x, sec_y)
            ax2.grid()
            ax2.set_title('SECTION')
            ax2 = plt.gca()
            xticks_mm = ax2.get_xticks()
            yticks_mm = ax2.get_yticks()

            ax2.set_xticks(xticks_mm)
            ax2.set_yticks(yticks_mm)

            ax2.set_xticklabels([f"{tick:.1f}" for tick in xticks_mm])
            ax2.set_yticklabels([f"{tick:.1f}" for tick in yticks_mm])


            ax2.set_xlabel(unit_name)
            ax2.set_ylabel(unit_name)
            ax2.axis('equal')

            # Add text to top right of the figure (figure coordinates)
            fig.text(0.98, 0.95, loadFactors, ha='right', va='top', fontsize=10,
                     bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))

            # Adjust layout to make space for the supertitle
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space at the top for suptitle
            # Enable hover cursor
            mplcursors.cursor(ax1, hover=True)
            # Show the plot
            plt.show()
            return self.values
