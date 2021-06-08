#include "ArduinoSTL.h"
#include <system_configuration.h>
#include <unwind-cxx.h>

#include <ArduinoJson.h>

#include "Arduino.h"

#include "UI.h"

CUI ui(Serial);

void setup() {
  InitSerialPort();

  std::vector<int> my_vec{1, 2};

  // Serial.println(my_vec[1]);

  //
}

void loop() { ui.Update(); }
