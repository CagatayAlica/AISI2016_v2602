import math
from Archive import SectionInput
from Archive.GrossSectionProps import GrossProp

def ero(rx, ry, xo):
    return math.sqrt(math.pow(rx,2)+math.pow(ry,2)+math.pow(xo,2))
def sigma_tor(Ag, ro,G,J,E,Cw,Kt,Lt):
    sig_t = (1.0/(Ag*ro**2))*(G*J+(math.pi**2*E*Cw/(Kt*Lt)**2))
    return sig_t
def sigma_global(E, K, L, r):
    return math.pow(math.pi,2)*E/math.pow(K*L/r,2)
def fcritical(beta, sex, set):
    return 1.0/(2.0*beta)*((sex+set)-math.sqrt(math.pow(sex+set,2)-4*beta*sex*set))

class Compression:
    def __init__(self):
        # Input:
        Inp = SectionInput.Inputs()
        # Gross Section Properties
        Gp = GrossProp(Inp.Res["A"], Inp.Res["B"], Inp.Res["C"], Inp.Res["t"], Inp.Res["R"], Inp.Res["alfa"])
        rx = math.sqrt(Gp.Res['Ix']/Gp.Res['Ag'])
        ry = math.sqrt(Gp.Res['Iy'] / Gp.Res['Ag'])
        xo = Gp.Res['xo']
        ro = ero(rx, ry, xo)
        sigma_t = sigma_tor(Gp.Res['Ag'],
                     ro,
                     Inp.Res['G'],
                     Gp.Res['J'],
                     Inp.Res["E"],
                     Gp.Res['Cw'],
                     Inp.Res["Kt"],
                     Inp.Res["Lt"])
        beta = 1 - (xo/ro)**2
        sigma_x = sigma_global(Inp.Res["E"],
                               Inp.Res["Kx"],
                               Inp.Res["Lx"],
                               rx)
        sigma_y = sigma_global(Inp.Res["E"],
                               Inp.Res["Ky"],
                               Inp.Res["Ly"],
                               ry)
        fcre = fcritical(beta,sigma_x,sigma_t)
