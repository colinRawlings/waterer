#pragma once

#include "Arduino.h"

#include "ISerializableEntity.h"

class CRequest : public ISerializableEntity {
 public:
  static const String kChannelKey;
  static const String kInstructionKey;
  static const String kData0Key;

  CRequest(long channel, String instruction, long data0);

  long m_Channel;
  String m_Instruction;
  long m_Data0;

  static CRequest Create(String request_as_str);

  String Serialize();
};