#include "Request.h"

#include <ArduinoJson.h>
#include "HWDef.h"

const String CRequest::kIDKey = "id";
const String CRequest::kChannelKey = "channel";
const String CRequest::kInstructionKey = "instruction";
const String CRequest::kDataKey = "data";

CRequest::CRequest() : m_ID{-1}, m_Channel{-1}, m_Instruction{""}, m_Data{0} {}

CRequest::CRequest(long ID, long channel, String instruction, long data)
    : m_ID{ID}, m_Channel{channel}, m_Instruction{instruction}, m_Data{data} {}

CRequest CRequest::Create(String doc_as_str, bool &success,
                          String &error_message) {
  DynamicJsonDocument doc(JSON_DOC_SIZE);

  CRequest request;

  auto exit_error = [&request, &success, &error_message](String msg) {
    error_message = msg;
    success = false;
    return request;
  };

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, doc_as_str);
  if (error) {
    return exit_error("Deserialize failed.");
  }

  if (!doc.containsKey(kIDKey)) return exit_error("Missing ID key.");

  if (!doc.containsKey(kChannelKey)) return exit_error("Missing channel key.");

  if (!doc.containsKey(kInstructionKey))
    return exit_error("Missing instruction key.");

  if (!doc.containsKey(kDataKey)) return exit_error("Missing data key.");

  // Collect values

  request.m_ID = doc[kIDKey];
  request.m_Channel = doc[kChannelKey];
  request.m_Instruction = doc[kInstructionKey].as<String>();
  request.m_Data = doc[kDataKey];

  success = true;

  return request;
}

String CRequest::Serialize() {
  StaticJsonDocument<JSON_DOC_SIZE> doc;
  doc[kIDKey] = m_ID;
  doc[kChannelKey] = m_Channel;
  doc[kInstructionKey] = m_Instruction;
  doc[kDataKey] = m_Data;

  String doc_as_str;

  serializeJson(doc, doc_as_str);

  return doc_as_str;
}