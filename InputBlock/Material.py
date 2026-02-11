class Material:
    def __init__(self, name:str, fy:float, fu:float, selectUnit):
        """
        Material definition
        :param name: Material name
        :param fy: Yield stress
        :param fu: Ultimate stress
        """
        self.name = name
        self.fy = fy
        self.fu = fu
        self.v = 0.3
        self.E = 29500.0 / selectUnit.toKsi
        self.G = 81000.0 * 0.1450377377 / selectUnit.toKsi

    def __str__(self):
        return f"Selected material grade is {self.name}"
