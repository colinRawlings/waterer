#include "Watchdog.h"

CWatchdog::CWatchdog(BLELongCharacteristic & ping_attr,
                     BLELongCharacteristic & countdown_attr,
                     long timeout_s)
    : m_PingAttr(ping_attr)
    , m_CountdownAttr(countdown_attr)
    , m_Timeout_s(timeout_s)
    , m_LastUpdated_ms(millis())
{}

bool CWatchdog::Expired()
{
    if (m_CountdownAttr.value() < 1)
    {
        return true;
    }

    return false;
}

void CWatchdog::Reset()
{
    m_CountdownAttr.writeValue(m_Timeout_s);
}

void CWatchdog::Update()
{
    if (m_PingAttr.written())
    {
        m_CountdownAttr.writeValue(m_Timeout_s);
        return;
    }

    if (millis() - m_LastUpdated_ms > 1000)
    {
        m_LastUpdated_ms = millis();

        if (m_CountdownAttr <= 0)
            return;

        m_CountdownAttr.writeValue(m_CountdownAttr.value() - 1);
    }
}