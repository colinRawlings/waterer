#pragma once

#include "HWDef.h"
#include "IEventLoopEntity.h"

enum class OutputStates : pin_state_type {
  OFF = false,
  ON = true,
};

enum class Statuses : int { NOT_READY = 0, READY, RUNNING };

class CDigitalOutput : IEventLoopEntity {
 public:
  CDigitalOutput(pin_id_type pin, bool inverted_output);

  // Turn on the pin - this cancels any timed activation
  void TurnOn();

  // Turn off the pin - this cancels any timed activation
  void TurnOff();

  // Enter a timed activation of the pin (us) - requires polling of the event
  // loop via Update
  void TurnOnFor(time_ms_type activation_duration_ms);

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

  time_ms_type m_TimeActivated_ms;
  time_ms_type m_ActivationDuration_ms;

  OutputStates m_OutputState;
  Statuses m_Status;
};
