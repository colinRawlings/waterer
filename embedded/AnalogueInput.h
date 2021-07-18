#pragma once

#include "HWDef.h"

#include "IEventLoopEntity.h"

class CAnalogueInput : public IEventLoopEntity {
 public:
  CAnalogueInput(pin_id_type pin, bool pull_up,
                 float averaging_time_constant_samples = 10);

  /// Returns the exponentially averaged voltage
  float GetVoltage();

  void SetPullUp();

  void Update() override;

 private:
  float _GetVoltage();

  const float kStepResolution;

  pin_id_type m_Pin;
  bool m_PullUp;

  //
  bool m_FirstSample;
  float m_AveragedVoltage;
  float m_AveragingTimeConstant_samples;
};
