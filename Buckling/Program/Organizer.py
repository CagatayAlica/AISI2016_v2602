from typing import Literal
import Buckling.Program.BucklingAnalysis

class Buckle:
    def __init__(self, selected_unit, section, material, case:Literal['AXIAL','BENDING']):
        self.values = None
        # ==============================================================================================================
        # Buckling analysis
        # ==============================================================================================================
        Buckling_for = Buckling.Program.BucklingAnalysis.Buckling(material, section, case, selected_unit)
        analysis_for = Buckling_for.runAnalysis()

        # Signature Curve Data
        # Curve shape
        self.x = analysis_for['X_values']
        self.y = analysis_for['Y_values']

        # Section
        sectionNodes = analysis_for['Section'].nodes
        section = analysis_for['Section']
        section_x = sectionNodes[:, 1]
        section_y = sectionNodes[:, 2]
        sec_name = analysis_for['Section'].descp_Plot
        # sec_name = f'H {A:.3f}"x{B:.3f}"x{L1:.3f}"x{L2:.3f}"-{L2:.3f}"'
        fyield = analysis_for['fy'] * selected_unit.toKsi
        designCase = analysis_for['Case']

        minima_val, maxima_val = Buckling_for.find_minimas(self.x, self.y)

        bending = Buckling_for.plot_the_signaturecurve(sec_name, fyield, self.x, self.y, section_x, section_y, minima_val, maxima_val, True,
                                               Buckling_for.case)
        self.values = Buckling_for.values
        print(Buckling_for.values)
