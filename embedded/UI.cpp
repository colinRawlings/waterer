
#include "Arduino.h"

#include "UI.h"

#include "HWDef.h"

static const String kRequestPrefix{"request{"};
static const String kRequestSuffix{"}"};
static const String kRequestSeparator{","};
static const char kLineEnding{'\r'};
static const String kErrorPrefix{"ERROR"};

void InitSerialPort() {
  Serial.begin(SERIAL_PORT_BAUD_RATE);

  unsigned long T0 = millis();
  while (!Serial) {
    delayMicroseconds(10);

    if ((millis() - T0) > DT_WAIT_FOR_SERIAL_PORT_MS) return;  // give up
  }

  delayMicroseconds(DT_INIT_SERIAL_WAIT_VSCODE_TEST_MSG);

  String initMsg = "";

  while (Serial.available() > 0) initMsg += (char)Serial.read();

  Serial.println("Initialised the serial port, received: '" + initMsg + "'");
}

//

CUI::CUI(Stream &serial_port)
    : m_SerialPort(serial_port), m_Output(LED_BUILTIN, false) {}

void CUI::Update() {
  if (!m_SerialPort.available()) return;

  String request_str = m_SerialPort.readStringUntil(kLineEnding);

  if (request_str.length() == 1) return;

  SRequest request;
  bool ok = ParseRequest(request_str, request);
  if (!ok) return;

  EchoRequest(request);

  HandleRequest(request);
}

bool CUI::ParseRequest(const String &request_str, SRequest &request) const {
  auto exit_error = [this](const String &msg) {
    ReportError(msg);
    return false;
  };

  if (!request_str.startsWith(kRequestPrefix)) return exit_error("Bad prefix");

  if (!request_str.endsWith(kRequestSuffix)) return exit_error("Bad suffix");

  String request_body = request_str.substring(
      kRequestPrefix.length(), request_str.length() - kRequestSuffix.length());

  // split

  auto first_comma_index = request_body.indexOf(kRequestSeparator);
  auto last_comma_index = request_body.lastIndexOf(kRequestSeparator);

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

void CUI::HandleRequest(const SRequest &request) {
  if (request.instruction == "turn_on") {
    m_Output.TurnOn();
  } else if (request.instruction == "turn_off") {
    m_Output.TurnOff();
  } else {
    ReportError("Unrecognized instruction: " + request.instruction);
  }
}

// Logging Output

void CUI::EchoKeyValue(const String &key, const String &value) const {
  m_SerialPort.print(key + ": ");
  m_SerialPort.println(value);
}

void CUI::EchoRequest(const SRequest &request) const {
  m_SerialPort.println("Request: ");

  EchoKeyValue("channel", String{request.channel});
  EchoKeyValue("instruction", request.instruction);
  EchoKeyValue("data", String{request.data0});
}

void CUI::ReportError(const String &error_msg) const {
  EchoKeyValue(kErrorPrefix, error_msg);
}