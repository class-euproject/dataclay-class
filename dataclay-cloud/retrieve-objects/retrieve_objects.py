from dataclay.api import init, finish
import time
import datetime

# Init dataClay session
init()

from CityNS.classes import DKB, Object, EventsSnapshot

def main():
    try:
        KBob = DKB.get_by_alias("DKB")
    except Exception:
        KBob = DKB()
        KBob.make_persistent(alias="DKB")

    minutes_to_sleep = 15
    while True:
        print("Checking Events Snapshot received...")
        kb = KBob.kb
        last_timestamp = 0
        if len(kb) > 0:
            last_timestamp = next(reversed(sorted(list(kb.keys()))))
        print(f"Number of snapshots {len(list(kb.keys()))} and number of objects {len(list(KBob.objects.keys()))} and "
              f"last timestamp {last_timestamp}")
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
        time.sleep(minutes_to_sleep * 60)
        if len(kb) > 0:
            KBob.remove_old_snapshots_and_objects(last_timestamp, False)
            # TODO: cannot remove based on .now()-10 minutes as the timestamp is set in the edge timing. Sleep of 15
            #  minutes solves it
            # timestamp_to_remove = int(
            #     (datetime.datetime.now() - datetime.timedelta(minutes=minutes_to_sleep)).timestamp() * 1000)
            # print(f"Removing objects older than: {timestamp_to_remove}")
            # KBob.remove_old_snapshots_and_objects(timestamp_to_remove, False)


if __name__ == "__main__":
    main()
    finish()
