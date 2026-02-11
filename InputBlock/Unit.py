from typing import Literal

class Unit:
    def __init__(self, unit: Literal['METRIC','IMPERIAL']):
        """
        General selection of units.
        Metric for length in mm, stress in MPa.
        Imperial for length in inches, stress in ksi.
        :param unit: Select METRIC or IMPERIAL
        """
        self.unit = unit
        self.name = None
        if self.unit == 'METRIC':
            self.name = '[mm, MPa, N]'
            self.length_unit = 'mm'
            self.stress_unit = 'MPa'
            self.toInches = 1.0 / 25.4
            self.toKsi = 0.1450377377
        else:
            self.name = '[in, ksi, kips]'
            self.length_unit = 'in'
            self.stress_unit = 'ksi'
            self.toInches = 1.0
            self.toKsi = 1.0

    def __str__(self):
        return f"Selected unit is {self.unit}, {self.name}"
