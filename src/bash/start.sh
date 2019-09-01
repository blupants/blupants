#!/bin/sh
echo "Robot init script..."

/usr/bin/rc_test_leds

echo "Waiting 30 seconds for network interface startup..."
sleep 30

/usr/bin/rc_test_leds

echo "QR Code WiFi setup..."
/usr/local/bin/qrcode_wifi

sleep 5

echo "WiFi setup completed!"
/usr/bin/rc_blink &

sleep 5

/usr/bin/rc_balance_dstr -i dstr &
echo "Ready to start blupants_client!"
/usr/local/bin/blupants -m blupants_client > /var/log/blupants_client.log 2>&1

echo "BluPants running..."