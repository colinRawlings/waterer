#include <ArduinoBLE.h>

#include "SmartPump.h"
#include "HWDef.h"

long previousMillis = 0;
int interval = 0;
int ledState = LOW;

BLEService pump_service(PUMP_SERVICE_ATTR_ID);

BLELongCharacteristic pump_attr(PUMP_ATTR_ID, BLERead | BLEWrite);
BLEBoolCharacteristic pump_status_attr(PUMP_STATUS_ATTR_ID, BLERead);
BLEFloatCharacteristic humidity_attr(HUMIDITY_ATTR_ID, BLERead | BLEWrite);

CSmartPump smart_pump(PUMP_DIGITAL_PIN, PUMP_ANALOGUE_PIN);

template <typename T>
void safe_println(T msg)
{
    if (!Serial)
        return;

    Serial.println(msg);
}

template <typename T>
void safe_print(T msg)
{
    if (!Serial)
        return;

    Serial.print(msg);
}

void setup()
{
    Serial.begin(9600);

    // set built in LED pin to output mode
    pinMode(10, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);

    // begin initialization
    if (!BLE.begin())
    {
        safe_println("starting BLE failed!");

        while (1)
            ;
    }

    // set advertised local name and service UUID:
    BLE.setLocalName("Ard Pump Lo");
    BLE.setAdvertisedService(pump_service);

    // add the characteristic to the service
    pump_service.addCharacteristic(pump_attr);
    pump_service.addCharacteristic(pump_status_attr);
    pump_service.addCharacteristic(humidity_attr);

    // add service
    BLE.addService(pump_service);

    // set the initial value for the characteristic:
    pump_attr.writeValue(0);
    pump_status_attr.writeValue(false);

    // start advertising
    BLE.advertise();

    safe_println("BLE Ard Pump Lo");
}

void loop()
{
    // listen for BLE peripherals to connect:
    BLEDevice central = BLE.central();

    // if a central is connected to peripheral:
    if (central)
    {

        safe_print("Connected to central: ");
        // print the central's MAC address:
        safe_println(central.address());

        digitalWrite(LED_BUILTIN, HIGH); // will turn the LED off

        // while the central is still connected to peripheral:
        while (central.connected())
        {
            smart_pump.Update();

            auto humidity_V = smart_pump.GetHumidityVoltage();
            humidity_attr.writeValue(humidity_V);
            pump_status_attr.writeValue(smart_pump.IsOn());

            if (pump_attr.written())
            {
                auto written_val = pump_attr.value();
                safe_print("Recieved instruction: ");
                safe_println(written_val);

                if (written_val == -1)
                {
                    safe_println("Pump on");

                    smart_pump.TurnOn();
                }
                else if (written_val == 0)
                {
                    safe_println("Pump off");

                    smart_pump.TurnOff();
                }
                else if (written_val > 0)
                {
                    safe_print("Turn on for (ms): ");
                    safe_println(written_val);

                    smart_pump.TurnOnFor(written_val);
                }
                else
                {
                    safe_print("Pump unhandled instruction: ");
                    safe_println(written_val);
                }
            }
        }

        // when the central disconnects, print it out:
        safe_print("Disconnected from central: ");
        safe_println(central.address());
        digitalWrite(LED_BUILTIN, LOW); // will turn the LED off
    }
}
