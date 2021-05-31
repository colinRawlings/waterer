
#include "Arduino.h"

#include "UI.h"

#include "HWDef.h"

static const String kRequestPrefix{"request{"};
static const String kRequestSuffix{"}\r"};
static const String kRequestSeparator{","};
static const char kLineEnding{'\n'};
static const String kErrorPrefix{"ERROR"};

void InitSerialPort() {
  Serial.begin(SERIAL_PORT_BAUD_RATE);

  unsigned long T0 = millis();
  while (!Serial) {
    delayMicroseconds(10);

    if ((millis() - T0) > DT_WAIT_FOR_SERIAL_PORT_MS) return;  // give up
  }
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

void CUI::EchoKeyValue(const String &key, const String &value,
                       bool new_line) const {
  m_SerialPort.print(key + ": ");
  m_SerialPort.print(value);
  if (new_line)
    m_SerialPort.println("");
  else
    m_SerialPort.print(kRequestSeparator);
}

void CUI::EchoRequest(const SRequest &request) const {
  m_SerialPort.print("Request= ");

  EchoKeyValue("channel", String{request.channel}, false);
  EchoKeyValue("instruction", request.instruction, false);
  EchoKeyValue("data", String{request.data0}, true);
}

void CUI::ReportError(const String &error_msg) const {
  EchoKeyValue(kErrorPrefix, error_msg, true);
}