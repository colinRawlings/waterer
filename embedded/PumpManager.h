#pragma once

#include "IEventLoopEntity.h"

#include "SmartPump.h"

class CPumpManager : public IEventLoopEntity {
 public:
  static const int kNumPumps;
  CPumpManager();

  CSmartPump& GetPump(long channel);

  void Update() override;

 private:
  CSmartPump m_Pumps[3];
};