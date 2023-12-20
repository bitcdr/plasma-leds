import plasma


_COLOR_ORDERS = {
    "RGB": plasma.COLOR_ORDER_RGB,
    "RBG": plasma.COLOR_ORDER_RBG,
    "GRB": plasma.COLOR_ORDER_GRB,
    "GBR": plasma.COLOR_ORDER_GBR,
    "BRG": plasma.COLOR_ORDER_BRG,
    "BGR": plasma.COLOR_ORDER_BGR,
}


class LedConfig:
    """Configuration for a LED strip"""

    def __init__(self, num_leds: int, color_order: str):
        self._num_leds = num_leds
        self._white = color_order.endswith("W")
        self._color_order = _COLOR_ORDERS[color_order[:3]]

    def num_leds(self) -> int:
        return self._num_leds

    def is_rgbw(self) -> bool:
        return self._white

    def color_order(self):
        return self._color_order
