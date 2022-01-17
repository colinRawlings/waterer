#pragma once

#include "Arduino.h"

using pin_id_type = uint8_t;
using pin_state_type = bool;

using time_ms_type = long;

// Values

extern const unsigned long SERIAL_PORT_BAUD_RATE;

extern const int DT_WAIT_FOR_SERIAL_PORT_MS;

// Scaling

extern const int AIN_LEVELS;
extern const float AIN_FULL_RANGE_V;

// Pin Allocations

extern const pin_id_type PUMP_DIGITAL_PIN;
extern const pin_id_type PUMP_ANALOGUE_PIN;

// Attr Id's

extern const char PUMP_ATTR_ID[];
extern const char PUMP_ATTR_ID[];
