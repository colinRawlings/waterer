#include "Response.h"

#include <ArduinoJson.h>
#include "HWDef.h"

const String CResponse::kChannelKey = "channel";
const String CResponse::kInstructionKey = "instruction";
const String CResponse::kData0Key = "data0";

CResponse CResponse::Create(String doc_as_str) {
  StaticJsonDocument<JSON_DOC_SIZE> doc;

  CResponse response{-1, "Error", -1};

  auto exit_error = [&response](String msg) {
    response.m_Instruction = msg;
    return response;
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

  response.m_Channel = doc["channel"];
  response.m_Instruction = doc["instruction"].as<String>();
  response.m_Data0 = doc["data0"];

  return response;
}

String CResponse::Serialize() {
  StaticJsonDocument<JSON_DOC_SIZE> doc;
  doc["channel"] = m_Channel;
  doc["instruction"] = m_Instruction;
  doc["data0"] = m_Data0;

  String doc_as_str;

  serializeJsonPretty(doc, doc_as_str);

  return doc_as_str;
}