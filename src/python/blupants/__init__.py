import blupants.blupants_client as blupants_client

global module_name
module_name = ""

def version():
    return "1.0.0a1"


def verbose(verbose_level):
    return verbose_level


def run(module):
    global module_name
    module_name = module
    if module_name == "blupants_client":
        blupants_client.run()


def shutdown():
    global module_name
    module_name = module
    if module_name == "blupants_client":
        blupants_client.shutdown()
