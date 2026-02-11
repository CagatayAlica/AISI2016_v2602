import numpy as np
from typing import Literal
import math
import matplotlib.pyplot as plt

def rotateCoordinates(XY, angle):
    # Shape of the input matrix
    num_rows, num_cols = XY.shape
    # Creating a dummy zeros matrix
    dummyzeros = np.zeros(num_cols)
    # Adding dummy zeros
    SectionWithZeros = np.vstack([XY, dummyzeros])
    # Cosine and sines
    c, s = np.cos(math.radians(angle)), np.sin(math.radians(angle))
    j = np.array([[c, s, 0],
                  [-s, c, 0],
                  [0, 0, 1]])
    # Multiply with transformation matrix
    RotatedCoordinates = np.matmul(j, SectionWithZeros)
    # Remove the dummy zeros
    RotatedCoordinates = np.delete(RotatedCoordinates, 2, 0)
    return XY, RotatedCoordinates

class C_Section:
    def __init__(self, A: float, B: float, C: float, t: float, R: float, angle: Literal[0, 90, 180, 270],
                 material):
        """
        Lipped C section definition and gross properties
        :param A: Web height
        :param B: Flange width
        :param C: Lip length
        :param t: Nominal thickness
        :param R: Inner radius
        :param angle: Orientation angle in degrees
        """
        self.ry = None
        self.rx = None
        self.descp_Plot_inches = None
        self.propDict_imperial = None
        self.E = material.E
        self.fy = material.fy
        self.v = material.v
        self.matname = material.name
        self.A = A
        self.B = B
        self.C = C
        self.t = t
        self.R = R
        self.angle = angle
        self.aa = None
        self.bb = None
        self.cc = None
        self.tcore = None
        self.a = None
        self.b = None
        self.c = None
        self.r = None
        self.nodes = np.array([[]])
        self.elements = None
        self.descp_rep = None
        self.descp_Plot = None
        self.centerline()
        self.coordinates()
        self.ang_shape = None
        self.orientation(self.angle)
        self.Wy = None
        self.Wx = None
        self.propDict = None
        self.cy = None
        self.cx = None
        self.zgr = None
        self.zgl = None
        self.zgt = None
        self.zgb = None
        self.xo = None
        self.It = None
        self.Cw = None
        self.ysc = None
        self.xsc = None
        self.Ixy = None
        self.Iy = None
        self.Ix = None
        self.zgx = None
        self.zgy = None
        self.Ar = None
        self.calculateGross()

    def centerline(self):
        self.r = self.R + self.t / 2.0
        # Centerline dimensions
        self.aa = self.A - self.t
        self.bb = self.B - self.t
        self.cc = self.C - self.t / 2.0
        self.tcore = self.t - 0.04
        # Flat portions
        self.a = self.aa - 2 * self.r
        self.b = self.bb - 2 * self.r
        self.c = self.cc - self.r

    def tranform(self, alfa, origin):
        # Transformation matrix
        p = origin
        c, s = np.cos(math.radians(alfa)), np.sin(math.radians(alfa))
        j = np.array([[c, s, 0],
                      [-s, c, 0],
                      [0, 0, 1]])
        RotatedCorners = np.matmul(j, p)
        return RotatedCorners.T

    def coordinates(self):
        # Bottom right
        origin1 = np.array([self.bb - self.r, self.r, 0.0])
        radius = np.array([0, self.r, 0.0])
        start_ang = 90
        p11 = self.tranform(start_ang + 10, radius)
        p12 = self.tranform(start_ang + 20, radius)
        p13 = self.tranform(start_ang + 30, radius)
        p14 = self.tranform(start_ang + 40, radius)
        p15 = self.tranform(start_ang + 50, radius)
        p16 = self.tranform(start_ang + 60, radius)
        p17 = self.tranform(start_ang + 70, radius)
        p18 = self.tranform(start_ang + 80, radius)
        # Bottom left
        origin2 = np.array([self.r, self.r, 0.0])
        start_ang = 180
        p21 = self.tranform(start_ang + 10, radius)
        p22 = self.tranform(start_ang + 20, radius)
        p23 = self.tranform(start_ang + 30, radius)
        p24 = self.tranform(start_ang + 40, radius)
        p25 = self.tranform(start_ang + 50, radius)
        p26 = self.tranform(start_ang + 60, radius)
        p27 = self.tranform(start_ang + 70, radius)
        p28 = self.tranform(start_ang + 80, radius)
        # Top left
        origin3 = np.array([self.r, self.aa - self.r, 0.0])
        start_ang = 270
        p31 = self.tranform(start_ang + 10, radius)
        p32 = self.tranform(start_ang + 20, radius)
        p33 = self.tranform(start_ang + 30, radius)
        p34 = self.tranform(start_ang + 40, radius)
        p35 = self.tranform(start_ang + 50, radius)
        p36 = self.tranform(start_ang + 60, radius)
        p37 = self.tranform(start_ang + 70, radius)
        p38 = self.tranform(start_ang + 80, radius)
        # Top right
        origin4 = np.array([self.bb - self.r, self.aa - self.r, 0.0])
        start_ang = 0
        p41 = self.tranform(start_ang + 10, radius)
        p42 = self.tranform(start_ang + 20, radius)
        p43 = self.tranform(start_ang + 30, radius)
        p44 = self.tranform(start_ang + 40, radius)
        p45 = self.tranform(start_ang + 50, radius)
        p46 = self.tranform(start_ang + 60, radius)
        p47 = self.tranform(start_ang + 70, radius)
        p48 = self.tranform(start_ang + 80, radius)

        self.Csection = np.array([[self.bb, self.cc],
                                  [self.bb, self.r],
                                  [origin1[0] + p11[0], origin1[1] + p11[1]],
                                  [origin1[0] + p12[0], origin1[1] + p12[1]],
                                  [origin1[0] + p13[0], origin1[1] + p13[1]],
                                  [origin1[0] + p14[0], origin1[1] + p14[1]],
                                  [origin1[0] + p15[0], origin1[1] + p15[1]],
                                  [origin1[0] + p16[0], origin1[1] + p16[1]],
                                  [origin1[0] + p17[0], origin1[1] + p17[1]],
                                  [origin1[0] + p18[0], origin1[1] + p18[1]],
                                  [self.bb - self.r, 0],
                                  [self.r + self.b / 2.0, 0],
                                  [self.r, 0],
                                  [origin2[0] + p21[0], origin2[1] + p21[1]],
                                  [origin2[0] + p22[0], origin2[1] + p22[1]],
                                  [origin2[0] + p23[0], origin2[1] + p23[1]],
                                  [origin2[0] + p24[0], origin2[1] + p24[1]],
                                  [origin2[0] + p25[0], origin2[1] + p25[1]],
                                  [origin2[0] + p26[0], origin2[1] + p26[1]],
                                  [origin2[0] + p27[0], origin2[1] + p27[1]],
                                  [origin2[0] + p28[0], origin2[1] + p28[1]],
                                  [0, self.r],
                                  [0, self.r + self.a * (1.0 / 4.0)],
                                  [0, self.r + self.a * (2.0 / 4.0)],
                                  [0, self.r + self.a * (3.0 / 4.0)],
                                  [0, self.r + self.a],
                                  [origin3[0] + p31[0], origin3[1] + p31[1]],
                                  [origin3[0] + p32[0], origin3[1] + p32[1]],
                                  [origin3[0] + p33[0], origin3[1] + p33[1]],
                                  [origin3[0] + p34[0], origin3[1] + p34[1]],
                                  [origin3[0] + p35[0], origin3[1] + p35[1]],
                                  [origin3[0] + p36[0], origin3[1] + p36[1]],
                                  [origin3[0] + p37[0], origin3[1] + p37[1]],
                                  [origin3[0] + p38[0], origin3[1] + p38[1]],
                                  [self.r, self.aa],
                                  [self.r + self.b / 2.0, self.aa],
                                  [self.bb - self.r, self.aa],
                                  [origin4[0] + p41[0], origin4[1] + p41[1]],
                                  [origin4[0] + p42[0], origin4[1] + p42[1]],
                                  [origin4[0] + p43[0], origin4[1] + p43[1]],
                                  [origin4[0] + p44[0], origin4[1] + p44[1]],
                                  [origin4[0] + p45[0], origin4[1] + p45[1]],
                                  [origin4[0] + p46[0], origin4[1] + p46[1]],
                                  [origin4[0] + p47[0], origin4[1] + p47[1]],
                                  [origin4[0] + p48[0], origin4[1] + p48[1]],
                                  [self.bb, self.aa - self.r],
                                  [self.bb, self.aa - self.cc]])
        # =================

        # Function call for rotation
        Csection, RotatedCsection = rotateCoordinates(self.Csection.T, self.angle)
        # Create id numbers for each row
        numbers = np.arange(RotatedCsection.shape[1], dtype=int)
        # Adding id numbers to the coordinates matrix
        CsectionWithNumbers = np.vstack([numbers, RotatedCsection])

        # Creating ones
        ones = np.ones((4, RotatedCsection.shape[1]))
        # Adding one numbers to the coordinates matrix
        CsectionWithNumbers = np.vstack([CsectionWithNumbers, ones])
        # Creating zeros
        zeros = np.zeros((RotatedCsection.shape[1]))
        # Adding zeros to the coordinates matrix
        CsectionWithNumbers = np.vstack([CsectionWithNumbers, zeros])

        # ===================================
        # Final nodes and elements for Opensees
        # ===================================
        self.nodes = CsectionWithNumbers.T
        # If angle is 90, shift section as flange width in Y dir.
        # If angle is 270, shift section as web height in X dir.
        if self.angle == 90:
            for i in self.nodes:
                i[2] = i[2] + self.B
        elif self.angle == 270:
            for i in self.nodes:
                i[1] = i[1] + self.A

        # Shape of the node matrix
        num_cols, num_rows = Csection.shape
        self.elements = np.empty([num_rows - 1, 5])
        for i in range(num_rows - 1):
            self.elements[i, 0] = i
            self.elements[i, 1] = i
            self.elements[i, 2] = i + 1
            self.elements[i, 3] = self.t
            self.elements[i, 4] = 0

        self.descp_Plot = f'Section :C {self.A:.3f} x {self.B:.3f} x {self.C:.3f} - {self.t:.3f}'
        self.descp_Plot_inches = f'Section :C {self.A/25.4:.3f} x {self.B/25.4:.3f} x {self.C/25.4:.3f} - {self.t/25.4:.4f}'
        self.descp_rep = (f'Section :C {self.A:.3f} x {self.B:.3f} x {self.C:.3f} - {self.t:.3f}\n'
                          f'   A:{self.A:.3f} in, Web height\n'
                          f'   B:{self.B:.3f} in, Flange width\n'
                          f'   C:{self.C:.3f} in, Lip length\n'
                          f'   R:{self.R:.3f} in, Inner radius\n'
                          f'   t:{self.t:.3f} in, Thickness')

    def orientation(self, angle):
        if angle == 0:
            self.ang_shape = (f'      ┌-┐\n'
                              f'        |\n'
                              f'      └-┘\n')
        elif angle == 270:
            self.ang_shape = (f'   ┌   ┐\n'
                              f'   └---┘\n')
        else:
            self.ang_shape = (f'  ┌---┐\n'
                              f'  └   ┘\n')

    def calculateGross(self):
        x = self.nodes[:, 1]
        y = self.nodes[:, 2]
        t = self.t
        r = self.r
        # Area of cross section
        da = np.zeros([len(x)])
        ba = np.zeros([len(x)])
        for i in range(1, len(da)):
            da[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2)) * t
            ba[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2))
        self.Ar = np.sum(da)
        Lt = np.sum(ba)
        # Total rj.tetaj/90
        Trj = 4 * 4 * r * (1.0 / 4.0)
        delta = 0.43 * Trj / Lt
        # First moment of area and coordinate for gravity centre
        sx0 = np.zeros([len(x)])
        sy0 = np.zeros([len(x)])
        for i in range(1, len(sx0)):
            sx0[i] = (y[i] + y[i - 1]) * da[i] / 2
        self.zgy = np.sum(sx0) / self.Ar
        for i in range(1, len(sy0)):
            sy0[i] = (x[i] + x[i - 1]) * da[i] / 2
        self.zgx = np.sum(sy0) / self.Ar

        # Second moment of area
        Ix0 = np.zeros([len(x)])
        Iy0 = np.zeros([len(x)])
        for i in range(1, len(Ix0)):
            Ix0[i] = (math.pow(y[i], 2) + math.pow(y[i - 1], 2) + y[i] * y[i - 1]) * da[i] / 3
        for i in range(1, len(Iy0)):
            Iy0[i] = (math.pow(x[i], 2) + math.pow(x[i - 1], 2) + x[i] * x[i - 1]) * da[i] / 3
        self.Ix = np.sum(Ix0) - self.Ar * math.pow(self.zgy, 2)
        self.Iy = np.sum(Iy0) - self.Ar * math.pow(self.zgx, 2)

        # Product moment of area
        Ixy0 = np.zeros([len(x)])
        for i in range(1, len(Ixy0)):
            Ixy0[i] = (2 * x[i - 1] * y[i - 1] + 2 * x[i] * y[i] + x[i - 1] * y[i] + x[i] * y[i - 1]) * da[i] / 6
        self.Ixy = np.sum(Ixy0) - (np.sum(sx0) * np.sum(sy0)) / self.Ar

        # Principle axis
        alfa = 0.5 * math.atan(2 * self.Ixy / (self.Iy - self.Ix))
        Iksi = 0.5 * (self.Ix + self.Iy + math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))
        Ieta = 0.5 * (self.Ix + self.Iy - math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))

        # Sectoral coordinates
        w = np.zeros([len(x)])
        w0 = np.zeros([len(x)])
        Iw = np.zeros([len(x)])
        w0[0] = 0
        for i in range(1, len(w0)):
            w0[i] = x[i - 1] * y[i] - x[i] * y[i - 1]
            w[i] = w[i - 1] + w0[i]
            Iw[i] = (w[i - 1] + w[i]) * da[i] / 2
        wmean = np.sum(Iw) / self.Ar

        # Sectorial constants
        Ixw0 = np.zeros([len(x)])
        Iyw0 = np.zeros([len(x)])
        Iww0 = np.zeros([len(x)])
        for i in range(1, len(Ixw0)):
            Ixw0[i] = (2 * x[i - 1] * w[i - 1] + 2 * x[i] * w[i] + x[i - 1] * w[i] + x[i] * w[i - 1]) * da[i] / 6
            Iyw0[i] = (2 * y[i - 1] * w[i - 1] + 2 * y[i] * w[i] + y[i - 1] * w[i] + y[i] * w[i - 1]) * da[i] / 6
            Iww0[i] = (math.pow(w[i], 2) + math.pow(w[i - 1], 2) + w[i] * w[i - 1]) * da[i] / 3
        Ixw = np.sum(Ixw0) - np.sum(sy0) * np.sum(Iw) / self.Ar
        Iyw = np.sum(Iyw0) - np.sum(sx0) * np.sum(Iw) / self.Ar
        Iww = np.sum(Iww0) - math.pow(np.sum(Iw), 2) / self.Ar

        # Shear centre
        self.xsc = (Iyw * self.Iy - Ixw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))
        self.ysc = (-Ixw * self.Ix + Iyw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))

        # Warping constant
        self.Cw = Iww + self.ysc * Ixw - self.xsc * Iyw

        # Torsion constant
        It0 = np.zeros([len(x)])
        for i in range(1, len(It0)):
            It0[i] = da[i] * math.pow(t, 2) / 3
        self.It = np.sum(It0)

        # Distance between centroid and shear centre
        self.xo = abs(self.xsc) + self.zgx
        # Distances from the boundaries
        self.zgb = self.zgy
        self.zgt = max(y) - self.zgb
        self.zgl = self.zgx
        self.zgr = max(x) - self.zgl
        self.cx = max(self.zgl, self.zgr)
        self.cy = max(self.zgb, self.zgt)
        # Section modulus
        self.Wx = self.Ix / max(self.zgb, self.zgt)
        self.Wy = self.Iy / max(self.zgl, self.zgr)

        self.rx = math.sqrt(self.Ix / self.Ar)
        self.ry = math.sqrt(self.Iy / self.Ar)
        # Data dictionary
        self.propDict = {
            "Ar ": str(round(self.Ar, 3)) + " mm2",
            "zgx ": str(round(self.zgx, 3)) + " mm",
            "zgy ": str(round(self.zgy, 3)) + " mm",
            "Ix ": str(round(self.Ix, 3)) + " mm4",
            "Wx ": str(round(self.Ix / max(self.zgb, self.zgt), 3)) + " mm3",
            "rx ": str(round(math.sqrt(self.Ix / self.Ar), 3)) + " mm",
            "Iy ": str(round(self.Iy, 3)) + " mm4",
            "Wy ": str(round(self.Iy / max(self.zgl, self.zgr), 3)) + " mm3",
            "ry ": str(round(math.sqrt(self.Iy / self.Ar), 3)) + " mm",
            "Ixy ": str(round(self.Ixy, 3)) + " mm4",
            "Iw ": str(round(np.sum(self.Cw), 5)) + " mm3",
            "xsc ": str(round(self.xsc, 3)) + " mm",
            "ysc ": str(round(self.ysc, 3)) + " mm",
            "Cw ": str(round(self.Cw, 5)) + " mm6",
            "It ": str(round(self.It, 5)) + " mm4",
            "xo ": str(round(self.xo, 3)) + " mm",
            "ro ": str(round(math.sqrt(math.sqrt(self.Ix / self.Ar)**2+math.sqrt(self.Iy / self.Ar)**2+self.xo**2), 3)) + " mm"
        }
        self.propDict_imperial = {
            "Ar ": str(round(self.Ar/25.4**2, 3)) + " in2",
            "zgx ": str(round(self.zgx/25.4, 3)) + " in",
            "zgy ": str(round(self.zgy/25.4, 3)) + " in",
            "Ix ": str(round(self.Ix/25.4**4, 3)) + " in4",
            "Wx ": str(round((self.Ix / max(self.zgb, self.zgt))/25.4**3, 3)) + " in3",
            "rx ": str(round(math.sqrt(self.Ix / self.Ar)/25.4**3, 3)) + " in",
            "Iy ": str(round(self.Iy/25.4**4, 3)) + " in4",
            "Wy ": str(round((self.Iy / max(self.zgl, self.zgr))/25.4**3, 3)) + " in3",
            "ry ": str(round(math.sqrt(self.Iy / self.Ar) / 25.4 ** 3, 3)) + " in",
            "Ixy ": str(round(self.Ixy/25.4**4, 3)) + " in4",
            "Iw ": str(round(np.sum(self.Cw)/25.4**3, 5)) + " in3",
            "xsc ": str(round(self.xsc/25.4, 3)) + " in",
            "ysc ": str(round(self.ysc/25.4, 3)) + " in",
            "Cw ": str(round(self.Cw/25.4**6, 5)) + " in6",
            "It ": str(round(self.It/25.4**4, 5)) + " in4",
            "xo ": str(round(self.xo/25.4, 3)) + " in",
            "ro ": str(
                round(math.sqrt(math.sqrt(self.Ix / self.Ar) ** 2 + math.sqrt(self.Iy / self.Ar) ** 2 + self.xo ** 2)/25.4,
                      3)) + " mm"
        }

    def __str__(self):
        rep = 'GROSS SECTION PROPERTIES \n'
        rep += f"Section {self.descp_Plot}"
        return rep

class U_Section:
    def __init__(self, A: float, B: float, t: float, R: float, angle: Literal[0, 90, 270],
                 material):
        """
        Lipped C section definition and gross properties
        :param A: Web height in mm
        :param B: Flange width in mm
        :param C: Lip length in mm
        :param t: Nominal thickness in mm
        :param R: Inner radius in mm
        :param angle: Orientation angle in degrees
        """
        self.Usection = None
        self.E = material.E
        self.fy = material.fy
        self.v = material.v
        self.matname = material.name
        self.A = A
        self.B = B
        self.t = t
        self.R = R
        self.angle = angle
        self.aa = None
        self.bb = None
        self.tcore = None
        self.a = None
        self.b = None
        self.r = None
        self.nodes = np.array([[]])
        self.elements = None
        self.descp_rep = None
        self.descp_Plot = None
        self.centerline()
        self.coordinates()
        self.ang_shape = None
        self.orientation(self.angle)
        self.Wy = None
        self.Wx = None
        self.propDict = None
        self.cy = None
        self.cx = None
        self.zgr = None
        self.zgl = None
        self.zgt = None
        self.zgb = None
        self.xo = None
        self.It = None
        self.Cw = None
        self.ysc = None
        self.xsc = None
        self.Ixy = None
        self.Iy = None
        self.Ix = None
        self.zgx = None
        self.zgy = None
        self.Ar = None
        self.calculateGross()

    def centerline(self):
        self.r = self.R + self.t / 2.0
        # Centerline dimensions
        self.aa = self.A - self.t
        self.bb = self.B - self.t / 2.0
        self.tcore = self.t - 0.04
        # Flat portions
        self.a = self.aa - 2 * self.r
        self.b = self.bb - self.r

    def tranform(self, alfa, origin):
        # Transformation matrix
        p = origin
        c, s = np.cos(math.radians(alfa)), np.sin(math.radians(alfa))
        j = np.array([[c, s, 0],
                      [-s, c, 0],
                      [0, 0, 1]])
        RotatedCorners = np.matmul(j, p)
        return RotatedCorners.T

    def coordinates(self):
        # Bottom right
        radius = np.array([0, self.r, 0.0])

        # Bottom left
        origin2 = np.array([self.r, self.r, 0.0])
        start_ang = 180
        p21 = self.tranform(start_ang + 10, radius)
        p22 = self.tranform(start_ang + 20, radius)
        p23 = self.tranform(start_ang + 30, radius)
        p24 = self.tranform(start_ang + 40, radius)
        p25 = self.tranform(start_ang + 50, radius)
        p26 = self.tranform(start_ang + 60, radius)
        p27 = self.tranform(start_ang + 70, radius)
        p28 = self.tranform(start_ang + 80, radius)
        # Top left
        origin3 = np.array([self.r, self.aa - self.r, 0.0])
        start_ang = 270
        p31 = self.tranform(start_ang + 10, radius)
        p32 = self.tranform(start_ang + 20, radius)
        p33 = self.tranform(start_ang + 30, radius)
        p34 = self.tranform(start_ang + 40, radius)
        p35 = self.tranform(start_ang + 50, radius)
        p36 = self.tranform(start_ang + 60, radius)
        p37 = self.tranform(start_ang + 70, radius)
        p38 = self.tranform(start_ang + 80, radius)
        # Top right
        start_ang = 0

        self.Usection = np.array([[self.bb, 0],
                                  [self.r + self.b / 2.0, 0],
                                  [self.r, 0],
                                  [origin2[0] + p21[0], origin2[1] + p21[1]],
                                  [origin2[0] + p22[0], origin2[1] + p22[1]],
                                  [origin2[0] + p23[0], origin2[1] + p23[1]],
                                  [origin2[0] + p24[0], origin2[1] + p24[1]],
                                  [origin2[0] + p25[0], origin2[1] + p25[1]],
                                  [origin2[0] + p26[0], origin2[1] + p26[1]],
                                  [origin2[0] + p27[0], origin2[1] + p27[1]],
                                  [origin2[0] + p28[0], origin2[1] + p28[1]],
                                  [0, self.r],
                                  [0, self.r + self.a * (1.0 / 4.0)],
                                  [0, self.r + self.a * (2.0 / 4.0)],
                                  [0, self.r + self.a * (3.0 / 4.0)],
                                  [0, self.r + self.a],
                                  [origin3[0] + p31[0], origin3[1] + p31[1]],
                                  [origin3[0] + p32[0], origin3[1] + p32[1]],
                                  [origin3[0] + p33[0], origin3[1] + p33[1]],
                                  [origin3[0] + p34[0], origin3[1] + p34[1]],
                                  [origin3[0] + p35[0], origin3[1] + p35[1]],
                                  [origin3[0] + p36[0], origin3[1] + p36[1]],
                                  [origin3[0] + p37[0], origin3[1] + p37[1]],
                                  [origin3[0] + p38[0], origin3[1] + p38[1]],
                                  [self.r, self.aa],
                                  [self.r + self.b / 2.0, self.aa],
                                  [self.bb, self.aa]])
        # =================

        # Function call for rotation
        Usection, RotatedCsection = rotateCoordinates(self.Usection.T, self.angle)
        # Create id numbers for each row
        numbers = np.arange(RotatedCsection.shape[1], dtype=int)
        # Adding id numbers to the coordinates matrix
        UsectionWithNumbers = np.vstack([numbers, RotatedCsection])

        # Creating ones
        ones = np.ones((4, RotatedCsection.shape[1]))
        # Adding one numbers to the coordinates matrix
        UsectionWithNumbers = np.vstack([UsectionWithNumbers, ones])
        # Creating zeros
        zeros = np.zeros((RotatedCsection.shape[1]))
        # Adding zeros to the coordinates matrix
        UsectionWithNumbers = np.vstack([UsectionWithNumbers, zeros])

        # ===================================
        # Final nodes and elements for Opensees
        # ===================================
        self.nodes = UsectionWithNumbers.T
        # If angle is 90, shift section as flange width in Y dir.
        # If angle is 270, shift section as web height in X dir.
        if self.angle == 90:
            for i in self.nodes:
                i[2] = i[2] + self.B
        elif self.angle == 270:
            for i in self.nodes:
                i[1] = i[1] + self.A

        # Shape of the node matrix
        num_cols, num_rows = Usection.shape
        self.elements = np.empty([num_rows - 1, 5])
        for i in range(num_rows - 1):
            self.elements[i, 0] = i
            self.elements[i, 1] = i
            self.elements[i, 2] = i + 1
            self.elements[i, 3] = self.t
            self.elements[i, 4] = 0

        self.descp_Plot = f'Section :U {self.A:.3f} x {self.B:.3f} - {self.t:.3f}'
        self.descp_rep = (f'Section :U {self.A:.3f} x {self.B:.3f} - {self.t:.3f}\n'
                          f'   A:{self.A:.3f} in, Web height\n'
                          f'   B:{self.B:.3f} in, Flange width\n'
                          f'   R:{self.R:.3f} in, Inner radius\n'
                          f'   t:{self.t:.3f} in, Thickness')

    def orientation(self, angle):
        if angle == 0:
            self.ang_shape = (f'   -┐\n'
                              f'    |\n'
                              f'   -┘\n')
        elif angle == 270:
            self.ang_shape = (f'       \n'
                              f'  └---┘\n')
        else:
            self.ang_shape = (f'  ┌---┐\n'
                              f'       \n')

    def calculateGross(self):
        x = self.nodes[:, 1]
        y = self.nodes[:, 2]
        t = self.t
        r = self.r
        # Area of cross section
        da = np.zeros([len(x)])
        ba = np.zeros([len(x)])
        for i in range(1, len(da)):
            da[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2)) * t
            ba[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2))
        self.Ar = np.sum(da)
        Lt = np.sum(ba)
        # Total rj.tetaj/90
        Trj = 4 * 4 * r * (1.0 / 4.0)
        delta = 0.43 * Trj / Lt
        # First moment of area and coordinate for gravity centre
        sx0 = np.zeros([len(x)])
        sy0 = np.zeros([len(x)])
        for i in range(1, len(sx0)):
            sx0[i] = (y[i] + y[i - 1]) * da[i] / 2
        self.zgy = np.sum(sx0) / self.Ar
        for i in range(1, len(sy0)):
            sy0[i] = (x[i] + x[i - 1]) * da[i] / 2
        self.zgx = np.sum(sy0) / self.Ar

        # Second moment of area
        Ix0 = np.zeros([len(x)])
        Iy0 = np.zeros([len(x)])
        for i in range(1, len(Ix0)):
            Ix0[i] = (math.pow(y[i], 2) + math.pow(y[i - 1], 2) + y[i] * y[i - 1]) * da[i] / 3
        for i in range(1, len(Iy0)):
            Iy0[i] = (math.pow(x[i], 2) + math.pow(x[i - 1], 2) + x[i] * x[i - 1]) * da[i] / 3
        self.Ix = np.sum(Ix0) - self.Ar * math.pow(self.zgy, 2)
        self.Iy = np.sum(Iy0) - self.Ar * math.pow(self.zgx, 2)

        # Product moment of area
        Ixy0 = np.zeros([len(x)])
        for i in range(1, len(Ixy0)):
            Ixy0[i] = (2 * x[i - 1] * y[i - 1] + 2 * x[i] * y[i] + x[i - 1] * y[i] + x[i] * y[i - 1]) * da[i] / 6
        self.Ixy = np.sum(Ixy0) - (np.sum(sx0) * np.sum(sy0)) / self.Ar

        # Principle axis
        alfa = 0.5 * math.atan(2 * self.Ixy / (self.Iy - self.Ix))
        Iksi = 0.5 * (self.Ix + self.Iy + math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))
        Ieta = 0.5 * (self.Ix + self.Iy - math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))

        # Sectoral coordinates
        w = np.zeros([len(x)])
        w0 = np.zeros([len(x)])
        Iw = np.zeros([len(x)])
        w0[0] = 0
        for i in range(1, len(w0)):
            w0[i] = x[i - 1] * y[i] - x[i] * y[i - 1]
            w[i] = w[i - 1] + w0[i]
            Iw[i] = (w[i - 1] + w[i]) * da[i] / 2
        wmean = np.sum(Iw) / self.Ar

        # Sectorial constants
        Ixw0 = np.zeros([len(x)])
        Iyw0 = np.zeros([len(x)])
        Iww0 = np.zeros([len(x)])
        for i in range(1, len(Ixw0)):
            Ixw0[i] = (2 * x[i - 1] * w[i - 1] + 2 * x[i] * w[i] + x[i - 1] * w[i] + x[i] * w[i - 1]) * da[i] / 6
            Iyw0[i] = (2 * y[i - 1] * w[i - 1] + 2 * y[i] * w[i] + y[i - 1] * w[i] + y[i] * w[i - 1]) * da[i] / 6
            Iww0[i] = (math.pow(w[i], 2) + math.pow(w[i - 1], 2) + w[i] * w[i - 1]) * da[i] / 3
        Ixw = np.sum(Ixw0) - np.sum(sy0) * np.sum(Iw) / self.Ar
        Iyw = np.sum(Iyw0) - np.sum(sx0) * np.sum(Iw) / self.Ar
        Iww = np.sum(Iww0) - math.pow(np.sum(Iw), 2) / self.Ar

        # Shear centre
        self.xsc = (Iyw * self.Iy - Ixw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))
        self.ysc = (-Ixw * self.Ix + Iyw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))

        # Warping constant
        self.Cw = Iww + self.ysc * Ixw - self.xsc * Iyw

        # Torsion constant
        It0 = np.zeros([len(x)])
        for i in range(1, len(It0)):
            It0[i] = da[i] * math.pow(t, 2) / 3
        self.It = np.sum(It0)

        # Distance between centroid and shear centre
        self.xo = abs(self.xsc) + self.zgx
        # Distances from the boundaries
        self.zgb = self.zgy
        self.zgt = max(y) - self.zgb
        self.zgl = self.zgx
        self.zgr = max(x) - self.zgl
        self.cx = max(self.zgl, self.zgr)
        self.cy = max(self.zgb, self.zgt)
        # Section modulus
        self.Wx = self.Ix / max(self.zgb, self.zgt)
        self.Wy = self.Iy / max(self.zgl, self.zgr)

        # Data dictionary
        self.propDict = {
            "Ar ": str(round(self.Ar, 3)) + " mm2",
            "zgx ": str(round(self.zgx, 3)) + " mm",
            "zgy ": str(round(self.zgy, 3)) + " mm",
            "Ix ": str(round(self.Ix, 3)) + " mm4",
            "Wx ": str(round(self.Ix / max(self.zgb, self.zgt), 3)) + " mm3",
            "Iy ": str(round(self.Iy, 3)) + " mm4",
            "Wy ": str(round(self.Iy / max(self.zgl, self.zgr), 3)) + " mm3",
            "Ixy ": str(round(self.Ixy, 3)) + " mm4",
            "Iw ": str(round(np.sum(self.Cw), 5)) + " mm3",
            "xsc ": str(round(self.xsc, 3)) + " mm",
            "ysc ": str(round(self.ysc, 3)) + " mm",
            "Cw ": str(round(self.Cw, 5)) + " mm6",
            "It ": str(round(self.It, 5)) + " mm4",
            "xo ": str(round(self.xo, 3)) + " mm"
        }

class Omega_Section:
    def __init__(self, A: float, B: float, C: float, D: float, t: float, R: float, angle: Literal[0, 90, 180, 270],
                 material):
        """
        Lipped C section definition and gross properties
        :param A: Web height in mm
        :param B: Flange width in mm
        :param C: Lip length in mm
        :param t: Nominal thickness in mm
        :param R: Inner radius in mm
        :param angle: Orientation angle in degrees
        """


        self.propDict_imperial = None
        self.E = material.E
        self.fy = material.fy
        self.v = material.v
        self.matname = material.name
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.t = t
        self.R = R
        self.angle = angle
        self.aa = None
        self.bb = None
        self.cc = None
        self.dd = None
        self.tcore = None
        self.a = None
        self.b = None
        self.c = None
        self.d = None
        self.r = None
        self.nodes = np.array([[]])
        self.elements = None
        self.descp_rep = None
        self.descp_Plot = None
        self.centerline()
        self.coordinates()
        self.ang_shape = None
        self.orientation(self.angle)
        self.Wy = None
        self.Wx = None
        self.propDict = None
        self.cy = None
        self.cx = None
        self.zgr = None
        self.zgl = None
        self.zgt = None
        self.zgb = None
        self.xo = None
        self.It = None
        self.Cw = None
        self.ysc = None
        self.xsc = None
        self.Ixy = None
        self.Iy = None
        self.Ix = None
        self.zgx = None
        self.zgy = None
        self.Ar = None
        self.calculateGross()
        self.plotter(False)

    def centerline(self):
        self.r = self.R + self.t / 2.0
        # Centerline dimensions
        self.aa = self.A - self.t
        self.bb = self.B - self.t
        self.cc = self.C - self.t
        self.dd = self.D - self.t / 2.0
        self.tcore = self.t - 0.04
        # Flat portions
        self.a = self.aa - 2 * self.r
        self.b = self.bb - 2 * self.r
        self.c = self.cc - 2 * self.r
        self.d = self.dd - self.r

    def tranform(self, alfa, origin):
        # Transformation matrix
        p = origin
        c, s = np.cos(math.radians(alfa)), np.sin(math.radians(alfa))
        j = np.array([[c, s, 0],
                      [-s, c, 0],
                      [0, 0, 1]])
        RotatedCorners = np.matmul(j, p)
        return RotatedCorners.T

    def coordinates(self):
        # o1
        origin1 = np.array([self.bb/2.0 + self.cc - self.r, self.r, 0.0])
        radius = np.array([0, self.r, 0.0])
        start_ang = 90
        p11 = self.tranform(start_ang + 10, radius)
        p12 = self.tranform(start_ang + 20, radius)
        p13 = self.tranform(start_ang + 30, radius)
        p14 = self.tranform(start_ang + 40, radius)
        p15 = self.tranform(start_ang + 50, radius)
        p16 = self.tranform(start_ang + 60, radius)
        p17 = self.tranform(start_ang + 70, radius)
        p18 = self.tranform(start_ang + 80, radius)
        # o2
        origin2 = np.array([self.bb/2.0 + self.r, self.r, 0.0])
        start_ang = 180
        p21 = self.tranform(start_ang + 10, radius)
        p22 = self.tranform(start_ang + 20, radius)
        p23 = self.tranform(start_ang + 30, radius)
        p24 = self.tranform(start_ang + 40, radius)
        p25 = self.tranform(start_ang + 50, radius)
        p26 = self.tranform(start_ang + 60, radius)
        p27 = self.tranform(start_ang + 70, radius)
        p28 = self.tranform(start_ang + 80, radius)
        # o3
        origin3 = np.array([self.bb/2.0 - self.r, self.aa - self.r, 0.0])
        start_ang = 270
        p31 = self.tranform(start_ang + 10, radius)
        p32 = self.tranform(start_ang + 20, radius)
        p33 = self.tranform(start_ang + 30, radius)
        p34 = self.tranform(start_ang + 40, radius)
        p35 = self.tranform(start_ang + 50, radius)
        p36 = self.tranform(start_ang + 60, radius)
        p37 = self.tranform(start_ang + 70, radius)
        p38 = self.tranform(start_ang + 80, radius)

        # o4
        origin4 = np.array([-self.bb / 2.0 + self.r, self.aa - self.r, 0.0])
        start_ang = 0
        p41 = self.tranform(start_ang + 10, radius)
        p42 = self.tranform(start_ang + 20, radius)
        p43 = self.tranform(start_ang + 30, radius)
        p44 = self.tranform(start_ang + 40, radius)
        p45 = self.tranform(start_ang + 50, radius)
        p46 = self.tranform(start_ang + 60, radius)
        p47 = self.tranform(start_ang + 70, radius)
        p48 = self.tranform(start_ang + 80, radius)

        # o5
        origin5 = np.array([-self.bb / 2.0 - self.r, self.r, 0.0])
        start_ang = 90
        p51 = self.tranform(start_ang + 10, radius)
        p52 = self.tranform(start_ang + 20, radius)
        p53 = self.tranform(start_ang + 30, radius)
        p54 = self.tranform(start_ang + 40, radius)
        p55 = self.tranform(start_ang + 50, radius)
        p56 = self.tranform(start_ang + 60, radius)
        p57 = self.tranform(start_ang + 70, radius)
        p58 = self.tranform(start_ang + 80, radius)

        # o6
        origin6 = np.array([-self.bb/2.0 - self.cc + self.r, self.r, 0.0])
        start_ang = 180
        p61 = self.tranform(start_ang + 10, radius)
        p62 = self.tranform(start_ang + 20, radius)
        p63 = self.tranform(start_ang + 30, radius)
        p64 = self.tranform(start_ang + 40, radius)
        p65 = self.tranform(start_ang + 50, radius)
        p66 = self.tranform(start_ang + 60, radius)
        p67 = self.tranform(start_ang + 70, radius)
        p68 = self.tranform(start_ang + 80, radius)

        self.Csection = np.array([[self.bb / 2.0 + self.cc, self.dd],
                                  [self.bb / 2.0 + self.cc, self.r + (self.dd - self.d)/2.0],
                                  [self.bb / 2.0 + self.cc, self.r],
                                  [origin1[0] + p11[0], origin1[1] + p11[1]],
                                  [origin1[0] + p12[0], origin1[1] + p12[1]],
                                  [origin1[0] + p13[0], origin1[1] + p13[1]],
                                  [origin1[0] + p14[0], origin1[1] + p14[1]],
                                  [origin1[0] + p15[0], origin1[1] + p15[1]],
                                  [origin1[0] + p16[0], origin1[1] + p16[1]],
                                  [origin1[0] + p17[0], origin1[1] + p17[1]],
                                  [origin1[0] + p18[0], origin1[1] + p18[1]],
                                  [self.bb / 2.0 + self.cc - self.r, 0],
                                  [self.bb / 2.0 + self.c / 2.0, 0],
                                  [self.bb / 2.0 + self.r, 0],
                                  [origin2[0] + p21[0], origin2[1] + p21[1]],
                                  [origin2[0] + p22[0], origin2[1] + p22[1]],
                                  [origin2[0] + p23[0], origin2[1] + p23[1]],
                                  [origin2[0] + p24[0], origin2[1] + p24[1]],
                                  [origin2[0] + p25[0], origin2[1] + p25[1]],
                                  [origin2[0] + p26[0], origin2[1] + p26[1]],
                                  [origin2[0] + p27[0], origin2[1] + p27[1]],
                                  [origin2[0] + p28[0], origin2[1] + p28[1]],
                                  [self.bb / 2.0, self.r],
                                  [self.bb / 2.0, self.r + self.a * (1.0 / 4.0)],
                                  [self.bb / 2.0, self.r + self.a * (2.0 / 4.0)],
                                  [self.bb / 2.0, self.r + self.a * (3.0 / 4.0)],
                                  [self.bb / 2.0, self.r + self.a],
                                  [origin3[0] - p31[0], origin3[1] + p31[1]],
                                  [origin3[0] - p32[0], origin3[1] + p32[1]],
                                  [origin3[0] - p33[0], origin3[1] + p33[1]],
                                  [origin3[0] - p34[0], origin3[1] + p34[1]],
                                  [origin3[0] - p35[0], origin3[1] + p35[1]],
                                  [origin3[0] - p36[0], origin3[1] + p36[1]],
                                  [origin3[0] - p37[0], origin3[1] + p37[1]],
                                  [origin3[0] - p38[0], origin3[1] + p38[1]],
                                  [self.bb / 2.0 - self.r, self.aa],
                                  [0.0, self.aa],
                                  [-self.bb / 2.0 + self.r, self.aa],
                                  [origin4[0] - p41[0], origin4[1] + p41[1]],
                                  [origin4[0] - p42[0], origin4[1] + p42[1]],
                                  [origin4[0] - p43[0], origin4[1] + p43[1]],
                                  [origin4[0] - p44[0], origin4[1] + p44[1]],
                                  [origin4[0] - p45[0], origin4[1] + p45[1]],
                                  [origin4[0] - p46[0], origin4[1] + p46[1]],
                                  [origin4[0] - p47[0], origin4[1] + p47[1]],
                                  [origin4[0] - p48[0], origin4[1] + p48[1]],
                                  [-self.bb / 2.0, self.r + self.a],
                                  [-self.bb / 2.0, self.r + self.a * (3.0 / 4.0)],
                                  [-self.bb / 2.0, self.r + self.a * (2.0 / 4.0)],
                                  [-self.bb / 2.0, self.r + self.a * (1.0 / 4.0)],
                                  [-self.bb / 2.0, self.r],
                                  [origin5[0] + p51[0], origin1[1] + p51[1]],
                                  [origin5[0] + p52[0], origin1[1] + p52[1]],
                                  [origin5[0] + p53[0], origin1[1] + p53[1]],
                                  [origin5[0] + p54[0], origin1[1] + p54[1]],
                                  [origin5[0] + p55[0], origin1[1] + p55[1]],
                                  [origin5[0] + p56[0], origin1[1] + p56[1]],
                                  [origin5[0] + p57[0], origin1[1] + p57[1]],
                                  [origin5[0] + p58[0], origin1[1] + p58[1]],
                                  [-self.bb / 2.0 - self.r, 0],
                                  [-self.bb / 2.0 - self.c / 2.0, 0],
                                  [-self.bb / 2.0 - self.cc + self.r, 0],
                                  [origin6[0] + p61[0], origin6[1] + p61[1]],
                                  [origin6[0] + p62[0], origin6[1] + p62[1]],
                                  [origin6[0] + p63[0], origin6[1] + p63[1]],
                                  [origin6[0] + p64[0], origin6[1] + p64[1]],
                                  [origin6[0] + p65[0], origin6[1] + p65[1]],
                                  [origin6[0] + p66[0], origin6[1] + p66[1]],
                                  [origin6[0] + p67[0], origin6[1] + p67[1]],
                                  [origin6[0] + p68[0], origin6[1] + p68[1]],
                                  [-self.bb / 2.0 - self.cc, self.r],
                                  [-self.bb / 2.0 - self.cc, self.r + (self.dd - self.d) / 2.0],
                                  [-self.bb / 2.0 - self.cc, self.dd]])
        # =================

        # Function call for rotation
        Csection, RotatedCsection = rotateCoordinates(self.Csection.T, self.angle)
        # Create id numbers for each row
        numbers = np.arange(RotatedCsection.shape[1], dtype=int)
        # Adding id numbers to the coordinates matrix
        CsectionWithNumbers = np.vstack([numbers, RotatedCsection])

        # Creating ones
        ones = np.ones((4, RotatedCsection.shape[1]))
        # Adding one numbers to the coordinates matrix
        CsectionWithNumbers = np.vstack([CsectionWithNumbers, ones])
        # Creating zeros
        zeros = np.zeros((RotatedCsection.shape[1]))
        # Adding zeros to the coordinates matrix
        CsectionWithNumbers = np.vstack([CsectionWithNumbers, zeros])

        # ===================================
        # Final nodes and elements for Opensees
        # ===================================
        self.nodes = CsectionWithNumbers.T
        # If angle is 90, shift section as flange width in Y dir.
        # If angle is 270, shift section as web height in X dir.
        if self.angle == 90:
            for i in self.nodes:
                i[2] = i[2] + self.B
        elif self.angle == 270:
            for i in self.nodes:
                i[1] = i[1] + self.A

        # Shape of the node matrix
        num_cols, num_rows = Csection.shape
        self.elements = np.empty([num_rows - 1, 5])
        for i in range(num_rows - 1):
            self.elements[i, 0] = i
            self.elements[i, 1] = i
            self.elements[i, 2] = i + 1
            self.elements[i, 3] = self.t
            self.elements[i, 4] = 0

        self.descp_Plot = f'Section :OM {self.A:.3f} x {self.B:.3f} x {self.C:.3f} x {self.D:.3f} - {self.t:.3f}'
        self.descp_rep = (f'Section :OM {self.A:.3f} x {self.B:.3f} x {self.C:.3f} x {self.D:.3f} - {self.t:.3f}\n'
                          f'   A:{self.A:.3f} in, Flange width\n'
                          f'   B:{self.B:.3f} in, Web height\n'
                          f'   C:{self.C:.3f} in, Lip length\n'
                          f'   D:{self.D:.3f} in, Lip length\n'
                          f'   R:{self.R:.3f} in, Inner radius\n'
                          f'   t:{self.t:.3f} in, Thickness')

    def plotter(self, plot_it:bool):
        if plot_it:
            sec_x = self.nodes[:, 1]
            sec_y = self.nodes[:, 2]
            plt.plot(sec_x, sec_y)
            plt.grid()
            plt.title('SECTION')
            plt.xlabel('[mm]')
            plt.ylabel('[mm]')
            plt.axis('equal')
            # Show the plot
            plt.show()

    def orientation(self, angle):
        if angle == 0:
            self.ang_shape = (f'      ┌-┐\n'
                              f'        |\n'
                              f'      └-┘\n')
        elif angle == 270:
            self.ang_shape = (f'   ┌   ┐\n'
                              f'   └---┘\n')
        else:
            self.ang_shape = (f'  ┌---┐\n'
                              f'  └   ┘\n')

    def calculateGross(self):
        x = self.nodes[:, 1]
        y = self.nodes[:, 2]
        t = self.t
        r = self.r
        # Area of cross section
        da = np.zeros([len(x)])
        ba = np.zeros([len(x)])
        for i in range(1, len(da)):
            da[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2)) * t
            ba[i] = math.sqrt(math.pow(x[i - 1] - x[i], 2) + math.pow(y[i - 1] - y[i], 2))
        self.Ar = np.sum(da)
        Lt = np.sum(ba)
        # Total rj.tetaj/90
        Trj = 4 * 4 * r * (1.0 / 4.0)
        delta = 0.43 * Trj / Lt
        # First moment of area and coordinate for gravity centre
        sx0 = np.zeros([len(x)])
        sy0 = np.zeros([len(x)])
        for i in range(1, len(sx0)):
            sx0[i] = (y[i] + y[i - 1]) * da[i] / 2
        self.zgy = np.sum(sx0) / self.Ar
        for i in range(1, len(sy0)):
            sy0[i] = (x[i] + x[i - 1]) * da[i] / 2
        self.zgx = np.sum(sy0) / self.Ar

        # Second moment of area
        Ix0 = np.zeros([len(x)])
        Iy0 = np.zeros([len(x)])
        for i in range(1, len(Ix0)):
            Ix0[i] = (math.pow(y[i], 2) + math.pow(y[i - 1], 2) + y[i] * y[i - 1]) * da[i] / 3
        for i in range(1, len(Iy0)):
            Iy0[i] = (math.pow(x[i], 2) + math.pow(x[i - 1], 2) + x[i] * x[i - 1]) * da[i] / 3
        self.Ix = np.sum(Ix0) - self.Ar * math.pow(self.zgy, 2)
        self.Iy = np.sum(Iy0) - self.Ar * math.pow(self.zgx, 2)

        # Product moment of area
        Ixy0 = np.zeros([len(x)])
        for i in range(1, len(Ixy0)):
            Ixy0[i] = (2 * x[i - 1] * y[i - 1] + 2 * x[i] * y[i] + x[i - 1] * y[i] + x[i] * y[i - 1]) * da[i] / 6
        self.Ixy = np.sum(Ixy0) - (np.sum(sx0) * np.sum(sy0)) / self.Ar

        # Principle axis
        alfa = 0.5 * math.atan(2 * self.Ixy / (self.Iy - self.Ix))
        Iksi = 0.5 * (self.Ix + self.Iy + math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))
        Ieta = 0.5 * (self.Ix + self.Iy - math.sqrt(math.pow(self.Iy - self.Ix, 2) + 4 * math.pow(self.Ixy, 2)))

        # Sectoral coordinates
        w = np.zeros([len(x)])
        w0 = np.zeros([len(x)])
        Iw = np.zeros([len(x)])
        w0[0] = 0
        for i in range(1, len(w0)):
            w0[i] = x[i - 1] * y[i] - x[i] * y[i - 1]
            w[i] = w[i - 1] + w0[i]
            Iw[i] = (w[i - 1] + w[i]) * da[i] / 2
        wmean = np.sum(Iw) / self.Ar

        # Sectorial constants
        Ixw0 = np.zeros([len(x)])
        Iyw0 = np.zeros([len(x)])
        Iww0 = np.zeros([len(x)])
        for i in range(1, len(Ixw0)):
            Ixw0[i] = (2 * x[i - 1] * w[i - 1] + 2 * x[i] * w[i] + x[i - 1] * w[i] + x[i] * w[i - 1]) * da[i] / 6
            Iyw0[i] = (2 * y[i - 1] * w[i - 1] + 2 * y[i] * w[i] + y[i - 1] * w[i] + y[i] * w[i - 1]) * da[i] / 6
            Iww0[i] = (math.pow(w[i], 2) + math.pow(w[i - 1], 2) + w[i] * w[i - 1]) * da[i] / 3
        Ixw = np.sum(Ixw0) - np.sum(sy0) * np.sum(Iw) / self.Ar
        Iyw = np.sum(Iyw0) - np.sum(sx0) * np.sum(Iw) / self.Ar
        Iww = np.sum(Iww0) - math.pow(np.sum(Iw), 2) / self.Ar

        # Shear centre
        self.xsc = (Iyw * self.Iy - Ixw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))
        self.ysc = (-Ixw * self.Ix + Iyw * self.Ixy) / (self.Ix * self.Iy - math.pow(self.Ixy, 2))

        # Warping constant
        self.Cw = Iww + self.ysc * Ixw - self.xsc * Iyw

        # Torsion constant
        It0 = np.zeros([len(x)])
        for i in range(1, len(It0)):
            It0[i] = da[i] * math.pow(t, 2) / 3
        self.It = np.sum(It0)

        # Distance between centroid and shear centre
        self.xo = abs(self.xsc) + self.zgx
        # Distances from the boundaries
        self.zgb = self.zgy
        self.zgt = max(y) - self.zgb
        self.zgl = self.zgx
        self.zgr = max(x) - self.zgl
        self.cx = max(self.zgl, self.zgr)
        self.cy = max(self.zgb, self.zgt)
        # Section modulus
        self.Wx = self.Ix / max(self.zgb, self.zgt)
        self.Wy = self.Iy / max(self.zgl, self.zgr)

        # Data dictionary
        self.propDict = {
            "Ar ": str(round(self.Ar, 3)) + " mm2",
            "zgx ": str(round(self.zgx, 3)) + " mm",
            "zgy ": str(round(self.zgy, 3)) + " mm",
            "Ix ": str(round(self.Ix, 3)) + " mm4",
            "Wx ": str(round(self.Ix / max(self.zgb, self.zgt), 3)) + " mm3",
            "rx ": str(round(math.sqrt(self.Ix / self.Ar), 3)) + " mm",
            "Iy ": str(round(self.Iy, 3)) + " mm4",
            "Wy ": str(round(self.Iy / max(self.zgl, self.zgr), 3)) + " mm3",
            "ry ": str(round(math.sqrt(self.Iy / self.Ar), 3)) + " mm",
            "Ixy ": str(round(self.Ixy, 3)) + " mm4",
            "Iw ": str(round(np.sum(self.Cw), 5)) + " mm3",
            "xsc ": str(round(self.xsc, 3)) + " mm",
            "ysc ": str(round(self.ysc, 3)) + " mm",
            "Cw ": str(round(self.Cw, 5)) + " mm6",
            "It ": str(round(self.It, 5)) + " mm4",
            "xo ": str(round(self.xo, 3)) + " mm",
            "ro ": str(round(math.sqrt(math.sqrt(self.Ix / self.Ar)**2+math.sqrt(self.Iy / self.Ar)**2+self.xo**2), 3)) + " mm"
        }
        self.propDict_imperial = {
            "Ar ": str(round(self.Ar/25.4**2, 3)) + " in2",
            "zgx ": str(round(self.zgx/25.4, 3)) + " in",
            "zgy ": str(round(self.zgy/25.4, 3)) + " in",
            "Ix ": str(round(self.Ix/25.4**4, 3)) + " in4",
            "Wx ": str(round((self.Ix / max(self.zgb, self.zgt))/25.4**3, 3)) + " in3",
            "rx ": str(round(math.sqrt(self.Ix / self.Ar)/25.4**3, 3)) + " in",
            "Iy ": str(round(self.Iy/25.4**4, 3)) + " in4",
            "Wy ": str(round((self.Iy / max(self.zgl, self.zgr))/25.4**3, 3)) + " in3",
            "ry ": str(round(math.sqrt(self.Iy / self.Ar) / 25.4 ** 3, 3)) + " in",
            "Ixy ": str(round(self.Ixy/25.4**4, 3)) + " in4",
            "Iw ": str(round(np.sum(self.Cw)/25.4**3, 5)) + " in3",
            "xsc ": str(round(self.xsc/25.4, 3)) + " in",
            "ysc ": str(round(self.ysc/25.4, 3)) + " in",
            "Cw ": str(round(self.Cw/25.4**6, 5)) + " in6",
            "It ": str(round(self.It/25.4**4, 5)) + " in4",
            "xo ": str(round(self.xo/25.4, 3)) + " in",
            "ro ": str(
                round(math.sqrt(math.sqrt(self.Ix / self.Ar) ** 2 + math.sqrt(self.Iy / self.Ar) ** 2 + self.xo ** 2)/25.4,
                      3)) + " mm"
        }
