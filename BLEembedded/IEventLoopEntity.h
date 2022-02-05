#pragma once

class IEventLoopEntity
{
  public:
    // Poll method for quasi-async behaviour
    virtual void Update() = 0;
};
