import json

from waterer_backend.models import SmartPumpSettings

sett = SmartPumpSettings()

print(sett.dict())


with open(
    "/home/test/Documents/waterer/backend/waterer_backend/config/default_pump_config.json",
    "r",
) as f:
    data = json.load(f)[0]

print(data["settings"])

print(SmartPumpSettings(**data["settings"]))
