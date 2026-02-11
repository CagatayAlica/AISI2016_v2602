import math


# ======================================================================================================================
# CONSTANTS
# ======================================================================================================================
# Section divider for text
secDivider = '============================================'
sp3 = '   '
sp6 = '      '
sp9 = '         '


class Shear_calc:
    def __init__(self, section:object, material:object, dHole: float, lHole:float):
        self.section = section
        self.material = material
        self.dHole = dHole
        self.lHole = lHole
        self.ff = 0.95 # Section G2
        self.Vcr = self.g2_3(section.a, section.t, material.E, material.v)[3]
        self.Vn = self.g2_1(self.Vcr,material.fy,section.a, section.t)[2]
        self.qs = self.g3(section.a,section.t,self.dHole,self.lHole)[0]
        self.Vnh = self.Vn * self.qs
        self.ffVn = self.ff * self.Vn
        self.ffVnh = self.ff * self.Vnh

    def g2_1(self, Vcr:float, fy:float, h:float, t:float):
        """
        G2.1 Flexural Members Without Transverse Web Stiffeners
        :param Vcr:Elastic shear buckling force
        :param fy:Yield stress
        :param h:Flat length of the web
        :param t:Thickness of the web
        :return: [0]Aw: Shear area, [1]Vy: Yield shear force, [2]Vn: Nominal shear strength
        """

        Aw = h*t
        Vy = Aw * fy
        lamv = math.sqrt(Vy/Vcr)
        if lamv <= 0.815:
            Vn = Vy
        elif 0.815 < lamv <= 1.227:
            Vn = 0.815 * math.sqrt(Vcr * Vy)
        else:
            Vn = Vcr
        return Aw, Vy, Vn

    def g2_3(self, h:float, t:float, E:float, v:float):
        """
        G2.3 Web Elastic critical Shear Buckling Force, Vcr
        :param h: Flat length of the web
        :param t: Thickness of the web
        :param E: Elastic modulus
        :param v: Poisson's ratio
        :return: [0]Aw: Shear area, [1]kv: Shear buckling coefficient, [2]Fcr: Elastic shear buckling stress, [3]Vcr: Shear buckling force
        """
        Aw = h * t
        kv = 5.34 # webs without stiffeners Section G2.3
        Fcr = (math.pow(math.pi,2)*E*kv)/(12.0*(1-math.pow(v,2))*math.pow(h/t,2))
        Vcr = Fcr * Aw
        return Aw, kv, Fcr, Vcr

    def g3(self, h:float, t:float, dh:float, lh:float):
        """
        G3 Shear Strength of C-Section Webs With Holes.
        :param h: Flat length of the web.
        :param t: Thickness of the web.
        :param dh: Hole width. In the direction aligned with the web.
        :param lh: Hole length. In the direction aligned with the profile.
        :return: [0]qs, Reduction factor. [1]note, Calculation note.
        """

        note : str = f'Shear strength of web with holes.\n'
        # if length of the hole is shorter than the width, the hole is assumed as circular.
        if lh <= dh : dh = lh

        safeRatio = dh / h
        if safeRatio > 0.7 : note += f'Ratio is over 0.7, dh/h = {safeRatio:.3f)}! Check AISI S100 G3(a).'
        hRatio = h/t
        if hRatio > 200: note += f'Ratio is over 200, h/t = {hRatio:.3f)}! Check AISI S100 G3(b).'

        if lh>dh:
            # for noncircular hole
            c = h/2 - dh/2
            note+= f'c value for noncircular hole is {c:.3f}'
        else:
            # for circular hole
            c = h/2 - dh/2.83
            note += f'c value for circular hole is {c:.3f}'

        if c/t >= 54:
            qs = 1.0
            note += f'c/t ≥ 54, qs = {c:.3f}'
        elif 5<= c/t < 54:
            qs = c/(54.0 * t)
            note += f'5 ≤ c/t < 54, qs = {c:.3f}'
        else:
            qs = 0
            note += f'c/t < 5 value is {qs:.3f}'

        # Create a dictionary of all relevant data
        data_log = {
                "clause": "AISI S100 G3, Shear Strength of C-Section Webs With Holes",
                "inputs": {
                    "h": h,
                    "t": t,
                    "dh": dh,
                    "lh": lh
                },
                "output": {
                    "qs": qs
                },
                "report":{note}
            }

        return qs, note

