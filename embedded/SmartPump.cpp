#include "SmartPump.h"

CSmartPump::CSmartPump(pin_id_type sensor_pin, pin_id_type pump_pin)
    : m_Pump(pump_pin, false), m_HumiditySensor(sensor_pin, false) {}

void CSmartPump::Update() {
  m_Pump.Update();
  m_HumiditySensor.Update();
}