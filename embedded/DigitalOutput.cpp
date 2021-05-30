#include "DigitalOutput.h"

namespace {
bool _xor(bool A, bool B) { return !A != !B; }
}  // namespace

CDigitalOutput::CDigitalOutput(pin_id_type pin, bool inverted_output)
    : m_Pin(pin),
      m_InvertedOutput(inverted_output),
      m_OutputState(OutputStates::OFF),
      m_Status(Statuses::READY) {
  pinMode(pin, OUTPUT);
  SetState(OutputStates::OFF);
}

void CDigitalOutput::SetState(OutputStates new_state) {
  // Cancel Any timed activation

  m_Status = Statuses::READY;

  auto pin_state =
      pin_state_type{_xor(static_cast<bool>(new_state), m_InvertedOutput)};
  digitalWrite(m_Pin, pin_state);
}

void CDigitalOutput::TurnOn() { SetState(OutputStates::ON); }
void CDigitalOutput::TurnOff() { SetState(OutputStates::OFF); }

void CDigitalOutput::Update() {  // TODO
}