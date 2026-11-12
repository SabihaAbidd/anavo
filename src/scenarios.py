from .models import Appliance, Scenario


def presets():
    loads = (Appliance("Fan", 40, 3, 9, True),
             Appliance("LED lights", 10, 3, 7, True),
             Appliance("Wi-Fi router", 10, 3, 8, True, True),
             Appliance("Laptop", 60, 2, 6))
    return {
        "Evening backup": Scenario("Evening backup", loads, 240, 100, 3),
        "Ample backup": Scenario("Ample backup", loads, 400, 150, 3),
        "Limited battery": Scenario("Limited battery", loads, 90, 60, 3),
        "Mandatory infeasible": Scenario("Mandatory infeasible", loads, 15, 100, 3),
    }
