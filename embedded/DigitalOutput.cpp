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

  m_TimeActivated_ms = millis();
}

void CDigitalOutput::SetState(OutputStates new_state) {
  // Cancel Any timed activation

  m_Status = Statuses::READY;

  m_OutputState = new_state;

  auto pin_state =
      pin_state_type{_xor(static_cast<bool>(new_state), m_InvertedOutput)};
  digitalWrite(m_Pin, pin_state);
}

OutputStates CDigitalOutput::GetOutputState() { return m_OutputState; }

void CDigitalOutput::TurnOn() { SetState(OutputStates::ON); }
void CDigitalOutput::TurnOff() { SetState(OutputStates::OFF); }

void CDigitalOutput::TurnOnFor(time_ms_type activation_duration_ms) {
  m_TimeActivated_ms = millis();
  m_ActivationDuration_ms = activation_duration_ms;

  SetState(OutputStates::ON);
  m_Status = Statuses::RUNNING;
}

void CDigitalOutput::Update() {
  if (m_Status != Statuses::RUNNING) {
    return;
  }

  if ((millis() - m_TimeActivated_ms) > m_ActivationDuration_ms) {
    SetState(OutputStates::OFF);
  }
}
