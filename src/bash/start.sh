#!/bin/sh
echo "Robot init script..."

/usr/bin/rc_test_leds

echo "Waiting 30 seconds for network setup."
sleep 30

/usr/bin/rc_blink &
sleep 5

/usr/bin/rc_balance_dstr -i dstr &
echo "Ready to start blupants_client."
/usr/bin/python3 /root/blupants/src/python/blupants/blupants_client.py