#pragma once

#include "Arduino.h"

#include "ISerializableEntity.h"

class CRequest : public ISerializableEntity {
 public:
  static const String kIDKey;
  static const String kChannelKey;
  static const String kInstructionKey;
  static const String kDataKey;

  CRequest();
  CRequest(long id, long channel, String instruction, long data);
  static CRequest Create(String request_as_str, bool &success,
                         String &error_message);
  String Serialize();

 public:
  long m_ID;
  long m_Channel;
  String m_Instruction;
  long m_Data;
};