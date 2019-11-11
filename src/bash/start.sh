#!/bin/sh
echo "Robot init script..."

/usr/bin/rc_test_leds
sleep 5

mkdir -p /tmp/blupants
mount -t tmpfs -o size=20M,mode=0755 tmpfs /tmp/blupants
echo "print(\"RPC module resetting...\")" > /tmp/blupants/blupants_rpc.py
rm -rf /usr/local/lib/python3.5/dist-packages/blupants/blupants_rpc.py
ln -s /tmp/blupants/blupants_rpc.py /usr/local/lib/python3.5/dist-packages/blupants/blupants_rpc.py

echo "Waiting 60 seconds for network interface startup..."
sleep 60

if ls /dev/video* 1> /dev/null 2>&1; then
  /usr/bin/rc_test_leds
  sleep 5
	echo "QR Code WiFi setup..."
	/usr/local/bin/qrcode_wifi
	sleep 5
	echo "Starting video stream..."
	/usr/local/bin/video_stream > /dev/null 2>&1 &
else
	echo "Video device not found. Skipping video capture."
fi
echo "WiFi setup completed!"

/usr/bin/rc_blink &
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
sleep 5

/usr/bin/rc_balance_dstr -i dstr &
echo "Ready to start blupants_client!"
/usr/local/bin/blupants -m blupants_client > /dev/null 2>&1

echo "BluPants running..."
