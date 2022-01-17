#include "SmartPump.h"

CSmartPump::CSmartPump(pin_id_type pump_pin, pin_id_type sensor_pin)
    : m_Pump(pump_pin, false)
    , m_HumiditySensor(sensor_pin, false)
{}

void CSmartPump::Update()
{
    m_Pump.Update();
    m_HumiditySensor.Update();
}

void CSmartPump::TurnOn()
{
    m_Pump.TurnOn();
}

void CSmartPump::TurnOff()
{
    m_Pump.TurnOff();
}

void CSmartPump::TurnOnFor(time_ms_type activation_ms)
{
    m_Pump.TurnOnFor(activation_ms);
}

float CSmartPump::GetHumidityVoltage()
{
    return m_HumiditySensor.GetVoltage();
}