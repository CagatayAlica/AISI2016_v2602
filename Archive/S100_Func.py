import math
import numpy as np


class C_App111:
    """
    Reference : AISI S100-16
    Section   : Appendix 1 | 1.1
    Topic     : Effective width of uniformly compressed stiffened elements
    """

    # The effective width, b, shall be calculated as follows:
    # If this procedure is run for strength determination f=fy,
    # If it is run for serviceability determination f=fd (Procedure I)
    def __init__(self, f, E, nu, w, t, k, Ri):
        # Calculating the critical buckling stress with Eq. 1.1-2
        fcrl = k * math.pow(math.pi, 2) * E / (12 * (1 - math.pow(nu, 2))) * math.pow(t / w, 2)
        # Calculating the lambda with Eq. 1.1-3
        lam = math.sqrt(f / fcrl)
        # Calculating the reduction factor with Eq. 1.1-2
        if lam <= 0.673:
            rho = 1.0
        else:
            rho = (1 - 0.22 / lam) / lam
        # Effective width of the element. Eq. 1.1-1
        b = w * rho
        ds = b * Ri
        b1 = b / 2.0
        b2 = b / 2.0
        # results
        self.Res_C_App111 = {
            "f": f,
            "k": k,
            "fcrl": fcrl,
            "lam": lam,
            "rho": rho,
            "b": b,
            "b1": b1,
            "b2": b2,
            "ds": ds
        }


class C_App1112:
    """
    Reference : AISI S100-16
    Section   : Appendix 1 | 1.1.2
    Topic     : Effective width of webs under stress gradient
    """

    # The effective width, b, shall be calculated as follows:
    # If this procedure is run for strength determination f=fy,
    # If it is run for serviceability determination f=fd (Procedure I)
    def __init__(self, f1, f2, w, t, h0, b0, E, nu, wref):
        # Stress ration of the both ends of the element. f1 is the greater value.
        sRat = abs(f2 / f1)
        # Eq. 1.1.2-2
        k = 4 + 2 * math.pow(1 + sRat, 3) + 2 * (1 + sRat)
        # Calculating the critical buckling stress with Eq. 1.1-2
        fcrl = k * math.pow(math.pi, 2) * E / (12 * (1 - math.pow(nu, 2))) * math.pow(t / w, 2)
        # Calculating the lambda with Eq. 1.1-3
        lam = math.sqrt(f1 / fcrl)
        # Calculating the reduction factor with Eq. 1.1-2
        if lam <= 0.673:
            rho = 1.0
        else:
            rho = (1 - 0.22 / lam) / lam
        # Effective width of the element. Eq. 1.1-1
        be = rho * w
        if h0 / b0 <= 4:
            # Eq. 1.1.2-3
            b1 = be / (3 + sRat)
            if sRat > 0.236:
                # Eq. 1.1.2-4
                b2 = be / 2
            else:
                # Eq. 1.1.2-5
                b2 = be - b1
        else:
            # Eq. 1.1.2-6
            b1 = be / (3 + sRat)
            # Eq. 1.1.2-7
            b2 = be / (1 + sRat) - b1
        if b1 + b2 < wref:
            warnText = "b1+b2<wref | Web is not fully effective for this iteration"
        else:
            warnText = "Web is fully effective."
            rho = 1.0
        # Results
        self.Res_C_App1112 = {
            "f1": f1,
            "f2": f2,
            "a": w,
            "sRat": sRat,
            "k": k,
            "fcrl": fcrl,
            "lam": lam,
            "rho": rho,
            "be": be,
            "b1": b1,
            "b2": b2,
            "wref": wref,
            "warnText": warnText
        }


class C_App1122:
    """
    Reference : AISI S100-16
    Section   : Appendix 1 | 1.1.2.2
    Topic     : Effective width of unstiffened elements with stress gradient
    """

    # The effective width, b, shall be calculated as follows:
    # If this procedure is run for strength determination f=fy,
    # If it is run for serviceability determination f=fd (Procedure I)
    def __init__(self, f1, f2, case, Ri, E, nu, w, t):
        # Stress ration of the both ends of the element. f1 is the greater value.
        sRat = abs(f2 / f1)
        k = 0.0
        if case == 1:
            # Eq. 1.2.2-2
            k = 0.578 / (sRat + 0.34)
        if case == 2:
            # Eq. 1.2.2-3
            k = 0.57 - 0.21 * sRat + 0.07 * pow(sRat, 2)
        if case == 3:
            # Eq. 1.2.2-5
            k = 0.57 + 0.21 * sRat + 0.07 * pow(sRat, 2)
        # Calculating the critical buckling stress with Eq. 1.1-2
        fcrl = k * math.pow(math.pi, 2) * E / (12 * (1 - math.pow(nu, 2))) * math.pow(t / w, 2)
        # Calculating the lambda with Eq. 1.1-3
        lam = math.sqrt(f1 / fcrl)
        if case == 1 or case == 2:
            # Calculating the reduction factor with Eq. 1.1-2
            if lam <= 0.673:
                rho = 1.0
            else:
                rho = (1 - 0.22 / lam) / lam
        if case == 3:
            if lam <= 0.673 * (1 + sRat):
                rho = 1.0
            else:
                rho = (1 + sRat) * (1 - (0.22 * (1 + sRat)) / lam) / lam
        # Effective width of the element. Eq. 1.1-1
        dsp = rho * w
        ds = dsp * Ri
        # Results
        self.Res_C_App1122 = {
            "f1": f1,
            "f2": f2,
            "sRat": sRat,
            "k": k,
            "fcrl": fcrl,
            "lam": lam,
            "rho": rho,
            "dsp": dsp,
            "ds": ds
        }


class C_App113:
    """
    Reference : AISI S100-16
    Section   : Appendix 1 | 1.3
    Topic     : Effective width of uniformly compressed elements with a Simple
    lip edge stiffener
    """

    def __init__(self, w, t, E, f, c, D, nu):
        # Calculating S. Eq. 1.3-7
        S = 1.28 * math.sqrt(E / f)
        if w / t <= 0.328 * S:
            rho = 1
            # Effective width of the element. Eq. 1.1-1
            b = w * rho
            b1 = b / 2
            b2 = b / 2
            Ri = 1
            # results
            self.Res_C_App113 = {
                "w": w,
                "S": S,
                "Ri": Ri,
                "k": "w/t<=0.328xS No need to calculate.",
                "rho": rho,
                "b": b,
                "b1": b1,
                "b2": b2
            }
        else:
            # Calculating the Ia. Eq. 1.3-8
            Ia1 = round(399 * math.pow(t, 4) * math.pow((w / t) / S - 0.328, 3), 5)
            Ia2 = round(math.pow(t, 4) * (115 * (w / t) / S + 5), 5)
            Ia = min(Ia1, Ia2)
            # Calculating the Ri. Eq. 1.3-9 with angle 90 degree
            Is = round((math.pow(c, 3) * t * 1) / 12, 5)
            Ri = min(Is / Ia, 1.0)
            # Eq. 1.3-11
            n = max((0.582 - (w / t) / (4 * S)), 1 / 3)
            # Determination of plate buckling coefficient, k
            k = 0.0
            if D / w <= 0.25:
                k = min(3.57 * math.pow(Ri, n) + 0.43, 4)
            elif 0.25 < D / w <= 0.8:
                k = min((4.82 - 5 * D / w) * math.pow(Ri, n) + 0.43, 4)
            else:
                print("D/w > 0.8")
            # Calculating the critical buckling stress. Eq. 1.1-4
            fcrl = k * math.pow(math.pi, 2) * E / (12 * (1 - math.pow(nu, 2))) * math.pow(t / w, 2)
            # Relative slenderness lambda. Eq. 1.1-3
            lam = math.sqrt(f / fcrl)
            # Reduction factor. Eq. 1.1-2
            rho = (1 - 0.22 / lam) / lam
            if lam <= 0.673:
                rho = 1.0
            else:
                rho = (1 - 0.22 / lam) / lam
            # Effective width of the element. Eq. 1.1-1
            b = w * rho
            b1 = (b / 2) * Ri
            b2 = b - b1
            # results
            self.Res_C_App113 = {
                "w": w,
                "S": S,
                "Ia1": Ia1,
                "Ia2": Ia2,
                "Is": Is,
                "Ia": Ia,
                "Ri": Ri,
                "fcrl": fcrl,
                "n": n,
                "k": k,
                "lam": lam,
                "rho": rho,
                "b": b,
                "b1": b1,
                "b2": b2
            }


class C_SecE21:
    """
    Reference : AISI S100-16
    Section   : Section E2.1
    Topic     : Section not subject to torsional or flexural-torsional buckling
    """

    def __init__(self, K, L, E, I, Ag):
        r = math.sqrt(I / Ag)
        Fcre = math.pow(math.pi, 2) * E / math.pow(K * L / r, 2)
        # results
        self.r = r
        self.Fcre = Fcre


class C_SecE22:
    """
    Reference : AISI S100-16
    Section   : Section E2.2
    Topic     : Singly symmetric sections subject to torsionbal or flexural torsional buckling
    """

    def __init__(self, Kx, Lx, Kt, Lt, E, J, Cw, xo, nu, Ix, Iy, Ag):
        G = E / (2 * (1 + nu))
        rx = math.sqrt(Ix / Ag)
        ry = math.sqrt(Iy / Ag)
        Fex = math.pow(math.pi, 2) * E / math.pow(Kx * Lx / rx, 2)
        ro = math.sqrt(math.pow(rx, 2) + math.pow(ry, 2) + math.pow(xo, 2))
        Fet = (1 / (Ag * math.pow(ro, 2))) * (G * J + (math.pow(math.pi, 2) * E * Cw) / (math.pow(Kt * Lt, 2)))
        beta = 1 - math.pow(xo / ro, 2)
        Fcre = (1 / (2 * beta)) * ((Fex + Fet) - math.sqrt(math.pow(Fex + Fet, 2) - 4 * beta * Fex * Fet))
        # results
        self.ro = ro
        self.Fet = Fet
        self.beta = beta
        self.Fcre = Fcre


class C_SecE2:
    """
    Reference : AISI S100-16
    Section   : Section E2
    Topic     : Yielding and Global buckling
    """

    def __init__(self, Fcre, Fy):
        # Eq. E2-4
        lambdaC = math.sqrt(Fy / Fcre)
        if lambdaC <= 1.5:
            # Eq. E2-2
            Fn = math.pow(0.658, math.pow(lambdaC, 2)) * Fy
        else:
            # Eq. E2-3
            Fn = (0.877 / math.pow(lambdaC, 2)) * Fy
        # results
        self.lambdaC = lambdaC
        self.Fn = Fn
