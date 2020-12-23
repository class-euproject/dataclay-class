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
    names_header = ["id_cam", "frame", "timestamp", "id_class", "lat", "lon", "geohash", "speed", "yaw", "id_obj"]
    data = pd.read_csv("../data/simulator.in", sep=" ", header=None, names=names_header)
    classes = ["person", "car", "truck", "bus", "motor", "bike", "rider", "traffic light", "traffic sign", "train"]

    for name, group in data.groupby(["frame"]):
        print(f"Creating snapshot for frame #{name}")
        eventsSnapshot = EventsSnapshot("events_" + str(name))
        for _, row in group.iterrows():
            if row["id_class"] not in [31, 32, 41]:
                obj_type = classes[row["id_class"]]
            else: # for smart cars and connected cars
                obj_type = str(row["id_class"])

            eventObject = KB.get_or_create(row["id_obj"], obj_type)
            eventObject.make_persistent()

            obj_id = str(eventObject.get_object_id()) + ":" + str(eventObject.get_class_extradata().class_id)
            if obj_id not in eventsSnapshot.objects_refs:
                eventsSnapshot.add_object_refs(obj_id)
                eventsSnapshot.add_object(eventObject)
                eventObject.retrieval_id = obj_id # TODO: add this in model and update get_objects() in DKB to return this instead of id_object

            event = Event(random.random(), eventObject, row["timestamp"], float(row["speed"]), float(row["yaw"]), row["lon"], row["lat"])
            eventObject.geohash = row["geohash"][0:7]
            eventsSnapshot.timestamp = row["timestamp"]

            eventObject.add_event(event)
        eventsSnapshot.make_persistent("events_" + str(name))
        KB.add_events_snapshot(eventsSnapshot)

if __name__ == "__main__":
    backend_id = get_backend_id_by_name("DS1")
    try:
        KB = DKB.get_by_alias("DKB")
        # KB.reset_dkb()
    except Exception:
        KB = DKB()
        KBob.cloud_backend_id = backend_id
        KB.make_persistent(alias="DKB")
    createDCObjects(KB)
    finish()
    exit(0)

