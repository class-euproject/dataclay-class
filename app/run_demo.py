import random
from dataclay.api import init, finish
from dataclay.api import get_backend_id_by_name
from dataclay import getRuntime
import pandas as pd
import uuid

# Init dataClay session
init()

from CityNS.classes import Event, Object, EventsSnapshot, DKB


def createDCObjects(KB):
#    2407 0 1614864273619 car 35.03094917780228 -78.93057766400014 dnpz7ch 0.0 0.0 2407_0 316 72 31 18 -1 -1 0,0,0,0,0 0,0,0,0,0 0,0,0,0,0
    names_header = ["id_cam", "frame", "timestamp", "id_class", "lat", "lon", "geohash", "speed", "yaw", "id_obj", "x", "y", "w", "h", "frame_tp", "timestamp_last_tp", "TPlat", "TPlon", "TPts"]
    data = pd.read_csv("../data/simulator.in", sep=" ", header=None, names=names_header)
    classes = ["person", "car", "truck", "bus", "motor", "bike", "rider", "traffic light", "traffic sign", "train"]

    for name, group in data.groupby(["frame"]):
        print(f"Creating snapshot for frame #{name}")
        eventsSnapshot = EventsSnapshot("events_" + str(name))
#        import pdb;pdb.set_trace()
        for _, row in group.iterrows():
#            if row["id_class"] not in [31, 32, 41]:
#                obj_type = classes[row["id_class"]]
#            else: # for smart cars and connected cars
#                obj_type = str(row["id_class"])
            obj_type = row["id_class"]

            eventObject = KB.get_or_create(row["id_obj"], obj_type, row['x'], row['y'], row['w'], row['h'])
            eventObject.make_persistent()
            obj_id = str(eventObject.get_object_id()) + ":" + str(eventObject.get_class_extradata().class_id)
            eventObject.retrieval_id = obj_id  # TODO: add this in model and update get_objects() in DKB to return this instead of id_object

            event = Event(uuid.uuid4().int, eventObject, row["timestamp"], float(row["speed"]), float(row["yaw"]), float(row["lon"]), float(row["lat"]))
            eventObject.geohash = row["geohash"][0:7]
            eventsSnapshot.timestamp = row["timestamp"]
            eventsSnapshot.add_event(event)
            eventObject.add_event(event)
#        import pdb;pdb.set_trace()
        eventsSnapshot.make_persistent("events_" + str(name))
        KB.add_events_snapshot(eventsSnapshot)

if __name__ == "__main__":
    try:
#        import pdb;pdb.set_trace()
        KB = DKB.get_by_alias("DKB")
        # KB.reset_dkb()
    except Exception:
        KB = DKB()
#        KBob.cloud_backend_id = backend_id
        KB.make_persistent(alias="DKB")
#    import pdb;pdb.set_trace()
    createDCObjects(KB)
    finish()
    exit(0)

