# # # # # mtconnect_publisher.py 

# import time                     # for sleeping between fetch cycles
# import json                     # for serializing our data into JSON
# import logging                  # for logging info and errors
# import requests                 # for making HTTP GET requests
# import xml.etree.ElementTree as ET  # for parsing XML responses
# from paho.mqtt import client as mqtt  # import the MQTT client class

# # MTConnect “current” endpoint URL of the UMC-750 device
# MTCONNECT_URL = "http://172.26.177.91:8082/UMC-750/current"

# # MQTT broker address
# MQTT_BROKER   = "broker.hivemq.com"

# # MQTT port (1883 = unencrypted)
# MQTT_PORT     = 1883

# # Topic under which we publish spindle speed JSON payloads
# MQTT_TOPIC    = "UMC750/spindleSpeed"

# # Configure root logger: include timestamp, log level, and message
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s: %(message)s"
# )

# # Instantiate the MQTT client; force callback API v1
# # pub = mqtt.Client(client_id="Publisher", callback_api_version=1)
# pub = mqtt.Client("Publisher")

# # Define a simple on_connect callback to confirm broker connection
# pub.on_connect = lambda rc: logging.info("Connected to MQTT (rc=%s)", rc)

# # Connect to the broker before publishing anything
# pub.connect(MQTT_BROKER, MQTT_PORT)
# # Start the network loop in a background thread to handle pings & reconnections
# pub.loop_start()

# def fetch_and_publish():
#     """
#     1) Fetch the “current” XML from the MTConnect agent.
#     2) Parse out the ACTUAL spindle speed.
#     3) Publish a small JSON blob over MQTT.
#     """
#     try:
#         # Request the current XML, with a 5-second timeout
#         resp = requests.get(MTCONNECT_URL, timeout=5)
#         # Raise an exception for HTTP errors (4xx or 5xx)
#         resp.raise_for_status()
#     except Exception as e:
#         # Log any errors contacting the MTConnect server
#         logging.error("MTConnect error: %s", e)
#         return

#     # Declare the XML namespace for MTConnect Streams v1.2
#     ns = {"m": "urn:mtconnect.org:MTConnectStreams:1.2"}
#     # Parse the XML into an ElementTree structure
#     root = ET.fromstring(resp.text)

#     # XPath to locate the <SpindleSpeed subType="ACTUAL"> element
#     xpath = (
#         ".//m:DeviceStream"
#         "/m:ComponentStream[@name='MachineController']"
#         "/m:Samples"
#         "/m:SpindleSpeed[@subType='ACTUAL']"
#     )
#     elem = root.find(xpath, ns)
#     if elem is None:
 
#         logging.warning("No spindle-speed found")
#         return

#     # Build a JSON payload with the timestamp attribute + speed value
#     payload = json.dumps({
#         "timestamp": elem.attrib["timestamp"],      # MTConnect timestamp
#         "spindle_speed": float(elem.text or 0)      # convert text to float
#     })

#     # Publish and check the return code (0 = success)
#     rc = pub.publish(MQTT_TOPIC, payload)[0]
#     if rc == 0:
#         logging.info("Published: %s", payload)
#     else:
#         logging.error("Publish failed")

# if __name__ == "__main__":
#     try:
#         # Continuously fetch + publish once per second
#         while True:
#             fetch_and_publish()
#             time.sleep(1)
#     except KeyboardInterrupt:
#         # Allow Ctrl+C to break the loop cleanly
#         pass
#     finally:
#         # Stop the background network loop and disconnect cleanly
#         pub.loop_stop()
#         pub.disconnect()











# Starting here for availability


import time
import json
import logging
import requests
import xml.etree.ElementTree as ET
from paho.mqtt import client as mqtt


MTCONNECT_URL = "https://smstestbed.nist.gov/vds/current" #change 1
MQTT_BROKER   = "broker.hivemq.com"
MQTT_PORT     = 1883
MQTT_TOPIC    = "UMC750/availability"
POLL_INTERVAL = 1.0  # seconds between fetches


# Set up logging so we can see timestamps, levels, and messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# Create an MQTT client and connect

pub = mqtt.Client("Publisher")       #instantiate new mqtt client with ID publisher
pub.on_connect = lambda rc: logging.info("MQTT connected (rc=%s)", rc) #As soon as the broker acknowledges our connection, we’ll see a log entry that includes the return code.
pub.connect(MQTT_BROKER, MQTT_PORT) #tells client to open a networrk connection to broker at the assigned port
pub.loop_start() # pings broker constantly



def fetch_and_publish():
    
    try:
        response = requests.get(MTCONNECT_URL, timeout=5)
        response.raise_for_status()
    except Exception as e:
        logging.error("MTConnect request failed: %s", e)
        return

    # XML namespace for Streams v2.0
    ns = {"m": "urn:mtconnect.org:MTConnectStreams:1.3"}

    # Parse XML
    root = ET.fromstring(response.text)

    # Build an XPath that finds the <Availability> under the Device component:
    #   <DeviceStream> → <ComponentStream component="Device"> → <Events> → <Availability>
    xpath = (
        ".//m:DeviceStream"
        "/m:ComponentStream[@component='Device']"    #change 2
        "/m:Events"
        "/m:Availability"
    )
    elem = root.find(xpath, ns)
    if elem is None:
        logging.warning("No <Availability> under component='Device' found")
        return

    # Prepare a JSON payload with timestamp and text value
    payload = json.dumps({
        "timestamp":    elem.attrib.get("timestamp", ""),
        "availability": elem.text or ""
    })

    # Publish and log success/failure
    rc = pub.publish(MQTT_TOPIC, payload)[0]
    if rc == 0:
        logging.info("Published: %s", payload)
    else:
        logging.error("Publish failed (rc=%s)", rc)

if __name__ == "__main__":
    try:
        while True:
            fetch_and_publish()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Interrupted by user; shutting down")
    finally:
        pub.loop_stop()
        pub.disconnect()
