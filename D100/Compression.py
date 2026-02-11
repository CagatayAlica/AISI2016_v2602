import math
# ======================================================================================================================
# CONSTANTS
# ======================================================================================================================
# Section divider for text
secDivider = '============================================'
sp3 = '   '
sp6 = '      '
sp9 = '         '

class Compression_calc:
    def __init__(self, section, material, factorlocal, factordistortional, Kx, Lx, Ky, Ly, Kt, Lt):
        self.Ag = section.Ar
        self.Ix = section.Ix
        self.Iy = section.Iy
        self.rx = math.sqrt(self.Ix/self.Ag)
        self.ry = math.sqrt(self.Iy/self.Ag)
        self.J = section.It
        self.Cw = section.Cw
        self.xo = section.xo
        self.ro = math.sqrt(math.pow(self.rx,2)+math.pow(self.ry,2)+math.pow(self.xo,2))
        self.beta = 1 - math.pow(self.xo/self.ro,2)
        self.fy = material.fy
        self.E = material.E
        self.G = material.G
        self.Kx = Kx
        self.Lx = Lx
        self.Ky = Ky
        self.Ly = Ly
        self.Kt = Kt
        self.Lt = Lt
        self.ff = 0.90 # Section F2
        self.factorlocal = factorlocal
        self.factordistort = factordistortional

        # ======
        # Global buckling strength
        self.Fcre_x = math.pow(math.pi,2)*self.E/math.pow((self.Kx*self.Lx)/self.rx,2)
        self.Fcre_y = math.pow(math.pi,2)*self.E/math.pow((self.Ky*self.Ly)/self.ry,2)
        self.sigma_t = (1.0/(self.Ag*self.ro**2))*(self.G*self.J+(math.pi**2*self.E*self.Cw/(self.Kt*self.Lt)**2))
        self.sigma_x = self.Fcre_x
        self.Fcre_t = 1.0/(2.0*self.beta)*((self.sigma_x+self.sigma_t)-math.sqrt(math.pow(self.sigma_x+self.sigma_t,2)-4*self.beta*self.sigma_x*self.sigma_t))
        self.lamc = math.sqrt(self.fy/min(self.Fcre_x,self.Fcre_y,self.Fcre_t))
        if self.lamc <= 1.5:
            self.Fn = math.pow(0.658, math.pow(self.lamc, 2)) * self.fy
            pr1 = (f'λc ≤ 1.5 ⇒ 0.658 ^ λc² . fy = Fn\n'
                   f'           0.658 ^ {self.lamc:.3f}² . {self.fy:.3f} = {self.Fn:.3f}')
        else:
            self.Fn = 0.877 / math.pow(self.lamc, 2) * self.fy
            pr1 = (f'λc > 1.5 ⇒ 0.877 / λc² . fy = Fn\n'
                   f'           0.877 / {self.lamc:.3f}² . {self.fy:.3f} = {self.Fn:.3f}')
        self.pr1 = pr1
        self.Pne = self.Ag*self.Fn
        self.ffPne = self.ff * self.Pne

        # ======
        # Local buckling strength without holes
        self.Py = self.Ag * self.fy
        self.Pcrl = self.factorlocal*self.Py
        self.laml = math.sqrt(self.Pne/self.Pcrl)
        if self.laml <= 0.776:
            self.Pnl = self.Pne
            pr2 = f'λl ≤ 0.776 ⇒ Pnl = Pne = {self.Pnl:.3f}'
        else:
            self.Pnl = (1-0.15*math.pow(self.Pcrl/self.Pne,0.4))*math.pow(self.Pcrl/self.Pne,0.4)*self.Pne
            pr2 = f'λl > 0.776 ⇒ Pnl = (1 - 0.15 . ({self.Pcrl:.3f} / {self.Pne:.3f})⁰·⁴) . ({self.Pcrl:.3f} / {self.Pne:.3f})⁰·⁴ . {self.Pne:.3f} = {self.Pnl:.3f}'
        self.pr2 = pr2
        self.ffPnl = self.ff * self.Pnl

        # ======
        # Distortional buckling strength without holes
        self.Pcrd = self.factordistort * self.Pne
        self.Py = self.Ag * self.fy
        self.lamd = math.sqrt(self.Py/self.Pcrd)
        if self.laml <= 0.561:
            self.Pnd = self.Py
            pr3 = f'λd ≤ 0.561 ⇒ Pnd = Py = {self.Pnd:.3f}'
        else:
            self.Pnd = (1-0.25*math.pow(self.Pcrd/self.Py,0.6))*math.pow(self.Pcrd/self.Py,0.6)*self.Py
            pr3 = f'λd > 0.561 ⇒ Pnd = (1 - 0.25 . ({self.Pcrd:.3f} / {self.Py:.3f})⁰·⁶) . ({self.Pcrd:.3f} / {self.Py:.3f})⁰·⁶ . {self.Py:.3f} = {self.Pnd:.3f}'
        self.pr3 = pr3
        self.ffPnd = self.ff * self.Pnd

        # ======
        # Strength
        self.ffPn = min(self.ffPne, self.ffPnl, self.ffPnd)



    def report(self):
        rep = (f'\n{secDivider}\nCALCULATION DETAILS\n{secDivider}\n'
               f'=== Gross Sectional Properties ===\n'
               f'Gross section area \t: Ag = {self.Ag:.3f}\n'
               f'Moment of inertia about x axis \t: Ix = {self.Ix:.3f}\n'
               f'Moment of inertia about y axis \t: Iy = {self.Iy:.3f}\n'
               f'Radius of gyration x axis \t: rx = √({self.Ix:.3f} / {self.Ag:.3f}) = {self.rx:.3f}\n'
               f'Radius of gyration y axis \t: ry = √({self.Iy:.3f} / {self.Ag:.3f}) = {self.ry:.3f}\n'
               f'Torsional constant \t: J = {self.J:.3f}\n'
               f'Warping constant \t: Cw = {self.Cw:.3f}\n'
               f'Distance from shear center \t: xo = {self.xo:.3f}\n'
               f'Polar radius of gyration \t: ro = √({self.rx:.3f}² + {self.ry:.3f}² + {self.xo:.3f}²) = {self.ro:.3f}\n'
               f'Beta constant \t: β =  1 - ({self.xo:.3f} / {self.ro:.3f})² = {self.beta:.3f}\n'
               f'\n=== Material Properties ===\n'
               f'Yield stress \t: fy = {self.fy:.3f}\n'
               f'Elastic modulus \t: E = {self.E:.0f}\n'
               f'Shear modulus \t: G = {self.G:.0f}\n'
               f'\n=== Member Properties ===\n'
               f'Length \t: Lx,y,t = {self.Lx:.3f}, {self.Ly:.3f}, {self.Lt:.3f}\n'
               f'Length factors \t: Kx,y,t = {self.Kx:.3f}, {self.Ky:.3f}, {self.Kt:.3f}\n'
               f'LRFD factor for compression \t: ∅ = {self.ff:.2f}\n'
               f'\n=== Direct Strength Method Analysis ===\n'
               f'Load factor for axial compression \n'
               f'Local buckling \t:   fLocal = {self.factorlocal:.3f}\n'
               f'Distortional buckling \t:  fDist = {self.factordistort:.3f}\n'
               f'{secDivider}\nGlobal Buckling Strength\n{secDivider}\n'
               f'{sp3}Fcre_x = π² . E / (Kx . Lx / rx)² | Eq. E2.1-1\n'
               f'{sp3}         π² . {self.E:.0f} / ({self.Kx:.3f} . {self.Lx:.3f} / {self.rx:.3f})² = {self.Fcre_x:.3f}\n'
               f'{sp3}Fcre_y = π² . E / (Ky . Ly / ry)² | Eq. E2.1-1\n'
               f'{sp3}         π² . {self.E:.0f} / ({self.Ky:.3f} . {self.Ly:.3f} / {self.ry:.3f})² = {self.Fcre_y:.3f}\n'
               f'{sp3}σt = [1 / (Ag . ro²)] . [G . J + (π² . E . Cw) / (Kt . Lt)²] | Eq. E2.2-5\n'
               f'{sp3}     [1 / ({self.Ag:.3f} . {self.ro:.3f}²)] . [{self.G:.0f} . {self.J:.3f} + (π² . {self.E:.0f} . {self.Cw:.3f}) / ({self.Kt:.3f} . {self.Lt:.3f})²] = {self.sigma_t:.3f}\n'
               f'{sp3}σx = Fcre_x | Eq. E2.2-5\n'
               f'{sp3}     Fcre_x = {self.Fcre_x:.3f}\n'
               f'{sp3}Fcre_t = 1 / (2 . β) . ((Fcre_x + σt) - √((Fcre_x + σt)² - 4 . β . Fcre_x . σt)) | Eq. E2.2-1\n'
               f'{sp3}         1 / (2 . {self.beta:.3f}) . [({self.Fcre_x:.3f} + {self.sigma_t:.3f}) - √(({self.Fcre_x:.3f} + {self.sigma_t:.3f})² - 4 . {self.beta:.3f} . {self.Fcre_x:.3f} . {self.sigma_t:.3f})] = {self.Fcre_t:.3f}\n'
               f'{sp3}λc = √(fy / min[Fcre_x,Fcre_y,Fcre_t]) | Eq. E2.4\n'
               f'{sp3}     √({self.fy:.3f} / min[{self.Fcre_x:.3f},{self.Fcre_y:.3f},{self.Fcre_t:.3f}]) = {self.lamc:.3f}\n'
               f'{sp3}Fn = {self.pr1}\n'
               f'{sp3}Pne = {self.Ag:.3f} . {self.Fn:.3f} = {self.Pne:.3f}\n'
               f'{sp3}∅Pne = {self.ff:.2f} * {self.Pne:.3f} = {self.ffPne:.3f}\n'
               f'{secDivider}\nLocal Buckling Strength Without Holes\n{secDivider}\n'
               f'{sp3}Py = {self.Ag:.3f} . {self.fy:.3f} = {self.Py:.3f}\n'
               f'{sp3}Pcrl = {self.factorlocal:.3f} . {self.Py:.3f} = {self.Pcrl:.3f}\n'
               f'{sp3}λl = √({self.Pne:.3f} / {self.Pcrl:.3f}) = {self.laml:.3f}\n'
               f'{sp3}Pnl = {self.pr2}\n'
               f'{sp3}∅Pnl = {self.ff:.2f} * {self.Pnl:.3f} = {self.ffPnl:.3f}\n'
               f'{sp3}Pnd = {self.pr3}\n'
               f'{sp3}∅Pnd = {self.ff:.2f} * {self.Pnd:.3f} = {self.ffPnd:.3f}\n'
               f'{secDivider}\nAxial Compression Strength\n{secDivider}\n'
               f'{sp3}∅Pn = min[{self.ffPne:.3f}, {self.ffPnl:.3f}, {self.ffPnd:.3f}] = {self.ffPn:.3f}\n')
        return rep

    def __str__(self):
        rep = f'{secDivider}\nCHAPTER F, MEMBERS IN FLEXURE\n{secDivider}\n'
        return rep

