#!/bin/sh
echo "Robot init script..."

if ls /boot/uEnv.txt  1> /dev/null 2>&1; then
  # Only run LED test for hardware that supports it (e.g. BeagleBone)
  /usr/bin/rc_test_leds
  sleep 5
  echo "Waiting 45 seconds for network interface startup..."
  sleep 45
fi

mkdir -p /tmp/blupants
mount -t tmpfs -o size=1M,mode=0755 tmpfs /tmp/blupants
echo "print(\"RPC module resetting...\")" > /tmp/blupants/blupants_rpc.py
rm -rf /usr/local/lib/python3.5/dist-packages/blupants/blupants_rpc.py
ln -s /tmp/blupants/blupants_rpc.py /usr/local/lib/python3.5/dist-packages/blupants/blupants_rpc.py


if ls /dev/video* 1> /dev/null 2>&1; then
  if ls /boot/uEnv.txt  1> /dev/null 2>&1; then
    /usr/bin/rc_test_leds
    sleep 5
    echo "QR Code WiFi setup..."
    /usr/local/bin/qrcode_wifi
    sleep 5
  fi
  echo "Starting video stream..."
  /usr/local/bin/video_stream > /dev/null 2>&1 &
else
  echo "Video device not found. Skipping video capture."
fi
echo "WiFi setup completed!"

if ls /boot/uEnv.txt  1> /dev/null 2>&1; then
  /usr/bin/rc_blink &
  export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  sleep 5

  /usr/bin/rc_balance_dstr -i dstr &
fi

echo "Ready to start blupants_client!"
python3 /usr/local/lib/python3.5/dist-packages/blupants/blupants_client.py

echo "BluPants running..."
