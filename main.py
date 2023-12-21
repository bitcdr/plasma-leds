import asyncio
import config
import machine
import plasma
import requests
import time

from led_config import LedConfig
from microdot_asyncio import Microdot, Request, send_file
from network_manager import NetworkManager
from plasma import plasma_stick
from random import random, uniform

current_leds_config = {"type": ""}
next_leds_config = dict()


def hex_to_rgb(hex_color: str):
    hex_color_stripped = hex_color.replace("%23", "#").lstrip("#")
    return (int(hex_color_stripped[i : i + 2], 16) for i in (0, 2, 4))


def black(led_strip):
    for i in range(config.NUM_LEDS):
        led_strip.set_rgb(i, 0, 0, 0)


def uniform_rgb(led_strip, red: int, green: int, blue: int):
    for i in range(config.NUM_LEDS):
        led_strip.set_rgb(i, red, green, blue)


def uniform_hsv(led_strip, hue: float, saturation: float, value: float):
    for i in range(config.NUM_LEDS):
        led_strip.set_hsv(i, hue, saturation, value)


async def hex_color(led_strip):
    global current_leds_config
    global next_leds_config

    # The color
    color_r, color_g, color_b = hex_to_rgb(current_leds_config.get("color", "#f9f06b"))

    uniform_rgb(led_strip, color_r, color_g, color_b)


async def rgb_color(led_strip):
    global current_leds_config
    global next_leds_config

    # The color
    color_r = int(current_leds_config.get("red", "32"))
    color_r = min(255, max(0, color_r))
    color_g = int(current_leds_config.get("green", "64"))
    color_g = min(255, max(0, color_g))
    color_b = int(current_leds_config.get("blue", "128"))
    color_b = min(255, max(0, color_b))

    uniform_rgb(led_strip, color_r, color_g, color_b)


async def hsv_color(led_strip):
    global current_leds_config
    global next_leds_config

    # The color
    hue = float(current_leds_config.get("hue", "50")) / 360.0
    hue = max(0.0, min(1.0, hue))
    saturation = float(current_leds_config.get("saturation", "100")) / 100.0
    saturation = max(0.0, min(1.0, saturation))
    value = float(current_leds_config.get("value", "100")) / 100.0
    value = max(0.0, min(1.0, value))

    uniform_hsv(led_strip, hue, saturation, value)


async def cheerlights(led_strip):
    # With code from Piromoni Pico Plasma Stick examples
    # Copyright (c) 2021 Pimoroni Ltd | MIT License | https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/cheerlights.py

    global current_leds_config
    global next_leds_config

    # The update interval in minutes [2, ]
    update_interval_sec = int(current_leds_config.get("update-interval", 2)) * 60

    r, g, b = (0, 0, 0)
    first_run = True
    last_time = time.time()

    while True:
        if next_leds_config:
            return

        current_time = time.time()
        if first_run or abs(current_time - last_time) > update_interval_sec:
            response = requests.get(
                "http://api.thingspeak.com/channels/1417/field/2/last.json"
            )
            hex_color = response.json()["field2"]
            response.close()

            r, g, b = hex_to_rgb(hex_color)
            first_run = False
            last_time = current_time

        uniform_rgb(led_strip, r, g, b)

        await asyncio.sleep(1)


async def fire(led_strip):
    # With code from Piromoni Pico Plasma Stick examples
    # Copyright (c) 2021 Pimoroni Ltd | MIT License | https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/fire.py

    global current_leds_config
    global next_leds_config

    # The update rate of the LEDs per second [1, 60]
    update_rate = int(current_leds_config.get("update-rate", "10"))
    update_rate = min(60, max(1, update_rate))

    while True:
        if next_leds_config:
            return

        for i in range(config.NUM_LEDS):
            led_strip.set_hsv(i, uniform(0.0, 50 / 360), 1.0, random())

        await asyncio.sleep(1.0 / update_rate)


async def police(led_strip):
    global current_leds_config
    global next_leds_config

    half_num_leds = int(config.NUM_LEDS / 2)

    # The left and right colors
    left_color_r, left_color_g, left_color_b = hex_to_rgb(
        current_leds_config.get("left-color", "#0000ee")
    )
    right_color_r, right_color_g, right_color_b = hex_to_rgb(
        current_leds_config.get("right-color", "#ee0000")
    )

    # The flash count [1, ]
    flash_count = int(current_leds_config.get("flash-count", "5"))
    flash_count = min(60, max(1, flash_count))

    # The update rate of the LEDs per second [1, 120]
    update_rate = int(current_leds_config.get("update-rate", "20"))
    update_rate = min(120, max(1, update_rate))

    # The spacing
    spacing = int(current_leds_config.get("spacing", "5"))
    spacing = min(half_num_leds - 2, max(1, spacing))

    while True:
        if next_leds_config:
            return

        for left_color_counter in range(flash_count):
            for i in range(config.NUM_LEDS):
                if i < half_num_leds and i % spacing == 0:
                    led_strip.set_rgb(i, left_color_r, left_color_g, left_color_b)

            await asyncio.sleep(1.0 / update_rate)

            for i in range(config.NUM_LEDS):
                led_strip.set_rgb(i, 0, 0, 0)

            await asyncio.sleep(1.0 / update_rate)

        for right_color_counter in range(flash_count):
            for i in range(config.NUM_LEDS):
                if i > half_num_leds and i % spacing == 0:
                    led_strip.set_rgb(i, right_color_r, right_color_g, right_color_b)

            await asyncio.sleep(1.0 / update_rate)

            for i in range(config.NUM_LEDS):
                led_strip.set_rgb(i, 0, 0, 0)

            await asyncio.sleep(1.0 / update_rate)


async def rainbow(led_strip):
    # With code from Piromoni Pico Plasma Stick examples
    # Copyright (c) 2021 Pimoroni Ltd | MIT License | https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/rainbows.py

    global current_leds_config
    global next_leds_config

    # The speed that the LEDs cycle at [0, 255]
    cycle_speed = int(current_leds_config.get("cycle-speed", "20"))
    cycle_speed = min(255, max(0, cycle_speed))

    # The update rate of the LEDs per second [1, 120]
    update_rate = int(current_leds_config.get("update-rate", "60"))
    update_rate = min(120, max(1, update_rate))

    offset = 0.0

    while True:
        if next_leds_config:
            return

        offset += float(cycle_speed) / 2000.0

        for i in range(config.NUM_LEDS):
            hue = float(i) / config.NUM_LEDS
            led_strip.set_hsv(i, hue + offset, 1.0, 1.0)

        await asyncio.sleep(1.0 / update_rate)


async def alternating(led_strip):
    # With code from Piromoni Pico Plasma Stick examples
    # Copyright (c) 2021 Pimoroni Ltd | MIT License | https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/alternating-blinkies.py

    global current_leds_config
    global next_leds_config

    # The left and right colors
    left_color_r, left_color_g, left_color_b = hex_to_rgb(
        current_leds_config.get("left-color", "#88ccff")
    )
    right_color_r, right_color_g, right_color_b = hex_to_rgb(
        current_leds_config.get("right-color", "#8855ff")
    )

    # The wait time in seconds [1, ]
    wait_time = int(current_leds_config.get("wait-time", 1))
    wait_time = max(1, wait_time)

    while True:
        if next_leds_config:
            return

        for i in range(config.NUM_LEDS):
            # the if statements below use a modulo operation to identify the even and odd numbered LEDs
            if (i % 2) == 0:
                led_strip.set_rgb(i, left_color_r, left_color_g, left_color_b)
            else:
                led_strip.set_rgb(i, right_color_r, right_color_g, right_color_b)

        await asyncio.sleep(wait_time)

        for i in range(config.NUM_LEDS):
            if (i % 2) == 0:
                led_strip.set_rgb(i, right_color_r, right_color_g, right_color_b)
            else:
                led_strip.set_rgb(i, left_color_r, left_color_g, left_color_b)

        await asyncio.sleep(wait_time)


async def sparkles(led_strip):
    # With code from Piromoni Pico Plasma Stick examples
    # Copyright (c) 2021 Pimoroni Ltd | MIT License | https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/sparkles.py

    global current_leds_config
    global next_leds_config

    # The background and sparkles colors
    bg_color_r, bg_color_g, bg_color_b = hex_to_rgb(
        current_leds_config.get("bg-color", "#000000")
    )
    sparkles_color_r, sparkles_color_g, sparkles_color_b = hex_to_rgb(
        current_leds_config.get("sparkles-color", "#ffffff")
    )

    # The fade up and fade down speeds
    fade_up_speed = int(current_leds_config.get("fade-up-speed", "255"))
    fade_up_speed = max(1, min(255, fade_up_speed))
    fade_down_speed = int(current_leds_config.get("fade-down-speed", "1"))
    fade_down_speed = max(1, min(255, fade_down_speed))

    # The intensity
    intensity = int(current_leds_config.get("intensity", "2"))
    intensity = max(1, intensity)
    intensity_norm = 1.0 * intensity / 10000.0

    # Create a list of [r, g, b] values that will hold current LED colours, for display
    current_leds = [[0] * 3 for i in range(config.NUM_LEDS)]
    # Create a list of [r, g, b] values that will hold target LED colours, to move towards
    target_leds = [[0] * 3 for i in range(config.NUM_LEDS)]

    while True:
        if next_leds_config:
            return

        for i in range(config.NUM_LEDS):
            # Randomly add sparkles
            if intensity_norm > uniform(0, 1):
                # Set a target to start a sparkle
                target_leds[i] = [sparkles_color_r, sparkles_color_g, sparkles_color_b]
            # Slowly reset sparkle to background
            if current_leds[i] == target_leds[i]:
                target_leds[i] = [bg_color_r, bg_color_g, bg_color_b]

        # Nudge our current colours closer to the target colours
        for i in range(config.NUM_LEDS):
            for c in range(3):  # 3 times, for R, G & B channels
                if current_leds[i][c] < target_leds[i][c]:
                    current_leds[i][c] = min(
                        current_leds[i][c] + fade_up_speed, target_leds[i][c]
                    )  # Increase current, up to a maximum of target
                elif current_leds[i][c] > target_leds[i][c]:
                    current_leds[i][c] = max(
                        current_leds[i][c] - fade_down_speed, target_leds[i][c]
                    )  # Reduce current, down to a minimum of target

        for i in range(config.NUM_LEDS):
            led_strip.set_rgb(
                i, current_leds[i][0], current_leds[i][1], current_leds[i][2]
            )

        await asyncio.sleep(0)


async def fade_timer(led_strip):
    global current_leds_config
    global next_leds_config

    # The start and target colors
    start_hue = float(current_leds_config.get("start-hue", "50")) / 360.0
    start_hue = max(0.0, min(1.0, start_hue))
    start_saturation = float(current_leds_config.get("start-saturation", "100")) / 100.0
    start_saturation = max(0.0, min(1.0, start_saturation))
    start_value = float(current_leds_config.get("start-value", "100")) / 100.0
    start_value = max(0.0, min(1.0, start_value))

    target_hue = int(current_leds_config.get("target-hue", 50)) / 360.0
    target_hue = max(0.0, min(1.0, target_hue))
    target_saturation = (
        float(current_leds_config.get("target-saturation", "100")) / 100.0
    )
    target_saturation = max(0.0, min(1.0, target_saturation))
    target_value = float(current_leds_config.get("target-value", "100")) / 100.0
    target_value = max(0.0, min(1.0, target_value))

    # The fade time
    fade_time_ms = int(current_leds_config.get("fade-time", "5")) * 60 * 1000
    fade_time_ms = max(1, min(86400 * 1000, fade_time_ms))

    # The control vars
    hue_delta = target_hue - start_hue
    saturation_delta = target_saturation - start_saturation
    value_delta = target_value - start_value
    start_time_ms = time.ticks_ms()

    while True:
        if next_leds_config:
            return

        elapsed_time_ms = time.ticks_diff(time.ticks_ms(), start_time_ms)
        ratio = max(0.0, min(1.0, elapsed_time_ms / fade_time_ms))

        current_hue = max(0.0, min(1.0, start_hue + ratio * hue_delta))
        current_saturation = max(
            0.0, min(1.0, start_saturation + ratio * saturation_delta)
        )
        current_value = max(0.0, min(1.0, start_value + ratio * value_delta))

        for i in range(config.NUM_LEDS):
            led_strip.set_hsv(i, current_hue, current_saturation, current_value)

        await asyncio.sleep(0.1)


async def count_up(led_strip):
    global current_leds_config
    global next_leds_config

    # The color
    color_r, color_g, color_b = hex_to_rgb(current_leds_config.get("color", "#ffffff"))

    # The time
    time_ms = int(current_leds_config.get("time", "1")) * 60 * 1000
    time_ms = max(60 * 1000, time_ms)

    # The action at end
    action = current_leds_config.get("action", "freeze")

    start_time_ms = time.ticks_ms()

    while True:
        if next_leds_config:
            return

        elapsed_time_ms = time.ticks_diff(time.ticks_ms(), start_time_ms)
        ratio = max(0.0, min(1.0, elapsed_time_ms / time_ms))

        num_leds_on = int(config.NUM_LEDS * ratio)

        for i in range(config.NUM_LEDS):
            if i < num_leds_on:
                led_strip.set_rgb(i, color_r, color_g, color_b)
            else:
                led_strip.set_rgb(i, 0, 0, 0)

        if num_leds_on < config.NUM_LEDS:
            await asyncio.sleep(0.1)
        else:
            break

    if action == "flash":
        for flash_count in range(10):
            if next_leds_config:
                return

            black(led_strip)
            await asyncio.sleep(1)

            uniform_rgb(led_strip, color_r, color_g, color_b)
            await asyncio.sleep(1)


async def leds(led_strip):
    global current_leds_config
    global next_leds_config

    while True:
        if next_leds_config:
            black(led_strip)
            current_leds_config = next_leds_config
            next_leds_config = dict()

        if current_leds_config["type"] == "hex-color":
            await hex_color(led_strip)
        elif current_leds_config["type"] == "rgb-color":
            await rgb_color(led_strip)
        elif current_leds_config["type"] == "hsv-color":
            await hsv_color(led_strip)
        elif current_leds_config["type"] == "fire":
            await fire(led_strip)
        elif current_leds_config["type"] == "rainbow":
            await rainbow(led_strip)
        elif current_leds_config["type"] == "cheerlights":
            await cheerlights(led_strip)
        elif current_leds_config["type"] == "police":
            await police(led_strip)
        elif current_leds_config["type"] == "alternating":
            await alternating(led_strip)
        elif current_leds_config["type"] == "sparkles":
            await sparkles(led_strip)
        elif current_leds_config["type"] == "fade-timer":
            await fade_timer(led_strip)
        elif current_leds_config["type"] == "count-up":
            await count_up(led_strip)

        current_leds_config["type"] = "none"

        await asyncio.sleep(0.1)


app = Microdot()


@app.route("chota.min.css")
async def chota_css(req: Request):
    return send_file("frontend/chota.min.css", content_type="text/css", max_age=86400)


@app.route("storage.js")
async def storage_js(req: Request):
    return send_file(
        "frontend/storage.js", content_type="application/javascript", max_age=86400
    )


@app.route("/", methods=["GET"])
async def index(req: Request):
    global next_leds_config

    if req.method == "GET" and req.query_string is not None:
        for key_value_pair in str(req.query_string).split("&"):
            key_and_value = key_value_pair.split("=", 1)
            next_leds_config[key_and_value[0]] = key_and_value[1]

    return send_file("frontend/index.html")


async def main():
    print(f"Connecting to WiFi with SSID {config.SSID}")
    network_manager = NetworkManager(config.COUNTRY)
    if config.IP and config.SUBNET and config.GATEWAY and config.DNS:
        network_manager.connect_static_ip(
            config.SSID,
            config.KEY,
            config.IP,
            config.SUBNET,
            config.GATEWAY,
            config.DNS,
            config.TIMEOUT,
        )
    else:
        network_manager.connect(config.SSID, config.KEY, config.TIMEOUT)

    if network_manager.isconnected():
        print(
            f"Connected to WiFi with SSID {config.SSID} and IP {network_manager.ip()}"
        )
    else:
        print(
            f"Failed to connected to WiFi with SSID {config.SSID} and IP {network_manager.ip()}"
        )

        if config.ON_CONNECT_FAIL == "reset":
            print("Resetting board")
            machine.reset()
        else:
            print("Terminating program execution")
            return

    print(
        f"Setting up LED strip with {config.NUM_LEDS} LEDs and color order {config.COLOR_ORDER}"
    )
    led_config = LedConfig(config.NUM_LEDS, config.COLOR_ORDER)
    led_strip = plasma.WS2812(
        config.NUM_LEDS,
        0,
        0,
        plasma_stick.DAT,
        rgbw=led_config.is_rgbw(),
        color_order=led_config.color_order(),
    )
    led_strip.start()
    print("Set up LED strip")

    print(f"Starting webserver at http://{network_manager.ip()}")
    leds_task = asyncio.create_task(leds(led_strip))
    control_task = asyncio.create_task(app.start_server(port=80))
    await asyncio.gather(leds_task, control_task)


if __name__ == "__main__":
    asyncio.run(main())
