#include "HWDef.h"

// Values

const unsigned long SERIAL_PORT_BAUD_RATE{115200};

const int DT_WAIT_FOR_SERIAL_PORT_MS{2000};

// Scaling

const int AIN_LEVELS{1023};
const float AIN_FULL_RANGE_V{3.3f};

// Pin Allocations

extern const pin_id_type PUMP_DIGITAL_PIN{10};
extern const pin_id_type PUMP_ANALOGUE_PIN{A6};