from dataclay.api import init, finish
from storage.api import getByID
from dataclay import getRuntime 
from dataclay.api import get_backend_id_by_name
import time
import uuid

# Init dataClay session
init()

from CityNS.classes import DKB, Object, EventsSnapshot, ListOfObjects

def main():
    backend_id = get_backend_id_by_name("DS1")
    try:
        KBob = DKB.get_by_alias("DKB")
    except Exception:
        KBob = DKB()
        KBob.cloud_backend_id = backend_id
        list_objects = ListOfObjects()
        list_objects.make_persistent()
        KBob.list_objects = list_objects
        KBob.make_persistent(alias="DKB")

    snaps = []
    while True:
        print("Checking Events Snapshot received...")
        kb = KBob.kb
        for timestamp, eventSnap in list(kb.items()):
            if eventSnap.snap_alias not in snaps:
                print("Snapshot " + eventSnap.snap_alias + " received.")
                snaps.append(eventSnap.snap_alias)
                for objInSnapshot in eventSnap.objects_refs:
                    obj_id, class_id = objInSnapshot.split(":")
                    obj_id = uuid.UUID(obj_id)
                    class_id = uuid.UUID(class_id)
                    obj = getRuntime().get_object_by_id(obj_id, hint=backend_id, class_id=class_id)
                    print(obj)
                print("#################")
        time.sleep(5)

if __name__ == "__main__":
    main()
    finish()
