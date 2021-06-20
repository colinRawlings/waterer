#include "Response.h"

#include <ArduinoJson.h>
#include "HWDef.h"

const String CResponse::kIDKey = "id";
const String CResponse::kChannelKey = "channel";
const String CResponse::kInstructionKey = "instruction";
const String CResponse::kSuccessKey = "success";
const String CResponse::kDataKey = "data";
const String CResponse::kMessageKey = "message";

CResponse::CResponse()
    : m_ID{-1},
      m_Channel{-1},
      m_Instruction{""},
      m_Success{false},
      m_Data{-1.0f},
      m_Message{""} {}

CResponse::CResponse(const CRequest &request)
    : m_ID{request.m_ID},
      m_Channel{request.m_Channel},
      m_Instruction{request.m_Instruction},
      m_Success{false},
      m_Data{-1.0f},
      m_Message{""} {}

CResponse::CResponse(long ID, long channel, String instruction, bool success,
                     float data, String message)
    : m_ID{ID},
      m_Channel{channel},
      m_Instruction{instruction},
      m_Success{success},
      m_Data{data},
      m_Message{message} {}

CResponse CResponse::Create(String doc_as_str, bool &success,
                            String &error_message) {
  StaticJsonDocument<JSON_DOC_SIZE> doc;

  CResponse response;

  auto exit_error = [&response, &success, &error_message](String msg) {
    success = false;
    error_message = msg;
    return response;
  };

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, doc_as_str);
  if (error) {
    return exit_error("Deserialize failed");
  }

  if (!doc.containsKey(kIDKey)) return exit_error("Missing ID key.");

  if (!doc.containsKey(kChannelKey)) return exit_error("Missing 'channel' key");

  if (!doc.containsKey(kInstructionKey))
    return exit_error("Missing 'instruction' key");

  if (!doc.containsKey(kSuccessKey)) return exit_error("Missing 'success' key");

  if (!doc.containsKey(kDataKey)) return exit_error("Missing 'data' key");

  if (!doc.containsKey(kMessageKey)) return exit_error("Missing 'message' key");

  // Collect values

  response.m_ID = doc[kIDKey];
  response.m_Channel = doc[kChannelKey];
  response.m_Instruction = doc[kInstructionKey].as<String>();
  response.m_Success = doc[kSuccessKey];
  response.m_Data = doc[kDataKey];
  response.m_Message = doc[kMessageKey].as<String>();

  return response;
}

String CResponse::Serialize() {
  DynamicJsonDocument doc(JSON_DOC_SIZE);

  doc[kIDKey] = m_ID;
  doc[kChannelKey] = m_Channel;
  doc[kInstructionKey] = m_Instruction;
  doc[kSuccessKey] = m_Success;
  doc[kDataKey] = m_Data;
  doc[kMessageKey] = m_Message;

  String doc_as_str;

  serializeJson(doc, doc_as_str);

  return doc_as_str;
}