from dataclay.api import init, finish
from dataclay import getRuntime 
from dataclay.api import get_backend_id_by_name
import time
import uuid

# Init dataClay session
init()

from CityNS.classes import DKB, Object, EventsSnapshot

def main():
    try:
        KBob = DKB.get_by_alias("DKB")
    except Exception:
        KBob = DKB()
        KBob.make_persistent(alias="DKB")

    while True:
        print("Checking Events Snapshot received...")
        kb = KBob.kb
        last_timestamp = 0
        if len(kb) > 0:
            last_timestamp = next(reversed(sorted(list(kb.keys()))))
        print(f"Number of snapshots {len(list(kb.keys()))} and number of objects {len(list(KBob.objects.keys()))} and last timestamp "
              f"{last_timestamp}")
        """
        for timestamp in list(kb.keys()):
            ts = timestamp
            eventSnap = kb[timestamp]
            current_snap_alias = eventSnap.snap_alias
            print("Snapshot " + current_snap_alias + " found.")
            for event in eventSnap.events:
                obj = event.detected_object
                print(obj)
            print("#################")
        """
        time.sleep(5)
        # if len(kb) > 0:
        #    KBob.remove_old_snapshots_and_objects(last_timestamp, False)


if __name__ == "__main__":
    main()
    finish()
