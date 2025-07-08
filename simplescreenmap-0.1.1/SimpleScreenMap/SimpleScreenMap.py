import ctypes
from ctypes import wintypes
class Display:
    def __init__(self, name, width, height, originX, originY, primary):
        self.name = name
        self.width = width
        self.height = height
        self.originX = originX
        self.originY = originY
        self.primary = primary

    def __repr__(self):
        return f"Display(name='{self.name}', width={self.width}, height={self.height}, originX={self.originX}, originY={self.originY}, primary={self.primary})"

def getDisplays():
    """Returns a list of displays. each display has properties, .name, .width, .height, .originX, .originY"""
    user32 = ctypes.windll.user32
    shcore = ctypes.windll.shcore
    displays = []
    MONITORINFOF_PRIMARY = 0x00000001

    try:
        shcore.SetProcessDpiAwareness(2)
    except Exception:
        print("DPI Scaling failed")

    class RECT(ctypes.Structure):
        _fields_ = [
            ('left', ctypes.c_long),
            ('top', ctypes.c_long),
            ('right', ctypes.c_long),
            ('bottom', ctypes.c_long)
        ]

    class MONITORINFOEX(ctypes.Structure):
        _fields_ = [
            ('cbSize', wintypes.DWORD),
            ('rcMonitor', RECT),
            ('rcWork', RECT),
            ('dwFlags', wintypes.DWORD),
            ('szDevice', wintypes.WCHAR * 32)
        ]

    def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        mi = MONITORINFOEX()
        mi.cbSize = ctypes.sizeof(MONITORINFOEX)
        if user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi)):
            width = mi.rcMonitor.right - mi.rcMonitor.left
            height = mi.rcMonitor.bottom - mi.rcMonitor.top
            originX = mi.rcMonitor.left
            originY = mi.rcMonitor.top
            name = mi.szDevice
            primary = (mi.dwFlags & MONITORINFOF_PRIMARY) != 0
            displays.append(Display(name, width, height, originX, originY, primary))
        return True

    MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)
    user32.EnumDisplayMonitors(0, 0, MonitorEnumProc(monitor_enum_proc), 0)
    displays.sort(key=lambda d: not d.primary)

    return displays

def screenPosition(x=0.5, y=0.5,display=0, bordered=True, relative=False):
    """
    (x=0.5, y=0.5, display=0, bordered=True, relative=False).
    x, y - ranging from 0 to 1, determines the position from the origin. 0.5, 0.5 is the center.
    display - The display to do the calculation for. 0 is primary display. Set relative to True for a position relative to that display's origin
    bordered - If True, position can not extend past the screen.
    relative - If True, the position is relative to the display's origin. Does not affect primary display.
    """
    display = getDisplays()[display]
    if bordered:
        x = max(0, min(x, 1))
        y = max(0, min(y, 1))
    x *= display.width
    y *= display.height
    Pos = (x, y)
    if not relative:
        Pos = (Pos[0]+display.originX, Pos[1]+display.originY)
    return Pos[0], Pos[1]
def screenPositionCentered(x=0, y=0, display=0, bordered=True, relative=False):
    """
    (x=0, y=0, display=0, bordered=True, relative=False).
    x, y - ranging from -1 to 1, determines the position from the center. 0, 0 is the center.
    display - The display to do the calculation for. 0 is primary display. Set relative to True for a position relative to that display's origin
    bordered - If True, position can not extend past the screen.
    relative - If True, the position is relative to the display's origin. Does not affect primary display.
    """
    display = getDisplays()[display]
    if bordered:
        x = max(-1, min(x, 1))
        y = max(-1, min(y, 1))
    x = x / 2 + 0.5
    y = y / 2 + 0.5
    x *= display.width
    y *= display.height
    Pos = (x, y)
    if not relative:
        Pos = (Pos[0]+display.originX, Pos[1]+display.originY)
    return Pos[0], Pos[1]
def positionPercent(x=0, y=0, display=0, bordered=True):
    """(x=0, y=0, display=0, bordered=True).
    x, y - The pixel on screen. Returns values from (0, 0) to (1, 1) relative to the origin.
    display - The display to perform the calculation on.
    bordered - Limits pixels to the display"""
    display = getDisplays()[display]
    x = display.width / x
    y = display.height / y
    if bordered:
        x = max(0, min(x, 1))
        y = max(0, min(y, 1))
    return x, y
