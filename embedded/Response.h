#pragma once

#include "Arduino.h"

#include "ISerializableEntity.h"
#include "Request.h"

class CResponse : public ISerializableEntity {
 public:
  static const String kIDKey;
  static const String kChannelKey;
  static const String kInstructionKey;
  static const String kSuccessKey;
  static const String kDataKey;
  static const String kMessageKey;

  CResponse();
  CResponse(const CRequest &request);

  CResponse(long id, long channel, String instruction, bool success, float data,
            String message);

  static CResponse Create(String doc_as_str, bool &success,
                          String &error_message);
  String Serialize();

 public:
  long m_ID;
  long m_Channel;
  bool m_Success;
  String m_Instruction;
  float m_Data;
  String m_Message;
};
