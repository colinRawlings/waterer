#pragma once

#include "Arduino.h"

using pin_id_type = uint8_t;
using pin_state_type = bool;

using time_us_type = unsigned long;

// Values

extern const unsigned long SERIAL_PORT_BAUD_RATE;

extern const int DT_WAIT_FOR_SERIAL_PORT_MS;

// Scaling

extern const int AIN_LEVELS;
extern const float AIN_FULL_RANGE_V;
