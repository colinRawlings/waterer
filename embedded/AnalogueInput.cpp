#include "AnalogueInput.h"

CAnalogueInput::CAnalogueInput(pin_id_type pin, bool pull_up)
    : m_Pin(pin),
      m_PullUp(false),
      kStepResolution(AIN_FULL_RANGE_V / AIN_LEVELS) {
  pinMode(m_Pin, INPUT);

  if (pull_up) SetPullUp();
}

void CAnalogueInput::SetPullUp() { digitalWrite(m_Pin, INPUT_PULLUP); }

void CAnalogueInput::Update() {}

float CAnalogueInput::GetVoltage() {
  return kStepResolution * analogRead(m_Pin);
}
