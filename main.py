# Other modules:
from Archive.GrossSectionProps import GrossProp
from Archive import C_Eff, SectionInput

# Input:
Inp = SectionInput.Inputs()
# Gross Section Properties
Gp = GrossProp(Inp.Res["A"], Inp.Res["B"], Inp.Res["C"], Inp.Res["t"], Inp.Res["R"], Inp.Res["alfa"])
print(Gp.Res["Report"])
# Bending Strong
Flx_Teta0 = C_Eff.FlxTeta0()
# Axial Compression
Axial = C_Eff.Axial()


