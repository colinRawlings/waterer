
#include "Arduino.h"

#include "UI.h"

#include "HWDef.h"

static const String kRequestPrefix{"request{"};
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

  if (request_str.length() == 1) return;

  SRequest request;
  bool ok = ParseRequest(request_str, request);
  if (!ok) return;

  PrintRequest(request);

  auto response = HandleRequest(request);

  PrintResponse(response);

  m_SerialPort.println("");
}

bool CUI::ParseRequest(const String &request_str, SRequest &request) const {
  auto exit_error = [this, request_str](const String &msg) {
    ReportError(msg + ": " + request_str);
    return false;
  };

  if (!request_str.startsWith(kRequestPrefix))
    return exit_error("Bad prefix" + request_str);

  if (!request_str.endsWith(kRequestSuffix)) return exit_error("Bad suffix");

  String request_body = request_str.substring(
      kRequestPrefix.length(), request_str.length() - kRequestSuffix.length());

  // split

  auto first_comma_index = request_body.indexOf(kSeparator);
  auto last_comma_index = request_body.lastIndexOf(kSeparator);

  if (first_comma_index >= last_comma_index)
    return exit_error("Not enough commas");

  //

  request.channel = request_body.substring(0, first_comma_index).toInt();

  request.instruction =
      request_body.substring(first_comma_index + 1, last_comma_index);

  request.data0 =
      request_body.substring(last_comma_index + 1, request_body.length())
          .toInt();

  return true;
}

//

SResponse CUI::HandleRequest(const SRequest &request) {
  SResponse response{0, "Error", 0.0f};

  if (request.instruction == "turn_on") {
    m_DigitalOutput.TurnOn();
    response = SResponse{request.channel, request.instruction, 0.0f};
  } else if (request.instruction == "turn_off") {
    m_DigitalOutput.TurnOff();
    response = SResponse{request.channel, request.instruction, 0.0f};
  } else if (request.instruction == "get_voltage") {
    auto output = m_AnalogueInput.GetVoltage();
    response = SResponse{request.channel, request.instruction, output};
  } else {
    ReportError("Unrecognized instruction: " + request.instruction);
  }

  return response;
}

// Logging Output

void CUI::PrintKeyValue(const String &key, const String &value,
                        bool new_line) const {
  m_SerialPort.print(key + ": ");
  m_SerialPort.print(value);
  if (new_line) m_SerialPort.println("");
}

void CUI::PrintRequest(const SRequest &request) const {
  m_SerialPort.print(kRequestPrefix);

  PrintKeyValue("\"channel\"", String{request.channel}, false);
  m_SerialPort.print(kSeparator);
  PrintKeyValue("\"instruction\"", "\"" + request.instruction + "\"", false);
  m_SerialPort.print(kSeparator);
  PrintKeyValue("\"data\"", String{request.data0}, false);

  m_SerialPort.print("}");
}

void CUI::PrintResponse(const SResponse &response) const {
  m_SerialPort.print(kResponsePrefix);

  PrintKeyValue("\"channel\"", String{response.channel}, false);
  m_SerialPort.print(kSeparator);
  PrintKeyValue("\"instruction\"", "\"" + response.instruction + "\"", false);
  m_SerialPort.print(kSeparator);
  PrintKeyValue("\"data\"", String{response.data0}, false);

  m_SerialPort.print("}");
}

void CUI::ReportError(const String &error_msg) const {
  PrintKeyValue(kErrorPrefix, error_msg, true);
}