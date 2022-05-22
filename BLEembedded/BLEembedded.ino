#include <ArduinoBLE.h>

#include "SmartPump.h"
#include "HWDef.h"
#include "DigitalOutput.h"
#include "Watchdog.h"

long previousMillis = 0;
int interval = 0;
int ledState = LOW;

BLEService pump_service(PUMP_SERVICE_ATTR_ID);

BLELongCharacteristic pump_attr(PUMP_ATTR_ID, BLERead | BLEWrite);
BLEBoolCharacteristic pump_status_attr(PUMP_STATUS_ATTR_ID, BLERead);
BLEFloatCharacteristic humidity_attr(HUMIDITY_ATTR_ID, BLERead | BLEWrite);
BLELongCharacteristic watchdog_ping_attr(WATCHDOG_PING_ATTR_ID, BLERead | BLEWrite);
BLELongCharacteristic watchdog_countdown_attr(WATCHDOG_COUNTDOWN_ATTR_ID, BLERead | BLEWrite);

//
CSmartPump smart_pump(PUMP_DIGITAL_PIN, PUMP_ANALOGUE_PIN);
CDigitalOutput connection_indicator(LED_BUILTIN, false);
CWatchdog watchdog(watchdog_ping_attr, watchdog_countdown_attr, 10);

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
    pump_service.addCharacteristic(watchdog_ping_attr);
    pump_service.addCharacteristic(watchdog_countdown_attr);

    // add service
    BLE.addService(pump_service);

    // set the initial value for the characteristic:
    pump_attr.writeValue(0);
    pump_status_attr.writeValue(false);

    // start advertising
    BLE.advertise();

    safe_println("BLE Ard Pump Lo");
}

void update()
{
    smart_pump.Update();
    connection_indicator.Update();
    watchdog.Update();
}

void on_pump_attr_change()
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

void connected_loop()
{
    update();

    auto humidity_V = smart_pump.GetHumidityVoltage();
    humidity_attr.writeValue(humidity_V);
    pump_status_attr.writeValue(smart_pump.IsOn());

    if (pump_attr.written())
    {
        on_pump_attr_change();
    }
}

void loop()
{
    update();

    if (BLEDevice central = BLE.central())
    {

        safe_print("Connected to central: ");
        safe_println(central.address());

        connection_indicator.TurnOn();
        watchdog.Reset();

        while (central.connected() && !watchdog.Expired())
        {
            connected_loop();
        }

        safe_print("Disconnected from central: ");
        safe_println(central.address());
        connection_indicator.TurnOff();
    }
}
