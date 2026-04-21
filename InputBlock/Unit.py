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


def convert(value, from_unit, to_unit):
    # Mapping units to their base SI unit (Meters for distance, Newtons for force)
    units = {
        "distance": {
            "factors": {'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0, 'in': 0.0254, 'ft': 0.3048, 'mi': 1609.34},
            "members": {'mm', 'cm', 'm', 'km', 'in', 'ft', 'mi'}
        },
        "force": {
            "factors": {'N': 1.0, 'kN': 1000.0, 'lbf': 4.44822, 'kgf': 9.80665},
            "members": {'N', 'kN', 'lbf', 'kgf'}
        }
    }

    # Find which category the units belong to
    category = next((cat for cat, data in units.items() if from_unit in data["members"]), None)

    if category and to_unit in units[category]["members"]:
        factors = units[category]["factors"]
        # Convert to base unit, then to target unit
        base_value = value * factors[from_unit]
        return base_value / factors[to_unit]

    return "Invalid conversion: Units must match type (Distance vs Force)."


# Examples
print(f"500 Newtons to Pounds-force: {convert(500, 'N', 'lbf'):.2f} lbf")
print(f"100 Feet to Meters: {convert(100, 'ft', 'm'):.2f} m")