#include "PumpManager.h"

#include "HWDef.h"

const int CPumpManager::kNumPumps = 3;

CPumpManager::CPumpManager()
    : m_Pumps{
          CSmartPump{PUMP_DIGITAL_PINS[0], PUMP_ANALOGUE_PINS[0]},
          CSmartPump{PUMP_DIGITAL_PINS[1], PUMP_ANALOGUE_PINS[1]},
          CSmartPump{PUMP_DIGITAL_PINS[2], PUMP_ANALOGUE_PINS[2]},
      } {}

void CPumpManager::Update() {
  for (int pump_idx{0}; pump_idx < kNumPumps; ++pump_idx) {
    m_Pumps[pump_idx].Update();
  }
}

CSmartPump& CPumpManager::GetPump(long channel, bool& success) {
  if (channel < 0 || channel >= kNumPumps) {
    success = false;
    return m_Pumps[0];
  }

  success = true;
  return m_Pumps[channel];
}
