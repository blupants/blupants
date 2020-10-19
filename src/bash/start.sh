#!/bin/sh
echo "Robot init script..."

INSTALL_PATH="/usr/local/lib/python3.5/dist-packages/blupants/"

if ls /boot/uEnv.txt  1> /dev/null 2>&1; then
  # Only run LED test for hardware that supports it (e.g. BeagleBone)
  /usr/bin/rc_test_leds
  sleep 5
fi

mkdir -p /tmp/blupants
mount -t tmpfs -o size=1M,mode=0755 tmpfs /tmp/blupants
echo "" > /tmp/blupants/blupants_rpc.py
chmod 777 /tmp/blupants/blupants_rpc.py
mkdir -p /var/lib/cloud9/BluPants
ln -s /tmp/blupants/blupants_rpc.py /var/lib/cloud9/BluPants/blupants_rpc.py

mkdir -p /var/blupants
cp /var/blupants/grab /tmp/blupants/grab

if ls /etc/blupants.json  1> /dev/null 2>&1; then
  cp $INSTALL_PATH/blupants.json /etc/blupants.json
fi

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
  #/usr/bin/rc_blink &
  /usr/bin/rc_test_leds
  export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  sleep 5

  # If robot is EduMip, uncomment the next line
  #/usr/bin/rc_balance_dstr -i dstr &
fi

echo "Ready to start blupants_client!"
python3 $INSTALL_PATH/blupants_client.py

echo "BluPants running..."
