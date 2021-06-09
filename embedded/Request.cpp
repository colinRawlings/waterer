#include "Request.h"

#include <ArduinoJson.h>
#include "HWDef.h"

const String CRequest::kChannelKey = "channel";
const String CRequest::kInstructionKey = "instruction";
const String CRequest::kData0Key = "data0";

CRequest::CRequest()

    CRequest CRequest::Create(String doc_as_str) {
  StaticJsonDocument<JSON_DOC_SIZE> doc;

  CRequest request{-1, "Error", -1};

  auto exit_error = [&request](String msg) {
    request.m_Instruction = msg;
    return request;
  };

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, doc_as_str);
  if (error) {
    return exit_error("Deserialize failed: " + doc_as_str);
  }

  if (!doc.containsKey(kChannelKey))
    return exit_error("Missing channel key: " + doc_as_str);

  if (!doc.containsKey(kInstructionKey))
    return exit_error("Missing instruction key: " + doc_as_str);

  if (!doc.containsKey(kData0Key))
    return exit_error("Missing data0 key: " + doc_as_str);

  // Collect values

  request.m_Channel = doc["channel"];
  request.m_Instruction = doc["instruction"].as<String>();
  request.m_Data0 = doc["data0"];

  return request;
}

String CRequest::Serialize() {
  StaticJsonDocument<JSON_DOC_SIZE> doc;
  doc["channel"] = m_Channel;
  doc["instruction"] = m_Instruction;
  doc["data0"] = m_Data0;

  String doc_as_str;

  serializeJsonPretty(doc, doc_as_str);

  return doc_as_str;
}