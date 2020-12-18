import random
from dataclay.api import init, finish
import pandas as pd

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
            try:
                eventObject = Object.get_by_alias(row["id_obj"])
            except:
                eventObject = Object(row["id_obj"], obj_type)
                eventObject.make_persistent(row["id_obj"])
            obj_id = str(row["id_obj"]) + ":" + str(eventObject.get_class_extradata().class_id)
            if obj_id not in eventsSnapshot.objects_refs:
                eventsSnapshot.add_object_refs(obj_id)
                eventsSnapshot.add_object(eventObject)
            event = Event(random.random(), eventObject, row["timestamp"], float(row["speed"]), float(row["yaw"]), row["lon"], row["lat"])
            eventObject.geohash = row["geohash"][0:7]
            eventsSnapshot.timestamp = row["timestamp"]

            eventObject.add_event(event)
        eventsSnapshot.make_persistent("events_" + str(name))
        KB.add_events_snapshot(eventsSnapshot)


if __name__ == "__main__":
    try:
        KB = DKB.get_by_alias("DKB")
        KB.reset_dkb()
    except Exception:
        KB = DKB()
        KB.make_persistent(alias="DKB")
    createDCObjects(KB)
    finish()
    exit(0)

