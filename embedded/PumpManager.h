#pragma once

#include "IEventLoopEntity.h"

#include "SmartPump.h"

class CPumpManager : public IEventLoopEntity {
 public:
  CPumpManager(long num_pumps);

  CSmartPump& GetPump(long channel);

  void Update() override;

 private:
  long m_NumPumps;
  CSmartPump* m_Pumps;
};