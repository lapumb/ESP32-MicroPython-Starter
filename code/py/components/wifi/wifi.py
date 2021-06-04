def connect(ssid: str, password: str) -> None:
    from network import WLAN, STA_IF

    wlan = WLAN(STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("connecting to wifi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass

    print("Wifi connected successfully")
    print("network config:", wlan.ifconfig())

def is_connected() -> bool:
    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    return wlan.isconnected()