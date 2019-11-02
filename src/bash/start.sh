#!/bin/sh
echo "Robot init script..."

/usr/bin/rc_test_leds

echo "Waiting 30 seconds for network interface startup..."
sleep 15

mkdir -p /tmp/motion

sleep 5

if ls /dev/video* 1> /dev/null 2>&1; then
	echo "Initializing video capture..."
	/usr/bin/motion &

	sleep 10

	/usr/bin/rc_test_leds

	echo "QR Code WiFi setup..."
	/usr/local/bin/qrcode_wifi

	sleep 5
else
	echo "Video device not found. Skipping video capture."
fi

echo "WiFi setup completed!"
/usr/bin/rc_blink &

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

sleep 5

/usr/bin/rc_balance_dstr -i dstr &
echo "Ready to start blupants_client!"
/usr/local/bin/blupants -m blupants_client > /var/log/blupants_client.log 2>&1

echo "BluPants running..."
