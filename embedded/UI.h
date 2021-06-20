#pragma once

#include "IEventLoopEntity.h"
#include "DigitalOutput.h"
#include "AnalogueInput.h"
#include "Request.h"
#include "Response.h"
#include "SmartPump.h"
#include "PumpManager.h"

// Free function to start the serial port - hopefully this succeeds
void InitSerialPort();

class CUI : public IEventLoopEntity {
 public:
  CUI(Stream &serial_port);

  void Update() override;

 private:
  bool ParseRequest(const String &request_str, CRequest &request) const;
  CResponse HandleRequest(const CRequest &request);

  void ReportError(const String &error_msg) const;

  void PrintRequest(const CRequest &request) const;
  void PrintResponse(const CResponse &response) const;

  void PrintKeyValue(const String &key, const String &value,
                     bool new_line) const;

 private:
  Stream &m_SerialPort;
  CPumpManager m_PumpManager;
};
