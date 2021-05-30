#pragma once

#include "HWDef.h"
#include "IEventLoopEntity.h"

enum class OutputStates : pin_state_type {
  OFF = false,
  ON = true,
};

enum class Statuses { NOT_READY, READY, RUNNING };

class CDigitalOutput : IEventLoopEntity {
 public:
  CDigitalOutput(pin_id_type pin, bool inverted_output);

  // Turn on the pin - this cancels any timed activation
  void TurnOn();

  // Turn off the pin - this cancels any timed activation
  void TurnOff();

  // Enter a timed activation of the pin (us) - requires polling of the event
  // loop via Update
  void TurnOnFor(time_us_type activation_duration_us);

  // Get the status
  Statuses GetStatus();

  // Get the current pin state
  OutputStates GetOutputState();

  //
  void Update() override;

 private:
  void SetState(OutputStates new_state);

 private:
  pin_id_type m_Pin;
  bool m_InvertedOutput;

  time_us_type m_TimeActivated_us;
  time_us_type m_ActivationDuration_us;

  OutputStates m_OutputState;
  Statuses m_Status;
};