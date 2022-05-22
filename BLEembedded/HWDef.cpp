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

// Id's

extern const char PUMP_SERVICE_ATTR_ID[]{'1', '8', '0', 'A', '\0'};

extern const char PUMP_ATTR_ID[]{'2', 'A', '6', '7', '\0'};
extern const char PUMP_STATUS_ATTR_ID[]{'2', 'A', '6', '8', '\0'};
extern const char HUMIDITY_ATTR_ID[]{'2', 'A', '6', '9', '\0'};