#include "Version.h"

extern const int VERSION_MAJOR = 1;
extern const int VERSION_MINOR = 0;

float GetVersion() { return VERSION_MAJOR + 0.1 * VERSION_MINOR; }