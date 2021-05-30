#pragma once

#include "Arduino.h"

using pin_id_type = uint8_t;
using pin_state_type = bool;

using time_us_type = unsigned long;

// Values

extern const unsigned long SERIAL_PORT_BAUD_RATE;

extern const int DT_WAIT_FOR_SERIAL_PORT_MS;
extern const int DT_INIT_SERIAL_WAIT_VSCODE_TEST_MSG;
