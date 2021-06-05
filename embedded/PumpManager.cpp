#include "PumpManager.h"

#include "HWDef.h"

CPumpManager::CPumpManager(long num_pumps) : m_NumPumps(0), m_Pumps(nullptr) {
  if (num_pumps > MAX_NUM_PUMPS) {
    num_pumps = MAX_NUM_PUMPS;
  }
  m_NumPumps = num_pumps;

  //   m_Pumps = new CSmartPump[m_NumPumps];

  // TODO :(
}

void CPumpManager::Update() {
  // loop over pumps and call their update ...
}