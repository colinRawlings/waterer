#pragma once

#include "IEventLoopEntity.h"

#include "DigitalOutput.h"
#include "AnalogueInput.h"

// Container class composing the IO for a smart pump (digital output + humidity
// sensor input)
class CSmartPump : public IEventLoopEntity
{
  public:
    CSmartPump(pin_id_type pump_pin, pin_id_type sensor_pin);

    CDigitalOutput & GetPump() { return m_Pump; }

    CAnalogueInput & GetHumiditySensor() { return m_HumiditySensor; }

    void Update() override;

    void TurnOff();
    void TurnOn();

    bool IsOn();

    void TurnOnFor(time_ms_type activation_ms);
    float GetHumidityVoltage();

  private:
    CDigitalOutput m_Pump;
    CAnalogueInput m_HumiditySensor;
};