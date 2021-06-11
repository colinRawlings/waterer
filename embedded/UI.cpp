
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
    : m_SerialPort(serial_port),
      m_DigitalOutput(LED_BUILTIN, false),
      m_AnalogueInput(A0, false) {}

void CUI::Update() {
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
    m_DigitalOutput.TurnOn();
    response.m_Success = true;
  } else if (request.m_Instruction == "turn_off") {
    m_DigitalOutput.TurnOff();
    response.m_Success = true;
  } else if (request.m_Instruction == "get_voltage") {
    auto output = m_AnalogueInput.GetVoltage();
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

// Logging Output

// void CUI::PrintKeyValue(const String &key, const String &value,
//                         bool new_line) const {
//   m_SerialPort.print(key + ": ");
//   m_SerialPort.print(value);
//   if (new_line) m_SerialPort.println("");
// }

// void CUI::PrintRequest(const CRequest &request) const {
//   m_SerialPort.print("request{");

//   PrintKeyValue("\"channel\"", String{request.m_Channel}, false);
//   m_SerialPort.print(kSeparator);
//   PrintKeyValue("\"instruction\"", "\"" + request.m_Instruction + "\"",
//   false); m_SerialPort.print(kSeparator); PrintKeyValue("\"data\"",
//   String{request.m_Data0}, false);

//   m_SerialPort.print("}");
// }

// void CUI::PrintResponse(const CResponse &response) const {
//   m_SerialPort.print(kResponsePrefix);

//   PrintKeyValue("\"channel\"", String{response.m_Channel}, false);
//   m_SerialPort.print(kSeparator);
//   PrintKeyValue("\"instruction\"", "\"" + response.m_Instruction + "\"",
//   false); m_SerialPort.print(kSeparator); PrintKeyValue("\"data\"",
//   String{response.m_Data0}, false);

//   m_SerialPort.print("}");
// }

// void CUI::ReportError(const String &error_msg) const {
//   PrintKeyValue(kErrorPrefix, error_msg, true);
// }
