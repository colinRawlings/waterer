#pragma once

#include "IEventLoopEntity.h"
#include "DigitalOutput.h"
#include "AnalogueInput.h"

// Free function to start the serial port - hopefully this succeeds
void InitSerialPort();

struct SRequest {
  long channel;
  String instruction;
  long data0;
};

struct SResponse {
  long channel;
  String instruction;
  float data0;
};

class CUI : public IEventLoopEntity {
 public:
  CUI(Stream &serial_port);

  void Update() override;

 private:
  bool ParseRequest(const String &request_str, SRequest &request) const;
  SResponse HandleRequest(const SRequest &request);

  void ReportError(const String &error_msg) const;

  void PrintRequest(const SRequest &request) const;
  void PrintResponse(const SResponse &response) const;

  void PrintKeyValue(const String &key, const String &value,
                     bool new_line) const;

 private:
  Stream &m_SerialPort;

  CDigitalOutput m_DigitalOutput;
  CAnalogueInput m_AnalogueInput;
};