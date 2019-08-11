# BluPants: Open Source robot programming

BluPants is a Python based module to control robots and IoT automation devices via [BluPants Coding Lab](https://blupants.org). Visit https://blupants.com for more details.

The Project goal is make robotics and programming available to anyone. 

## Welcome
Let's build an open source community for any child across the globe from the age of 5 to 99.
Together we can build the tools to make the journey to STEM accessible to anyone.

Open source hardware and software can make it affordable, at the same time we give unlimited flexibility to expand BluPants as far as the human imagination can go.


## Dependencies
BluPants is based exclusively on open source solution:

[BeagleBoneBlue](https://beagleboard.org/blue)

[EduMIP](https://beagleboard.org/p/edumip/edumip-13a29c)

Robot Control Library - [documentation](http://strawsondesign.com/docs/librobotcontrol/) / [Github](https://github.com/StrawsonDesign/librobotcontrol)

RCPy - [documentation](https://guitar.ucsd.edu/rcpy/html/index.html) / [Github](https://github.com/mcdeoliveira/rcpy)

[Blockly](https://developers.google.com/blockly/)

[Scratch](https://scratch.mit.edu)


## Deployment
Run the following commands to get BluPants running in your BegaleBoneBlue:

    $ ssh beaglebone.local
    Make sure Python is installed
    $ python3 --version
    $ sudo su -
    $ cd /root
    Make sure rcpy is installed
    # pip3 install rcpy --upgrade
    https://github.com/StrawsonDesign/librobotcontrol
    # git clone git@github.com:blupants/blupants.git
    # git clone https://github.com/StrawsonDesign/librobotcontrol.git
    # cp ./librobotcontrol/examples/src/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c.ORIGINAL
    # cp ./blupants/src/c/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c
    # cd librobotcontrol
    # make
    # cp ./examples/bin/rc_balance /usr/bin/rc_balance_dstr
    # cp ./blupants/src/c/start.sh /etc/robotcontrol
    # rm /etc/robotcontrol/link_to_startup_program
    # ln -s /etc/robotcontrol/start.sh /etc/robotcontrol/link_to_startup_program
    # /etc/robotcontrol/link_to_startup_program
    
