# Configuration of WiFi

COUNTRY = ""  # Change to the two-letter country code of your country, see https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
SSID = ""  # Change to the SSID aka name of your WiFi network
KEY = ""  # Change to the key aka password of your WiFi network

TIMEOUT = 10 # Set the timeout for the WiFi connection in sec
ON_CONNECT_FAIL = "reset" # Set to "reset" to reset the board if the WiFi fails to connect after the timeout, otherwise set to "" to terminate program execution

IP = ""  # Set IP, subnet, gateway and DNS if you want to set a static IP
SUBNET = ""  # Set IP, subnet, gateway and DNS if you want to set a static IP
GATEWAY = ""  # Set IP, subnet, gateway and DNS if you want to set a static IP
DNS = ""  # Set IP, subnet, gateway and DNS if you want to set a static IP

# Configuration of LED strip

NUM_LEDS = 96  # Change to the number of LEDs
COLOR_ORDER = "RGB"  # Set to color order of LED strip, one of "RGB", "RGBW" (RGB plus white), "RBG", "RBGW", "GRB", "GRBW", "GBR", "GBRW", "BRG", "BRGW", "BGR", "BGRW"
