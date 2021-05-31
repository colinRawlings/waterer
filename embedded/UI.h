#pragma once

#include "IEventLoopEntity.h"
#include "DigitalOutput.h"

// Free function to start the serial port - hopefully this succeeds
void InitSerialPort();

struct SRequest {
  long channel;
  String instruction;
  long data0;
};

class CUI : public IEventLoopEntity {
 public:
  CUI(Stream &serial_port);

  void Update() override;

 private:
  bool ParseRequest(const String &request_str, SRequest &request) const;
  void HandleRequest(const SRequest &request);

  void ReportError(const String &error_msg) const;
  void EchoRequest(const SRequest &request) const;
  void EchoKeyValue(const String &key, const String &value,
                    bool new_line) const;

 private:
  Stream &m_SerialPort;

  CDigitalOutput m_Output;
};