#include "Arduino.h"
#include "DigitalOutput.h"

// led

CDigitalOutput led(LED_BUILTIN, false);

// the setup function runs once when you press reset or power the board
void setup() {}

// the loop function runs over and over again forever
void loop() {
  led.TurnOn();

  delay(1000);  // wait for a second

  led.TurnOff();

  delay(1000);  // wait for a second

  //   Serial.println("Hello!!!");
}