#!/bin/sh
echo "Robot init script..."

/usr/bin/rc_test_leds

sleep 60

/usr/bin/rc_test_leds

/usr/bin/rc_balance_dstr -i dstr &
echo "Ready to start blupants_client."
/usr/bin/python3 /blupants/src/python/blupants/blupants_client.py