#pragma once
#include <windows.h>
#include <string>

// true: натиснуто "Так"; false: скасування або помилка.
// text змінюється лише після підтвердження.
bool ShowTextDialog(HWND owner, std::wstring& text);
