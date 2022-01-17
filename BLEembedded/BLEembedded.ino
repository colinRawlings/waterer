#include <ArduinoBLE.h>

#include "SmartPump.h"
#include "HWDef.h"

long previousMillis = 0;
int interval = 0;
int ledState = LOW;

BLEService pump_service("180A"); // BLE LED Service

// BLE LED Switch Characteristic - custom 128-bit UUID, read and writable by
// central
BLELongCharacteristic pump_attr("2A67", BLERead | BLEWrite);
BLEFloatCharacteristic humidity_attr("2A68", BLERead | BLEWrite);

CSmartPump smart_pump(PUMP_DIGITAL_PIN, PUMP_ANALOGUE_PIN);

void setup()
{
    Serial.begin(9600);
    //  while (!Serial);

    // set built in LED pin to output mode
    pinMode(10, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);

    // begin initialization
    if (!BLE.begin())
    {
        if (Serial)
            Serial.println("starting BLE failed!");

        while (1)
            ;
    }

    // set advertised local name and service UUID:
    BLE.setLocalName("Ard Pump Lo");
    BLE.setAdvertisedService(pump_service);

    // add the characteristic to the service
    pump_service.addCharacteristic(pump_attr);
    pump_service.addCharacteristic(humidity_attr);

    // add service
    BLE.addService(pump_service);

    // set the initial value for the characteristic:
    pump_attr.writeValue(0);

    // start advertising
    BLE.advertise();

    if (Serial)
        Serial.println("BLE Ard Pump Lo");
}

void loop()
{
    // listen for BLE peripherals to connect:
    BLEDevice central = BLE.central();

    // if a central is connected to peripheral:
    if (central)
    {

        if (Serial)
            Serial.print("Connected to central: ");
        // print the central's MAC address:
        if (Serial)
            Serial.println(central.address());

        digitalWrite(LED_BUILTIN, HIGH); // will turn the LED off

        // while the central is still connected to peripheral:
        while (central.connected())
        {
            smart_pump.Update();

            auto humidity_V = smart_pump.GetHumidityVoltage();
            // if (Serial)
            //     Serial.println(humidity_V);
            humidity_attr.writeValue(humidity_V);

            if (pump_attr.written())
            {
                auto written_val = pump_attr.value();
                if (Serial)
                {
                    Serial.print("Recieved instruction: ");
                    Serial.println(written_val);
                }

                if (written_val == -1)
                {
                    if (Serial)
                        Serial.println("Pump on");

                    smart_pump.TurnOn();
                }
                else if (written_val == 0)
                {
                    if (Serial)
                        Serial.println("Pump off");

                    smart_pump.TurnOff();
                }
                else if (written_val > 0)
                {
                    if (Serial)
                    {
                        Serial.print("Turn on for (ms): ");
                        Serial.println(written_val);
                    }

                    smart_pump.TurnOnFor(written_val);
                }
                else
                {
                    if (Serial)
                    {
                        Serial.print("Pump unhandled instruction: ");
                        Serial.println(written_val);
                    }
                }
            }
        }

        // when the central disconnects, print it out:
        if (Serial)
            Serial.print(F("Disconnected from central: "));
        if (Serial)
            Serial.println(central.address());
        digitalWrite(LED_BUILTIN, LOW); // will turn the LED off
    }
}
