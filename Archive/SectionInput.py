class Inputs:
    def __init__(self):
        # Select Units
        units = "Metric"
        if units == "Metric":
            uConvL = 1 / 25.4
            uConvS = 1 / 6.895
        else:
            uConvL = 1
            uConvS = 1

        A = 250 * uConvL  # Web total height [in]
        B = 65 * uConvL  # Flange width [in]
        C = 15 * uConvL  # Lip length [in]
        t = 2 * uConvL  # Thickness [in]
        R = 2.5 * uConvL  # Internal bend radius [in]
        alf = 1  # 1 for lipped C section or hat section, 0 for unlipped C sec.
        E = 210000 * uConvS  # Modulus of elasticity [ksi]
        G = 81000 * uConvS  # Modulus of shear [ksi]
        fy = 350 * uConvS  # Yield stress [ksi]
        nu = 0.3  # Poisson's ratio
        # Member Inputs
        Teta = "0"  # Section orientation [Degree]
        Lx = 2830 * uConvL   # Member length in X direction [in]
        Ly = 2830 * uConvL   # Member length in Y direction [in]
        Lt = 2830 * uConvL   # Member length for torsion [in]
        Kx = 1.0  # Buckling factor for X direction
        Ky = 0.5  # Buckling factor for Y direction
        Kt = 0.5 # Buckling factor for torsion
        self.Res = {
            "Unit": units,
            "A": A,
            "B": B,
            "C": C,
            "t": t,
            "R": R,
            "alfa": alf,
            "E": E,
            "G": E,
            "fy": fy,
            "nu": nu,
            "Lx": Lx,
            "Ly": Ly,
            "Lt": Lt,
            "Kx": Kx,
            "Ky": Ky,
            "Kt": Kt,
            "Teta": Teta
        }


class Orientation:
    def __init__(self):
        self.Teta = {"0": """
                        ┌-┐
                        |
                        └-┘
                        """,
                "90": """
                        ┌   ┐
                        └---┘
                        """,
                "270": """
                        ┌---┐
                        └   ┘
                        """
                }
