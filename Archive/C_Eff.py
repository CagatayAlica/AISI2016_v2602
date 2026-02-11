from S100_Func import *
import SectionInput
from GrossSectionProps import GrossProp


class FlxTeta0:
    def __init__(self):
        # Input:
        Inp = SectionInput.Inputs()
        secDivider = "==========================================================="
        print(f'{secDivider}\nEffective Flexural Properties at Stress {Inp.Res["fy"]:.3} ksi\n{secDivider}')
        print("Orientation: ", SectionInput.Orientation().Teta[Inp.Res["Teta"]])
        # Gross Section Properties
        Gp = GrossProp(Inp.Res["A"], Inp.Res["B"], Inp.Res["C"], Inp.Res["t"], Inp.Res["R"], Inp.Res["alfa"])

        # Function for printing the dictionary
        def PrintDict(Ele, Dict_Name):  # TODO Report output string will be created.
            print(Ele, " :")
            for key, val in Dict_Name.items():
                print("{} : {}".format(key, val))

        # Function for the construct the data matrix
        def DataMatrix(bneg, yneg, t):
            # Defining data matrix
            dataMa = np.zeros([10, 5])
            # L (in.)
            dataMa[0, 0] = calcFlg.Res_C_App113["b"]  # Top flange
            dataMa[1, 0] = Gp.Res["b"]  # Bottom flange
            dataMa[2, 0] = Gp.Res["a"]  # Web
            dataMa[3, 0] = bneg  # Negative web element
            dataMa[4, 0] = Gp.Res["u"]  # Top inside corner
            dataMa[5, 0] = Gp.Res["u"]  # Bottom inside corner
            dataMa[6, 0] = Gp.Res["u"]  # Top outside corner
            dataMa[7, 0] = Gp.Res["u"]  # Bottom outside corner
            dataMa[8, 0] = calcLip.Res_C_App1122["ds"]  # Top lip
            dataMa[9, 0] = Gp.Res["c"]  # Bottom lip
            # y (in.)
            dataMa[0, 1] = Inp.Res["t"] / 2  # Top flange
            dataMa[1, 1] = Inp.Res["A"] - Inp.Res["t"] / 2  # Bottom flange
            dataMa[2, 1] = Inp.Res["A"] / 2  # Web
            dataMa[3, 1] = yneg  # Negative web element
            dataMa[4, 1] = (1 - 0.637) * Gp.Res["r"] + Inp.Res["t"] / 2  # Top inside corner
            dataMa[5, 1] = Inp.Res["A"] - 0.637 * Gp.Res["r"]  # Bottom inside corner
            dataMa[6, 1] = (1 - 0.637) * Gp.Res["r"] + Inp.Res["t"] / 2  # Top outside corner
            dataMa[7, 1] = Inp.Res["A"] - 0.637 * Gp.Res["r"]  # Bottom outside corner
            dataMa[8, 1] = calcLip.Res_C_App1122["ds"] + Gp.Res["r"] + Inp.Res["t"] / 2  # Top lip
            dataMa[9, 1] = Inp.Res["A"] - Gp.Res["c"] / 2 - Gp.Res["r"] - Inp.Res["t"] / 2  # Bottom lip
            # L.y (in2.)
            dataMa[0, 2] = dataMa[0, 0] * dataMa[0, 1]  # Top flange
            dataMa[1, 2] = dataMa[1, 0] * dataMa[1, 1]  # Bottom flange
            dataMa[2, 2] = dataMa[2, 0] * dataMa[2, 1]  # Web
            dataMa[3, 2] = dataMa[3, 0] * dataMa[3, 1]  # Negative web element
            dataMa[4, 2] = dataMa[4, 0] * dataMa[4, 1]  # Top inside corner
            dataMa[5, 2] = dataMa[5, 0] * dataMa[5, 1]  # Bottom inside corner
            dataMa[6, 2] = dataMa[6, 0] * dataMa[6, 1]  # Top outside corner
            dataMa[7, 2] = dataMa[7, 0] * dataMa[7, 1]  # Bottom outside corner
            dataMa[8, 2] = dataMa[8, 0] * dataMa[8, 1]  # Top lip
            dataMa[9, 2] = dataMa[9, 0] * dataMa[9, 1]  # Bottom lip
            # L.y2 (in3.)
            dataMa[0, 3] = dataMa[0, 2] * dataMa[0, 1]  # Top flange
            dataMa[1, 3] = dataMa[1, 2] * dataMa[1, 1]  # Bottom flange
            dataMa[2, 3] = dataMa[2, 2] * dataMa[2, 1]  # Web
            dataMa[3, 3] = dataMa[3, 2] * dataMa[3, 1]  # Negative web element
            dataMa[4, 3] = dataMa[4, 2] * dataMa[4, 1]  # Top inside corner
            dataMa[5, 3] = dataMa[5, 2] * dataMa[5, 1]  # Bottom inside corner
            dataMa[6, 3] = dataMa[6, 2] * dataMa[6, 1]  # Top outside corner
            dataMa[7, 3] = dataMa[7, 2] * dataMa[7, 1]  # Bottom outside corner
            dataMa[8, 3] = dataMa[8, 2] * dataMa[8, 1]  # Top lip
            dataMa[9, 3] = dataMa[9, 2] * dataMa[9, 1]  # Bottom lip
            # Ix' (in3.)
            dataMa[0, 4] = 0  # Top flange
            dataMa[1, 4] = 0  # Bottom flange
            dataMa[2, 4] = dataMa[2, 0] ** 3 / 12  # Web
            dataMa[3, 4] = 0  # Negative web element
            dataMa[4, 4] = dataMa[4, 0] ** 3 / 12  # Top inside corner
            dataMa[5, 4] = dataMa[5, 0] ** 3 / 12  # Bottom inside corner
            dataMa[6, 4] = dataMa[6, 0] ** 3 / 12  # Top outside corner
            dataMa[7, 4] = dataMa[7, 0] ** 3 / 12  # Bottom outside corner
            dataMa[8, 4] = dataMa[8, 0] ** 3 / 12  # Top lip
            dataMa[9, 4] = dataMa[9, 0] ** 3 / 12  # Bottom lip

            arrSum = dataMa.sum(axis=0)
            calculated_ybar = arrSum[2] / arrSum[0]
            Ixe = (arrSum[4] + arrSum[3] - calculated_ybar ** 2 * arrSum[0]) * t
            Res_DataMatrix = {
                "calc_ybar": calculated_ybar,
                "Ixe": Ixe,
                "DataMatrix": dataMa,
                "Subtotals": arrSum
            }
            return Res_DataMatrix

        # 1. Effective Section Modulus, Se, at Initiation of Yielding
        #   a. Compression flange: from Appendix 1 Section 1.3
        f = Inp.Res["fy"]
        calcFlg = C_App113(Gp.Res["b"], Inp.Res["t"], Inp.Res["E"], f, Gp.Res["c"], Inp.Res["C"], Inp.Res["nu"])
        PrintDict("Flange", calcFlg.Res_C_App113)
        #   b. Stiffener lip: from Appendix 1, Section 1.2.2(a)
        ybar = Inp.Res["A"] / 2  # This is the initial position of the neutral axis.
        case = 1  # Figure 1.2.2-1(a) Inward facing lip.
        f1 = f * (ybar - Inp.Res["t"] / 2 - Gp.Res["r"]) / ybar  # Stress on the top end of the lip.
        f2 = f * (ybar - Inp.Res["C"]) / ybar  # Stress on the bottom end of the lip.
        calcLip = C_App1122(f1, f2, case, calcFlg.Res_C_App113["Ri"], Inp.Res["E"], Inp.Res["nu"], Gp.Res["c"],
                            Inp.Res["t"])
        PrintDict('Lip', calcLip.Res_C_App1122)

        #   c. Web: from Appendix 1, Section 1.1.2
        f1 = f * (ybar - Inp.Res["t"] / 2 - Gp.Res["r"]) / ybar  # Stress on the top end of the web.
        f2 = -f * (Inp.Res["A"] - ybar - Inp.Res["t"] / 2 - Gp.Res["r"]) / ybar  # Stress on the bottom end of the web.
        wref = Gp.Res["a"] / 2  # Compression block of the flat width of the web.
        calcWeb = C_App1112(f1, f2, Gp.Res["a"], Inp.Res["t"], Inp.Res["A"], Inp.Res["B"], Inp.Res["E"], Inp.Res["nu"],
                            wref)
        PrintDict('Web', calcWeb.Res_C_App1112)
        # Length of the negative portion of the web:
        bneg = -(wref - (calcWeb.Res_C_App1112["b1"] + calcWeb.Res_C_App1112["b2"]))
        # Distance between centroid of the negative portion and the top fiber.
        yneg = Inp.Res["t"] / 2 + Gp.Res["r"] + calcWeb.Res_C_App1112["b1"] - bneg / 2
        # Calculation of the new centroid and the effective moment of inertia.
        DataRes = DataMatrix(bneg, yneg, Inp.Res["t"])

        # Storing the previous value
        ypre = ybar
        ybar = DataRes["calc_ybar"]

        print(f"ypre = {ypre} ==> ybar = {ybar}, Ixe = {DataRes['Ixe']} ")
        print("_____________________")

        # Iteration starts
        #   a. Compression flange: from Appendix 1 Section 1.3. Stress level is same for the flange.
        #   Previous solution is valid.
        Re_Calculate = True
        iteration = 0
        while Re_Calculate:
            iteration += 1
            print(f"İteration #{iteration}\n")
            #   b. Stiffener lip: from Appendix 1, Section 1.2.2(a)
            case = 1  # Figure 1.2.2-1(a) Inward facing lip.
            f1 = f * (ybar - Inp.Res["t"] / 2 - Gp.Res["r"]) / ybar  # Stress on the top end of the lip.
            f2 = f * (ybar - Inp.Res["C"]) / ybar  # Stress on the bottom end of the lip.
            calcLip = C_App1122(f1, f2, case, calcFlg.Res_C_App113["Ri"], Inp.Res["E"], Inp.Res["nu"], Gp.Res["c"],
                                Inp.Res["t"])
            PrintDict('Lip', calcLip.Res_C_App1122)
            #   c. Web: from Appendix 1, Section 1.1.2
            f1 = f * (ybar - Inp.Res["t"] / 2 - Gp.Res["r"]) / ybar  # Stress on the top end of the web.
            f2 = -f * (Inp.Res["A"] - ybar - Inp.Res["t"] / 2 - Gp.Res[
                "r"]) / ybar  # Stress on the bottom end of the web.
            wref = ybar - Gp.Res["r"] - Inp.Res["t"] / 2  # Compression block of the flat portion of the web.
            calcWeb = C_App1112(f1, f2, Gp.Res["a"], Inp.Res["t"], Inp.Res["A"], Inp.Res["B"], Inp.Res["E"],
                                Inp.Res["nu"],
                                wref)
            PrintDict('Web', calcWeb.Res_C_App1112)
            # Length of the negative portion of the web:
            bneg = -(wref - (calcWeb.Res_C_App1112["b1"] + calcWeb.Res_C_App1112["b2"]))
            # Distance between centroid of the negative portion and the top fiber.
            yneg = Inp.Res["t"] / 2 + Gp.Res["r"] + calcWeb.Res_C_App1112["b1"] - bneg / 2
            # Calculation of the new centroid and the effective moment of inertia.
            DataRes = DataMatrix(bneg, yneg, Inp.Res["t"])

            # Storing the previous value
            ypre = ybar
            ybar = DataRes["calc_ybar"]
            print(f"ypre = {ypre} ==> ybar = {ybar}, Ixe = {DataRes['Ixe']} ")
            print("_____________________")
            # Exit the loop if ybar converges
            if abs((ypre - ybar) / ybar) < 0.0001:
                Re_Calculate = False

        # Final results:
        Flx_Teta0 = {
            "ybar": DataRes["calc_ybar"],
            "Ixe": DataRes['Ixe'],
            "Sxe": DataRes["Ixe"] / DataRes["calc_ybar"]
        }
        print(PrintDict("Final Results", Flx_Teta0))


class Axial:
    def __init__(self):
        # Input:
        Inp = SectionInput.Inputs()
        secDivider = "==========================================================="

        # Gross Section Properties
        Gp = GrossProp(Inp.Res["A"], Inp.Res["B"], Inp.Res["C"], Inp.Res["t"], Inp.Res["R"], Inp.Res["alfa"])

        # Function for printing the dictionary
        def PrintDict(Ele, Dict_Name):
            print(Ele, " :")
            for key, val in Dict_Name.items():
                print("{} : {}".format(key, val))

        # Function for the construct the data matrix
        def DataMatrix(t):
            # Defining data matrix
            dataMa = np.zeros([10, 1])
            # L (in.)
            dataMa[0, 0] = calcFlg.Res_C_App113["b"]  # Top flange
            dataMa[1, 0] = calcFlg.Res_C_App113["b"]  # Bottom flange
            dataMa[2, 0] = calcWeb.Res_C_App111["b"]  # Web
            dataMa[3, 0] = Gp.Res["u"]  # Top inside corner
            dataMa[4, 0] = Gp.Res["u"]  # Bottom inside corner
            dataMa[5, 0] = Gp.Res["u"]  # Top outside corner
            dataMa[6, 0] = Gp.Res["u"]  # Bottom outside corner
            dataMa[7, 0] = calcLip.Res_C_App111["ds"]  # Top lip
            dataMa[8, 0] = calcLip.Res_C_App111["ds"]  # Bottom lip

            Ae = dataMa.sum(axis=0) * t
            Res_DataMatrix = {
                "Ae": Ae
            }
            return Res_DataMatrix

        # 1. Effective Section Modulus, Se, at Initiation of Yielding
        #   a. Compression flange: from Appendix 1 Section 1.3
        f1 = C_SecE21(Inp.Res['Kx'], Inp.Res['Lx'], Inp.Res['E'], Gp.Res['Ix'], Gp.Res['Ag'])
        f2 = C_SecE22(Inp.Res['Kx'], Inp.Res['Lx'], Inp.Res['Kt'], Inp.Res['Lt'], Inp.Res['E'], Gp.Res['J'],
                      Gp.Res['Cw'],
                      Gp.Res['xo'], Inp.Res['nu'], Gp.Res['Ix'], Gp.Res['Iy'], Gp.Res['Ag'])

        f = min(f1.Fcre, f2.Fcre)
        lamc = math.sqrt(Inp.Res["fy"]/f)

        if lamc<=1.5:
            Fn = math.pow(0.658,math.pow(lamc,2))*Inp.Res['fy']
        else:
            Fn = (0.877/math.pow(lamc,2))*Inp.Res['fy']

        print(f'{secDivider}\nEffective Axial Properties at Stress {Fn:.3} ksi\n{secDivider}')

        calcFlg = C_App113(Gp.Res["b"], Inp.Res["t"], Inp.Res["E"], Fn, Gp.Res["c"], Inp.Res["C"], Inp.Res["nu"])
        PrintDict("Flange", calcFlg.Res_C_App113)
        #   b. Stiffener lip: from Appendix 1, Section 1.2.2(a)
        k = 0.43  # Free end element
        calcLip = C_App111(Fn, Inp.Res["E"], Inp.Res["nu"], Gp.Res["c"], Inp.Res["t"], k, calcFlg.Res_C_App113["Ri"])
        PrintDict('Lip', calcLip.Res_C_App111)
        #   c. Web: from Appendix 1, Section 1.1.2
        k = 4.0  # Fixed at both end
        calcWeb = C_App111(Fn, Inp.Res["E"], Inp.Res["nu"], Gp.Res["a"], Inp.Res["t"], k, 1)
        PrintDict('Web', calcWeb.Res_C_App111)

        DataRes = DataMatrix(Inp.Res["t"])
        # Final results:
        Ax = {
            "Ae ": DataRes["Ae"]
        }
        print(PrintDict("Final Results", Ax))
