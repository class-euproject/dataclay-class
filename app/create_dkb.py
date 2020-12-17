from dataclay.api import init, finish
import time

# Init dataClay session
init()

from CityNS.classes import *

def main():
    KBob = DKB()
    KBob.make_persistent(alias="DKB")
    KBob2 = DKB.get_by_alias("DKB") 
    print(KBob2)


if __name__ == "__main__":
    main()
    finish()
