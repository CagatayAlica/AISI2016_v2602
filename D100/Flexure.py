import math

from fontTools.ufoLib.filenames import maxFileNameLength

# ======================================================================================================================
# CONSTANTS
# ======================================================================================================================
# Section divider for text
secDivider = '============================================'
sp3 = '   '
sp6 = '      '
sp9 = '         '

class Flexure_calc:
    def __init__(self, section, material, factorlocal, factordistortional, Kx, Lx, Ky, Ly, Kt, Lt):
        self.Ag = section.Ar
        self.Ix = section.Ix
        self.Iy = section.Iy
        self.Sf = section.Wx
        self.rx = math.sqrt(self.Ix / self.Ag)
        self.ry = math.sqrt(self.Iy / self.Ag)
        self.J = section.It
        self.Cw = section.Cw
        self.xo = section.xo
        self.ro = math.sqrt(math.pow(self.rx, 2) + math.pow(self.ry, 2) + math.pow(self.xo, 2))
        self.beta = 1 - math.pow(self.xo / self.ro, 2)
        self.fy = material.fy
        self.My = self.Sf*self.fy
        self.E = material.E
        self.G = material.G
        self.Kx = Kx
        self.Lx = Lx
        self.Ky = Ky
        self.Ly = Ly
        self.Kt = Kt
        self.Lt = Lt
        self.Cb = 1.0
        self.ff = 0.90
        self.factorlocal = factorlocal
        self.factordistort = factordistortional
        self.sey = self.eulerBuckling(self.E,self.Ky,self.Ly,self.ry)
        self.set = self.torsionalBuckling(self.Ag,self.ro,self.G,self.J,self.E,self.Cw,self.Kt,self.Lt)
        self.Fcre_t = self.f2_1_1(self.Cb,self.ro,self.Ag,self.Sf,self.sey,self.set)

        self.Mnl = self.f3_2_1(self.My,self.Sf,self.fy,self.factorlocal)[2]
        self.Mnd = self.f4_1(self.Sf,self.fy,self.factordistort)[2]
        self.Mne = self.f2_1(self.Sf,self.fy,self.Fcre_t)[1]
        self.Mn = min(self.Mnl,self.Mnd,self.Mne)
        self.ffMn = self.ff*self.Mn

    def f2_1(self, sf, fy, fcre):
        """
        F2.1 Initiation of Yielding Strength
        :param sf: Elastic section modulus
        :param fy: Yield stress
        :param fcre: Critical elastic lateral-torsional stress
        :return: Fn: flexural stress, Mne: Nominal flexural strength for yielding and global buckling
        """

        if fcre >= 2.78*fy:
            fn = fy
        elif 2.78*fy>fcre>0.56*fy:
            fn = 10.0/9.0*fy*(1-(10.0*fy/(36.0*fcre)))
        else:
            fn = fcre
        mne = sf * fn
        return fn, mne

    def eulerBuckling(self, E, k, l, r):
        """
        Flexural buckling stress. Equation F2.1.1-4.
        :param E: Elastic modulus
        :param k: Member buckling length factor
        :param l: Unbraced length
        :param r: Radius of gyration
        :return: Se: Flexural buckling stress
        """
        se = math.pow(math.pi,2)*E/math.pow(k*l/r,2)
        return se

    def torsionalBuckling(self, A, r, G, J, E, cw, k, l):
        """
        Torsional buckling stress. Equation F2.1.1-5.
        :param A: Gross cross-section area
        :param r: Polar radius of gyration
        :param G: Shear modulus of steel
        :param J: Torsional constant
        :param E: Elastic modulus
        :param cw: Warping constant
        :param k: Member buckling length factor
        :param l: Unbraced length
        :return: set: Torsional buckling stress.
        """
        set=(1.0/(A*math.pow(r,2)))*(G*J+(math.pow(math.pi,2)*E*cw)/math.pow(k*l,2))
        return set

    def f2_1_1(self, cb, ro, A, sf, sey, set):
        """
        F2.1.1 Singly or Doubly Symmetric Sections Bending About Symmetric Axis
        :param cb: 1.0 Eq.F2.1.1-2
        :param ro: Polar radius of gyration
        :param A: Gross cross-sectional area
        :param sf: Elastic section modulus
        :param sey: Flexural buckling stress
        :param set: Torsional buckling stress
        :return: Fcre, The elastic buckling stress Eq. F2.1.1-1
        """
        fcre = (cb*ro*A)/sf*math.sqrt(sey*set)
        return fcre

    def f3_2_1(self, mne, sf, fy, factor):
        """
        F3.2.1 Members Without Holes
        The nominal flexural strength for considering interaction of local buckling and global buckling.
        :param mne: Nominal flexural strength for lateral-torsional buckling strength.
        :param sf: Section modulus.
        :param fy: Yield stress.
        :param factor: Load factor obtained from FSM.
        :return: [0]λl; Slenderness for local buckling, [1]Mcrl; Critical local buckling moment, [2]Mnl; the nominal flexural strength
        """
        Mcrl = sf*fy*factor
        laml = math.sqrt(mne/Mcrl)
        if laml<=0.776:
            Mnl = mne # Eq. F3.2.1-1
        else:
            Mnl = (1-0.15*math.pow(Mcrl/mne,0.4))*math.pow(Mcrl/mne,0.4)*mne # Eq. F3.2.1-2

        return laml, Mcrl, Mnl

    def f4_1(self, sf, fy, factor):
        """
        F4.1 Members Without Holes
        The nominal flexural strength for distortional buckling.        :param sf: Section modulus.
        :param fy: Yield stress.
        :param factor: Load factor obtained from FSM.
        :return: [0]λd; Slenderness for local buckling, [1]Mcrd; Critical distortional buckling moment, [2]Mnd; the nominal flexural strength
        """
        My = sf*fy
        Mcrd = My * factor
        lamd = math.sqrt(My/Mcrd)
        if lamd<=0.673:
            Mnd = My # Eq. F4.1-1
        else:
            Mnd = (1-0.22*math.pow(Mcrd/My,0.5))*math.pow(Mcrd/My,0.5)*My # Eq. F3.2.1-2

        return lamd, Mcrd, Mnd

