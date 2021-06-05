#include "Arduino.h"

#include "UI.h"

CUI ui(Serial);

void setup() { InitSerialPort(); }

void loop() { ui.Update(); }
