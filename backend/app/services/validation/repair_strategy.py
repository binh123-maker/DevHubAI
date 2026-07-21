class BaseRepairStrategy:
    def __init__(self, name: str):
        self.name = name

class ConservativeRepairStrategy(BaseRepairStrategy):
    def __init__(self):
        super().__init__("CONSERVATIVE")

class BalancedRepairStrategy(BaseRepairStrategy):
    def __init__(self):
        super().__init__("BALANCED")

class AggressiveRepairStrategy(BaseRepairStrategy):
    def __init__(self):
        super().__init__("AGGRESSIVE")
