#pragma once

#include <ArduinoBLE.h>

#include "HWDef.h"

#include "IEventLoopEntity.h"

class CWatchdog : public IEventLoopEntity
{
  public:
    CWatchdog(BLELongCharacteristic & ping_attr,
              BLELongCharacteristic & countdown_attr,
              long timeout_s);

    void Update() override;

    bool Expired();

    void Reset();

  private:
    BLELongCharacteristic & m_PingAttr;
    BLELongCharacteristic & m_CountdownAttr;

    long m_Timeout_s;
    time_ms_type m_LastUpdated_ms;
};