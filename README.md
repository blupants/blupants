# BluPants: Web Based IDE for Coding Robots

Our goal is make robotics and programming available to anyone. 

BluPants is the most effective and fun way to learn coding. It is a free out of the box web based coding environment (IDE) that works with a variety of [robots](https://blupants.com/robots#cdd08a2f-fd49-403f-bec8-3e3e477ffc5a).

Pre-readers can start with the [basic block-based visual programming language](http://blupants.org/studio?level=0). Readers can use the [intermediate block-based visual](http://blupants.org/studio?level=1) for coding and gradually advanced to the [Python mode](http://blupants.org/studio?level=2) programming language.

All that using the same [BluPants IDE](http://blupants.org) with any of the supported [robots](https://blupants.com/robots#cdd08a2f-fd49-403f-bec8-3e3e477ffc5a).  

Visit [blupants.com](https://blupants.com) for more details.

## Welcome
Let's build a community for any child across the globe from the age of 5 to 99.

Compatibility with a variety of existing robotics hardware can make it affordable, at the same time we give unlimited flexibility to expand BluPants as far as the human imagination can go.

Check out this [video](https://youtu.be/xfamu1fHa2E) and see how you can take coding classes to the next level with real robots. We show how students can start with block-based visual programming language and gradually advance to Python.

## BluPants Python Documentation
The blupants Python module documentation can be found [here](http://blupants.org/help). Check all available functions for coding your robot with Python. 

## Get a Robot
Visit [blupants.com/robots](https://blupants.com/robots) or our [Hackster.io page](https://www.hackster.io/blupantsrobot/projects) for complete instructions on how to get your own robot up and running.

## Start Coding
Once you get your robot on and connected to the internet, simply visit [blupants.org](http://blupants.org) and start coding.

You may also visit our [blupants.com/lessons](https://blupants.com/lessons) to get some ideas on how code with BluPants.

## Dependencies
BluPants is based on the following projects:

[Python](https://www.python.org/)

[BeagleBone](https://beagleboard.org/bone)

[Raspberry Pi](https://www.raspberrypi.org/)

[LEGO® MINDSTORMS: ev3dev](https://www.ev3dev.org/)

[Blockly](https://developers.google.com/blockly)


## Manual Deployment
Run the following commands to get BluPants running in your BegaleBoneBlue:

    $ ssh beaglebone.local
    Make sure Python is installed
    $ python3 --version
    $ sudo su -
    $ cd /root
    Make sure rcpy is installed
    # python3 -m pip install rcpy --upgrade
    
    Disable usb0 gateway so ipv4 gateway gets assigned to wlan0
    # vi /etc/network/interfaces
    Comment the following line:
    #    gateway 192.168.7.1
    
    https://github.com/StrawsonDesign/librobotcontrol
    # git clone https://github.com/blupants/blupants.git
    # git clone https://github.com/StrawsonDesign/librobotcontrol.git
    # cp ./librobotcontrol/examples/src/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c.ORIGINAL
    # cp ./blupants/src/c/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c
    # cd librobotcontrol
    # make
    # cp ./examples/bin/rc_balance /usr/bin/rc_balance_dstr
    # cd
    # mkdir -p /etc/robotcontrol
    # cp ./blupants/src/bash/start.sh /etc/robotcontrol
    # chmod +x /etc/robotcontrol/start.sh
    # cp ./blupants/etc/blupants.service /etc/systemd/system/
    # mkdir -p /var/lib/cloud9/BluPants
    # cp ./blupants/src/python/reload.py /var/lib/cloud9/BluPants/
    # chmod +s /usr/bin/python3
    # apt-get install espeak
    # python3 -m pip install pyttsx3
    
    (If fails, try specific version)
    # python3 -m pip install pyttsx3==2.81

    # apt-get install autoconf-archive
    # python3 -m pip install blupants --upgrade
    # git clone https://github.com/brgl/libgpiod
    # cd libgpiod
    # ./autogen.sh --enable-tools=yes --enable-bindings-python --prefix=/usr/local
    
    Or in the case you get an error because libgpiod needs a newer kernel version, use older libgpiod
    https://github.com/aquaticus/nexus433/issues/21
    # wget https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/snapshot/libgpiod-1.1.1.tar.gz
    # tar xvf libgpiod-1.1.1.tar.gz
    # cd libgpiod-1.1.1
    # export PYTHON_VERSION=3
    # ./autogen.sh --enable-tools=yes --enable-bindings-python --prefix=/usr/local
    
    # make
    # make install
    # mv /usr/local/lib/python3.5/site-packages/* /usr/local/lib/python3.5/dist-packages/.
    # echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    # cd
    # cp -r blupants/src/python/blupants/* /usr/local/lib/python3.5/dist-packages/blupants/
    # cp /usr/local/lib/python3.5/dist-packages/blupants/blupants.json /root/
    # rm -rf /usr/local/lib/python3.5/dist-packages/blupants/*.pyc 
    # systemctl daemon-reload
    # systemctl enable blupants.service
    
