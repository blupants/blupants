# BluPants: Agnostic Programming Platform for Robots

BluPants is a Python based module to control robots and IoT automation devices via [BluPants Coding Lab](https://blupants.org). Visit https://blupants.com for more details.

The Project goal is make robotics and programming available to anyone. 

## Welcome
Let's build a community for any child across the globe from the age of 5 to 99.
Together we can build the tools to make the journey to STEM accessible to anyone.

Compatibility with a variety of existing robotics hardware can make it affordable, at the same time we give unlimited flexibility to expand BluPants as far as the human imagination can go.


## Dependencies
BluPants is based on the following projects:

[BeagleBoneBlue](https://beagleboard.org/blue)

[EduMIP](https://beagleboard.org/p/edumip/edumip-13a29c)

Robot Control Library - [documentation](http://strawsondesign.com/docs/librobotcontrol/) / [Github](https://github.com/StrawsonDesign/librobotcontrol)

RCPy - [documentation](https://guitar.ucsd.edu/rcpy/html/index.html) / [Github](https://github.com/mcdeoliveira/rcpy)

[Blockly](https://developers.google.com/blockly/)


## Deployment
Run the following commands to get BluPants running in your BegaleBoneBlue:

    $ ssh beaglebone.local
    Make sure Python is installed
    $ python3 --version
    $ sudo su -
    $ cd /root
    Make sure rcpy is installed
    # python3 -m pip install rcpy --upgrade
    https://github.com/StrawsonDesign/librobotcontrol
    # git clone https://github.com/blupants/blupants.git
    # git clone https://github.com/StrawsonDesign/librobotcontrol.git
    # cp ./librobotcontrol/examples/src/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c.ORIGINAL
    # cp ./blupants/src/c/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c
    # cd librobotcontrol
    # make
    # cp ./examples/bin/rc_balance /usr/bin/rc_balance_dstr
    # cd
    # cp ./blupants/src/bash/start.sh /etc/robotcontrol
    # chmod +x /etc/robotcontrol/start.sh
    # cp ./blupants/etc/blupants.service /etc/systemd/system/
    # mdkir -p /var/lib/cloud9/BluPants
    # cp ./blupants/src/python/*.py /var/lib/cloud9/BluPants/
    # chmod +s /usr/bin/python3
    # python3 -m pip install blupants --upgrade
    # git clone https://github.com/brgl/libgpiod
    # cd libgpiod
    # apt-get install autoconf-archive
    # ./autogen.sh --enable-tools=yes --enable-bindings-python --prefix=/usr/local
    # make
    # make install
    # mv /usr/local/lib/python3.5/site-packages/* /usr/local/lib/python3.5/dist-packages/.
    # echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    # cd
    # cp -r blupants/src/python/blupants/*.py /usr/local/lib/python3.5/dist-packages/blupants/
    # cp -r blupants/src/python/blupants/templates /usr/local/lib/python3.5/dist-packages/blupants/
    # rm -rf /usr/local/lib/python3.5/dist-packages/blupants/*.pyc 
    # systemctl daemon-reload
    # systemctl enable blupants.service
    
