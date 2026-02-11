import math


class GrossProp:
    def __init__(self, A, B, C, t, R, alfa):
        #  1. Axial and Flexural Properties
        secDivider = "==========================================================="
        grossOutput = f'{secDivider}\nGross Section Properties [inches]\n{secDivider}\n'
        grossOutput += f'Section C {A:.4} x {B:.4} x {C:.4} - {t:.4}\n'
        grossOutput += "1. Axial and Flexural Properties \n"
        #   a. Basic parameters
        grossOutput += "   a. Basic parameters \n"
        grossOutput += f"A : {round(A, 3)}\n"
        grossOutput += f"B : {round(B, 3)}\n"
        grossOutput += f"C : {round(C, 3)}\n"
        grossOutput += f"t : {round(t, 3)}\n"
        grossOutput += f"R : {round(R, 3)}\n"
        grossOutput += f"alfa : {round(alfa, 1)}\n"
        r = R + t / 2
        grossOutput += f"r : {round(r, 3)}\n"
        a = A - (2 * r + t)
        grossOutput += f"a : {round(a, 3)}\n"
        aa = A - t
        grossOutput += f"aa : {round(aa, 3)}\n"
        b = B - (r + t / 2 + alfa * (r + t / 2))
        grossOutput += f"b : {round(b, 3)}\n"
        bb = B - (t / 2 + alfa * t / 2)
        grossOutput += f"bb : {round(bb, 3)}\n"
        c = alfa * (C - (r + t / 2))
        grossOutput += f"c : {round(c, 3)}\n"
        cc = alfa * (C - t / 2)
        grossOutput += f"cc : {round(cc, 3)}\n"
        u = math.pi * r / 2
        grossOutput += f"u : {round(u, 3)}\n"
        #   b. Cross-section area
        grossOutput += "   b. Cross-section area\n"
        A = t * (a + 2 * b + 2 * u + alfa * (2 * c + 2 * u))
        grossOutput += f"A : {round(A, 3)}\n"
        #   c. Moment of inertia about the x-axis
        grossOutput += "   c. Moment of inertia about the x-axis\n"
        Ix = 2 * t * (0.0417 * a ** 3 + b * (a / 2 + r) ** 2 + u * (a / 2 + 0.637 * r) ** 2 + 0.149 * r ** 3 +
                      alfa * (0.0833 * c ** 3 + c / 4 * (a - c) ** 2 + u * (a / 2 + 0.637 * r) ** 2 + 0.149 * r ** 3))
        grossOutput += f"Ix : {round(Ix, 3)}\n"
        #   d. Distance between centroid and web centerline
        grossOutput += "   d. Distance between centroid and web centerline\n"
        xcbar = 2 * t / A * (b * (b / 2 + r) + u * (0.363 * r) + alfa * (u * (b + 1.637 * r) + c * (b + 2 * r)))
        grossOutput += f"xcbar : {round(xcbar, 3)}\n"
        #   e. Moment of inertia about the y-axis
        grossOutput += "   e. Moment of inertia about the y-axis\n"
        Iy = 2 * t * (b * (b / 2 + r) ** 2 + b ** 3 / 12 + 0.356 * r ** 3 +
                      alfa * (c * (b + 2 * r) ** 2 + u * (b + 1.637 * r) ** 2 + 0.149 * r ** 3)) - A * xcbar ** 2
        grossOutput += f"Iy : {round(Iy, 3)}\n"
        #   f. Distance between shear and web centerline
        grossOutput += "   f. Distance between shear and web centerline\n"
        m = bb * ((3 * aa ** 2 * bb + alfa * cc * (6 * aa ** 2 - 8 * cc ** 2)) / (
                aa ** 3 + 6 * aa ** 2 * bb + alfa * cc * (8 * cc ** 2 - 12 * aa * cc + 6 * aa ** 2)))
        grossOutput += f"m : {round(m, 3)}\n"
        #   g. Distance between centroid and shear center
        grossOutput += "   g. Distance between centroid and shear center\n"
        xo = -(xcbar + m)
        grossOutput += f"xo : {round(xo, 3)}\n"
        #  2. Torsional Properties
        grossOutput += "2. Torsional Properties\n"
        #   a. St. Venant torsional constant
        grossOutput += "   a. St. Venant torsional constant\n"
        J = t ** 3 / 3 * (a + 2 * b + 2 * u + alfa * (2 * c + 2 * u))
        grossOutput += f"J : {round(J, 6)}\n"
        #   b. Warping constant
        grossOutput += "   b. Warping constant\n"
        Cw = aa ** 2 * bb ** 2 * t / 12 * ((2 * aa ** 3 * bb + 3 * aa ** 2 * bb ** 2 +
                                            alfa * (48 * cc ** 4
                                                    + 112 * bb * cc ** 3
                                                    + 8 * aa * cc ** 3
                                                    + 48 * aa * bb * cc ** 2
                                                    + 12 * aa ** 2 * cc ** 2
                                                    + 12 * aa ** 2 * bb * cc
                                                    + 6 * aa ** 3 * cc)) /
                                           (6 * aa ** 2 * bb + (aa + alfa * 2 * cc) ** 3 - alfa * 24 * aa * cc ** 2))
        grossOutput += f"Cw : {round(Cw, 6)}\n"
        #   c. Parameter used in determination of elastic critical moment
        grossOutput += "   c. Parameter used in determination of elastic critical moment\n"
        bw = -(t * xcbar * aa ** 3 / 12 + t * xcbar ** 3 * aa)
        bf = t / 2 * ((bb - xcbar) ** 4 - xcbar ** 4) + t * aa ** 2 / 4 * ((bb - xcbar) ** 2 - xcbar ** 2)
        bl = alfa * (2 * cc * t * (bb - xcbar) ** 3 + 2 / 3 * t * (bb - xcbar) * ((aa / 2) ** 3 - (aa / 2 - cc) ** 3))
        j = 1 / (2 * Iy) * (bw + bf + bl) - xo
        grossOutput += f"bw : {round(bw, 3)}\n"
        grossOutput += f"bf : {round(bf, 3)}\n"
        grossOutput += f"bl : {round(bl, 3)}\n"
        grossOutput += f"j : {round(j, 3)}\n"
        # Output
        self.Res = {
            "r": r,
            "a": a,
            "aa": aa,
            "b": b,
            "bb": bb,
            "c": c,
            "cc": cc,
            "u": u,
            "Ag": A,
            "Ix": Ix,
            "xcbar": xcbar,
            "Iy": Iy,
            "m": m,
            "xo": xo,
            "J": J,
            "Cw": Cw,
            "bw": bw,
            "bf": bf,
            "bl": bl,
            "j": j,
            "Report": grossOutput
        }
