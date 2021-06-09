#pragma once

#include "Arduino.h"

#include "ISerializableEntity.h"

class CResponse {
 public:
  static const String kChannelKey;
  static const String kInstructionKey;
  static const String kData0Key;

  long m_Channel;
  String m_Instruction;
  float m_Data0;

  static CResponse Create(String doc_as_str);
  String Serialize();
};
