class InterruptRegister:
    def __init__(self):
        self.is_halted: bool = False
        self.interrupt: bool = False
