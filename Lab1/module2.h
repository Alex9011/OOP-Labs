#pragma once
#include <windows.h>

// Підтверджене число належить діапазону 1..100.
// При скасуванні number залишається незмінним.
bool ShowNumberDialog(HWND owner, int& number);
