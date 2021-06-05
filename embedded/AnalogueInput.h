#pragma once

#include "HWDef.h"

#include "IEventLoopEntity.h"

class CAnalogueInput : public IEventLoopEntity {
 public:
  CAnalogueInput(pin_id_type pin, bool pull_up);

  float GetVoltage();

  void SetPullUp();

  void Update() override;

 private:
  const float kStepResolution;

  pin_id_type m_Pin;
  bool m_PullUp;
};
