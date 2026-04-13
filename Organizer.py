import InputBlock.Unit
from typing import Literal
import InputBlock.Section
import InputBlock.Material
import InputBlock.Definitions as defs
import D100.Compression as comp
import D100.Flexure as bend
import D100.Shear as sh
import Buckling.Program.Organizer as org

# ======================================================================================================================
# Selection of unit
# ======================================================================================================================
select_unit = InputBlock.Unit.Unit('METRIC')
print(select_unit)
# ======================================================================================================================
# Steel material in selected unit
# ======================================================================================================================
mat = InputBlock.Material.Material(defs.name, defs.fy, defs.fu, select_unit)
print(mat)
# ======================================================================================================================
# Defining the section in selected unit
# ======================================================================================================================
sec = InputBlock.Section.C_Section(defs.A, defs.B, defs.C, defs.t, defs.R, 0, mat)
print(sec)
# ======================================================================================================================
# Calculation for Axial Compression
# ======================================================================================================================
step1 = org.Buckle(selected_unit=select_unit, section=sec, material=mat, case='AXIAL')
factors = step1.values
modes_total = len(step1.values)
print(f'modes : {modes_total}')
AxialCalc= comp.Compression_calc(sec,mat,factors[0][2],factors[1][2],defs.Kx,defs.Lx,defs.Ky,defs.Ly,defs.Kt,defs.Lt)
print(AxialCalc)
print(AxialCalc.report())

# ======================================================================================================================
# Calculation for Bending
# ======================================================================================================================
step2 = org.Buckle(selected_unit=select_unit, section=sec, material=mat, case='BENDING')
factors = step2.values
modes_total = len(step2.values)
print(f'modes : {modes_total}')
BendingCalc= bend.Flexure_calc(sec,mat,factors[0][2],factors[1][2],defs.Kx,defs.Lx,defs.Ky,defs.Ly,defs.Kt,defs.Lt)

print(BendingCalc.ffMn)


ShearCalc = sh.Shear_calc(sec,mat,34,55)
print(ShearCalc.ffVn)
print(ShearCalc.ffVnh)