# Script to send a python code to be executed by Blupants robot
#
# Sample usage:
# python3 send_blupants_code.py my_code.py "192.168.0.103"
#
# Where:
# my_code.py: Python source code you want your robot to execute
# 192.168.0.103: The IP address of your robot

import json
import os
import requests
import sys

global url, robot_ip, robot_code, robot_code_file

url = "http://blupants.org/api/v1/code"

robot_ip = "127.0.0.1"
robot_code = "print(\"Hello world!\")"
robot_code_file = "blupants_sample_code.py"

def main():
    global url, robot_ip, robot_code, robot_code_file

    if len(sys.argv) > 1:
        robot_code_file = sys.argv[1]

    if len(sys.argv) > 2:
        robot_ip = sys.argv[2]

    if os.path.exists(robot_code_file):
        with open(robot_code_file) as f:
            robot_code = f.read()

    # payload="{\"id\":\"192.168.0.103\",\"code\":{\"version\":1,\"type\":\"python\",\"payload\":\"robot.camera_toggle()\\n\"}}"
    payload = {"id": robot_ip, "code": {"version": 1, "type": "python", "payload": robot_code}}
    payload = json.dumps(payload)

    headers = {
      'Content-Type': 'application/json'
    }

    # curl -i -s -k -X $'POST' \
    #     -H $'Content-Type: application/json' \
    #     --data-binary $'{\"id\":\"192.168.0.103\",\"code\":{\"version\":1,\"type\":\"python\",\"payload\":\"robot.camera_toggle()\\n\"}}' \
    #     $'http://blupants.org/api/v1/code'
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


if __name__ == "__main__":
    main()