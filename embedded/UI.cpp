
#include "Arduino.h"

#include <ArduinoJson.h>

#include "UI.h"

#include "HWDef.h"

static const String kRequestKey{"request"};
static const String kResponsePrefix{"response{"};
static const String kErrorPrefix{"ERROR"};

static const String kRequestSuffix{"}\r"};
static const String kSeparator{","};
static const char kLineEnding{'\n'};

void InitSerialPort() {
  Serial.begin(SERIAL_PORT_BAUD_RATE);

  /*

  Send an initial I am ready message so that clients don't send instructions
  before the arduino is ready to recieve them.

  */

  unsigned long T0 = millis();
  while (!Serial) {
    delayMicroseconds(10);

    if ((millis() - T0) > DT_WAIT_FOR_SERIAL_PORT_MS) return;  // give up
  }

  delayMicroseconds(100);

  Serial.println("Arduino ready");
}

//

CUI::CUI(Stream &serial_port)
    : m_SerialPort(serial_port), m_SmartPump{A0, LED_BUILTIN} {};

void CUI::Update() {
  m_SmartPump.Update();

  //

  if (!m_SerialPort.available()) return;

  String request_str = m_SerialPort.readStringUntil(kLineEnding);
  request_str.trim();

  bool deserialize_ok{false};
  String error_msg;
  auto request = CRequest::Create(request_str, deserialize_ok, error_msg);

  CResponse response{request};

  if (deserialize_ok) {
    response = HandleRequest(request);
  } else {
    response.m_Success = false;
    response.m_Message = "Request de-serialization failed: " + error_msg;
  }
  m_SerialPort.print(response.Serialize());
  m_SerialPort.println("");
}

//

CResponse CUI::HandleRequest(const CRequest &request) {
  CResponse response{request};

  if (request.m_Instruction == "turn_on") {
    auto &pump = m_SmartPump.GetPump();

    if (request.m_Data <= 0) {
      pump.TurnOn();
    } else {
      pump.TurnOnFor(request.m_Data * 1000);
      response.m_Message = "TurnOnFor";
      response.m_Data = request.m_Data;
      pump.Update();
    }
    response.m_Success = true;
  } else if (request.m_Instruction == "turn_off") {
    auto &pump = m_SmartPump.GetPump();
    pump.TurnOff();
    response.m_Success = true;
  } else if (request.m_Instruction == "get_state") {
    auto &pump = m_SmartPump.GetPump();
    response.m_Data = (bool)pump.GetOutputState();
    response.m_Success = true;
  } else if (request.m_Instruction == "get_voltage") {
    auto &sensor = m_SmartPump.GetHumiditySensor();
    auto output = sensor.GetVoltage();
    response.m_Success = true;
    response.m_Data = output;
  } else {
    response.m_Success = false;
    response.m_Instruction = "";
    response.m_Message =
        "Error: Unrecognized instruction: " + request.m_Instruction;
  }

  return response;
}
