import network
import time
import machine


_DEFAULT_NETWORK_ADDRESS = "0.0.0.0"


class NetworkManager:
    """Blocking network connection to a WiFi network in station aka client mode"""

    def __init__(self, country: str = "XX", status_led: bool = True):
        network.country(country)

        self._sta_if = network.WLAN(network.STA_IF)
        self._sta_if.active(True)

        if status_led:
            self.status_led = machine.Pin("LED", machine.Pin.OUT)
        else:
            self.status_led = None

    def connect(self, ssid: str, key: str, timeout: int = 10):
        self._sta_if.connect(ssid, key)

        # Wait for connection and blink on-board LED in the meanwhile
        for wait_count in range(timeout):
            if self._sta_if.isconnected():
                return
            
            if self.status_led is not None:
                self.status_led.value(True)
            time.sleep_ms(500)

            if self.status_led is not None:
                self.status_led.value(False)
            time.sleep_ms(500)

    def connect_static_ip(
        self,
        ssid: str,
        key: str,
        ip: str,
        subnet: str,
        gateway: str,
        dns: str,
        timeout: int = 10,
    ):
        self._sta_if.ifconfig((ip, subnet, gateway, dns))
        self.connect(ssid, key, timeout)

    def isconnected(self) -> bool:
        return self._sta_if.isconnected()

    def ip(self) -> str:
        if self.isconnected():
            return self._sta_if.ifconfig()[0]
        return _DEFAULT_NETWORK_ADDRESS

    def subnet(self) -> str:
        if self.isconnected():
            return self._sta_if.ifconfig()[1]
        return _DEFAULT_NETWORK_ADDRESS

    def gateway(self) -> str:
        if self.isconnected():
            return self._sta_if.ifconfig()[2]
        return _DEFAULT_NETWORK_ADDRESS

    def dns(self) -> str:
        if self.isconnected():
            return self._sta_if.ifconfig()[3]
        return _DEFAULT_NETWORK_ADDRESS
