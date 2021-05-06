import threading
from collections import OrderedDict
from dataclay import DataClayObject, dclayMethod

"""
City Knowledge Base: collection of Events Snapshots
"""


class DKB(DataClayObject):
    """
    @ClassField kb dict<int, CityNS.classes.EventsSnapshot>
    @ClassField K int
    @ClassField frame_number int
    @ClassField connectedCars list<str>
    @ClassField objects dict<str, CityNS.classes.Object>
    @ClassField original_timestamp int
    @ClassField federated_objects set<str>
    @ClassField federate_compressed_info dict<int, CityNS.classes.FederationCompressedInfo>


    @dclayImportFrom geolib import geohash
    @dclayImportFrom collections import OrderedDict
    @dclayImport threading
    @dclayImport traceback
    """
    # kb should be a dict<int, CityNS.classes.EventsSnapshot> so snapshots are ordered by timestamp
    # original_timestamp is used in videos only, not in real-time streams

    @dclayMethod(k='int')
    def __init__(self, k=10):
        self.kb = dict()
        self.K = k
        self.frame_number = -1
        self.connectedCars = ["31", "32", "41"]  # TODO: change as below. Also replace definition from list<anything>
        self.objects = dict()
        self.global_lock = threading.Lock()
        self.original_timestamp = 0
        self.federated_objects = set()
        self.federate_compressed_info = dict()

    @dclayMethod(eventsSt='list<CityNS.classes.EventsSnapshot>')
    def aggregate_events(self, events_st):
        for event in events_st:
            self.add_events_snapshot(event)

    @dclayMethod()
    def reset_dkb(self):
        self.kb = dict()

    @dclayMethod(k='int')
    def set_k(self, k):
        self.K = k

    @dclayMethod(obj='CityNS.classes.Object')
    def add_object(self, obj):
        obj_id = obj.id_object
        if obj_id not in self.objects:
            self.objects[obj_id] = obj

    @dclayMethod(event_snp='CityNS.classes.EventsSnapshot')
    def add_events_snapshot(self, event_snp):
        self.kb[event_snp.timestamp] = event_snp
        self.frame_number += 1

    # returns a set of all relevant objects from K latest snapshots inside the specified geohashes, based on:
    # If geohashes set is None or empty, then return all relevant objects from latest K snapshots.
    # If with_neighbors == True, return also neighbors; if == False, then return only geohashes specified in set.
    # If with_tp == True, return only objects with trajectory prediction. If == False, then return only objects without
    #           trajectory prediction. If == None, then return all objects (with/without tp).
    # If connected == True, return connected car objects only. If == False then return all non-connected cars.
    # If == None, then return all objects (connected and non-connected).
    @dclayMethod(geohashes='set<str>', with_neighbors='bool', with_tp='bool', connected='bool',
                 events_length_max='dict<str,int>', events_length_min='dict<str,int>', num_objects='int',
                 return_="list<anything>")
    def get_objects(self, geohashes=None, with_neighbors=None, with_tp=None, connected=None, events_length_max=None,
                    events_length_min=None, num_objects=None):
        if events_length_max is None:
            events_length_max = {
                "person": 50,
                "car": 40,
                "truck": 40,
                "bus": 40,
                "motor": 40,
                "bike": 40,
                "rider": 50,
                "train": 40
            }
        if events_length_min is None:
            events_length_min = {
                "person": 20,
                "car": 10,
                "truck": 10,
                "bus": 10,
                "motor": 10,
                "bike": 10,
                "rider": 20,
                "train": 10
            }
        if geohashes is None:
            geohashes = []
        objs = []
        obj_refs = []
        # for i, (_, event_snap) in enumerate(reversed(OrderedDict(sorted(self.kb.items()))).items()): # get latest updates for objects
        for i, event_snap in enumerate(
                reversed(OrderedDict(sorted(self.kb.items())).values())):  # get latest updates for objects
            if i >= self.K or num_objects is not None and len(objs) == num_objects:
                break
            for event in event_snap.events:
                if num_objects is not None and len(objs) == num_objects:
                    break
                obj = event.detected_object
                retrieval_id = obj.retrieval_id  # retrieval_id instead of id_object
                if retrieval_id not in obj_refs:
                    obj_refs.append(retrieval_id)
                    geohash = obj.geohash
                    if geohashes is None or len(geohashes) == 0 or geohash in geohashes or with_neighbors is None \
                            or with_neighbors and geohash in [el for n in geohashes for el in geohash.neighbours(n)]:
                        trajectory_px = obj.trajectory_px
                        if with_tp is None or not with_tp and len(trajectory_px) == 0 \
                                or with_tp and len(trajectory_px) > 0:
                            obj_type = obj.type
                            if connected is None or not connected and obj_type not in self.connectedCars \
                                    or connected and obj_type in self.connectedCars:
                                # objs.append((id_object, trajectory_px, obj.trajectory_py, obj.trajectory_pt, geohash,
                                #     [list(ev.convert_to_dict().values()) for ev in list
                                #     (OrderedDict(sorted(obj.events_history.items())).values())]))
                                # objs.append((id_object, trajectory_px, obj.trajectory_py, obj.trajectory_pt, geohash,
                                #     obj.get_events_history()))
                                obj_type = obj.type
                                dequeues = obj.get_events_history(events_length_max[obj_type])
                                timestamp = dequeues[2][-1]  # timestamp dequeue and [-1] to get ts of last event
                                if len(dequeues[0]) >= events_length_min[obj_type]:
                                    if with_tp is None or not with_tp:  # and
                                        if dequeues[2][-1] > obj.timestamp_last_tp_comp:
                                            # or with_tp:  # condition of > is only active for the TP invocation
                                            objs.append((retrieval_id, trajectory_px, obj.trajectory_py,
                                                         obj.trajectory_pt,
                                                         geohash, dequeues, obj.id_object,
                                                         int(event_snap.snap_alias.split("_")[1]), obj.pixel_w,
                                                         obj.pixel_h))
                                    else:  # for CD
                                        objs.append((trajectory_px, obj.trajectory_py, obj.trajectory_pt, geohash,
                                                     obj.id_object, obj.type))

        return objs

    @dclayMethod(object_id='str', object_class='str', x='int', y='int', w='int', h='int',
                 return_='CityNS.classes.Object')
    def get_or_create(self, object_id, object_class, x, y, w, h):
        if not hasattr(self, "global_lock") or self.global_lock is not None:
            self.global_lock = threading.Lock()
        with self.global_lock:
            if object_id not in self.objects:
                obj = Object(object_id, object_class, x, y, w, h)
                self.objects[object_id] = obj
            else:
                obj = self.objects[object_id]

        obj.pixel_x = x
        obj.pixel_y = y
        obj.pixel_w = w
        obj.pixel_h = h
        return obj

    """ TODO: objects coming from {get,set}state are not linked to DKB
    @dclayMethod(return_="dict<str, anything>")
    def __getstate__(self):
        # if KB is serialized, objects that are not persistent will be automatically persisted
        return {"kb": self.kb, "K": self.K, "frame_number": self.frame_number,
                "connectedCars": self.connectedCars, "objects": self.objects,
                "original_timestamp": self.original_timestamp}

    @dclayMethod(state="dict<str, anything>")
    def __setstate__(self, state):
        self.kb = state["kb"]
        self.K = state["K"]
        self.frame_number = state["frame_number"]
        self.connectedCars = state["connectedCars"]
        self.objects = state["objects"]
        self.original_timestamp = state["original_timestamp"]
        self.global_lock = threading.Lock()
    """

    @dclayMethod(timestamp='int', unfederate_objects='bool')
    def remove_old_snapshots_and_objects(self, timestamp: int, unfederate_objects: bool):
        if not hasattr(self, "global_lock") or self.global_lock is not None:
            self.global_lock = threading.Lock()
        for snap_timestamp in list(self.kb.keys()):
            if snap_timestamp < timestamp:
                snapshot = self.kb[snap_timestamp]
                if snapshot.get_replica_locations() is not None and len(snapshot.get_replica_locations()) > 0:
                    print(
                        f"Deleting snapshot at timestamp {snap_timestamp} and snap_alias {snapshot.snap_alias}")
                    snapshot.delete(unfederate_objects)
                    del self.kb[snap_timestamp]
                elif snap_timestamp in self.federate_compressed_info:
                    print(
                        f"Deleting snapshot at timestamp {snap_timestamp} and snap_alias {snapshot.snap_alias}")
                    snapshot.delete(unfederate_objects)
                    del self.kb[snap_timestamp]
                    if unfederate_objects:
                        compressed_info = self.federate_compressed_info[snap_timestamp]
                        compressed_info.unfederate()
                    del self.federate_compressed_info[snap_timestamp]

        for object_id in list(self.objects.keys()):
            obj = self.objects[object_id]
            if obj.timestamp < timestamp:
                if obj.get_replica_locations() is not None and len(obj.get_replica_locations()) > 0:
                    with self.global_lock:
                        print(f"Deleting object id {object_id}")
                        obj.delete(unfederate_objects)
                        del self.objects[object_id]
                elif object_id in self.federated_objects:
                    with self.global_lock:
                        print(f"Deleting object id {object_id}")
                        obj.delete(False)
                        del self.objects[object_id]
                    self.federated_objects.remove(object_id)


    @dclayMethod(snapshot='CityNS.classes.EventsSnapshot', backend_id='anything')
    def federate_compressed_snapshot(self, snapshot, backend_id):
        compressed_info = FederationCompressedInfo(snapshot, self)
        compressed_info.federate_to_backend(backend_id)
        self.federate_compressed_info[snapshot.timestamp] = compressed_info



"""
Events Snapshots: List of the events detected in an snapshot. Each event
points to detected object.
"""
class EventsSnapshot(DataClayObject):
    """
    @ClassField events list<CityNS.classes.Event>
    @ClassField snap_alias str
    @ClassField timestamp int

    @dclayImportFrom geolib import geohash
    @dclayImport pygeohash as pgh
    @dclayImport requests
    """

    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.events = list()
        self.snap_alias = alias
        # self.session = requests.Session()
        self.timestamp = 0

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.events.append(event)

    @dclayMethod(events_detected='anything', kb='CityNS.classes.DKB')
    def add_events_from_trackers(self, events_detected, kb):
        import uuid
        classes = ["person", "car", "truck", "bus", "motor", "bike", "rider", "traffic light", "traffic sign", "train"]
        # snapshot_ts = int(datetime.now().timestamp() * 1000) # replaced for below
        # self.timestamp = events_detected[0]  # TODO: replace for real-streams
        if self.snap_alias.split("_")[1] == "0":  # frame 0
            self.timestamp = events_detected[0]
            kb.original_timestamp = self.timestamp
        else:
            self.timestamp = kb.original_timestamp + int(self.snap_alias.split("_")[1]) * 1000 // 24
        # self.timestamp = 1611592497727 + int(self.snap_alias.split("_")[1])*400 # to debug purpose only
        for index, ev in enumerate(events_detected[1]):
            id_cam = ev[0]
            tracker_id = ev[1]
            tracker_class = ev[2]
            vel_pred = ev[3]
            yaw_pred = ev[4]
            lat = ev[5]
            lon = ev[6]
            x = ev[7]
            y = ev[8]
            w = ev[9]
            h = ev[10]
            id_object = str(id_cam) + "_" + str(tracker_id)
            obj = kb.get_or_create(id_object, classes[tracker_class], x, y, w, h)
            event = Event(uuid.uuid4().int, obj, self.timestamp, vel_pred, yaw_pred, float(lon), float(lat))
            obj.add_event(event)
            obj.geohash = pgh.encode(lat, lon, precision=7)
            self.events.append(event)

        kb.add_events_snapshot(self)  # persists snapshot


    """
    @dclayMethod()
    def when_unfederated(self):
        # TODO
        #kb = DKB.get_by_alias("DKB")
        #kb.remove_events_snapshot(self)
    """

    @dclayMethod(return_='str')
    def __repr__(self):
        return f"Events Snapshot: \n\tevents: {self.events}, \n\tsnap_alias: " \
               f"{self.snap_alias}, timestamp: {self.timestamp}"

    @dclayMethod()
    def when_federated(self):
        try:
            kb = DKB.get_by_alias("DKB")
            kb.add_events_snapshot(self)
            for event in self.events:
                ### DEBUG ###
                obj = event.detected_object
                kb.add_object(obj)

                #### Associate federated event to detected object in cloud
                ## events are federated and pointing to object already present in cloud E -> O but is not O -> E
                obj.add_event(event)

                obj_id = obj.id_object

                id_cam = obj_id.split("_")[0]
                iteration = self.snap_alias.split("_")[1]
                ts = self.timestamp
                lat = event.latitude_pos
                lon = event.longitude_pos
                speed = event.speed
                yaw = event.yaw
                x = obj.pixel_x
                y = obj.pixel_y
                w = obj.pixel_w
                h = obj.pixel_h
                obj_class = obj.type
                geohash = obj.geohash

                if obj.frame_last_tp != -1:
                    print(f"""WF LOG FILE: {id_cam} {iteration} {ts} {obj_class} {lat} {lon} {geohash} {speed} {yaw}"""
                          f""" {obj_id} {x} {y} {w} {h} {obj.frame_last_tp} {next(reversed(sorted(obj.events_history)))}"""
                          f""" {obj.trajectory_px} {obj.trajectory_py} {obj.trajectory_pt}""")
                else:
                    print(f"""WF LOG FILE: {id_cam} {iteration} {ts} {obj_class} {lat} {lon} {geohash} {speed} {yaw}"""
                          f""" {obj_id} {x} {y} {w} {h} {obj.frame_last_tp} {-1} 0,0,0,0,0 0,0,0,0,0 0,0,0,0,0""")

            try:
                # trigger prediction via REST with alias specified for last EventsSnapshot
                apihost = 'https://192.168.7.42:31001'  # 'https://192.168.7.40:31001'
                auth_key = \
                       '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
                namespace = '_'
                blocking = 'false'
                result = 'false'
                # trigger = 'tp-trigger'
                # url = apihost + '/api/v1/namespaces/' + namespace + '/triggers/' + trigger
                tp_action = 'tpAction'
                cd_action = 'cdAction'
                url = apihost + '/api/v1/namespaces/' + namespace + '/actions/' + tp_action + \
                       '?blocking=false&result=false'  # asynchronous invocation
                url_cd = apihost + '/api/v1/namespaces/' + namespace + '/actions/' + cd_action + \
                          '?blocking=false&result=false'  # asynchronous invocation
                user_pass = auth_key.split(':')
                # alias = self.snap_alias
                alias = "DKB"
                session = requests.Session()
                session.post(url, params={'blocking': blocking, 'result': result},
                                                     json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]),
                                                     verify=False)  # keep alive the connection
                session.post(url_cd, params={'blocking': blocking, 'result': result},
                                          json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]),
                                          verify=False)  # keep alive the connection
            except Exception:
                traceback.print_exc()
                print("Error in REST API connection with Modena.")

        except Exception:
            traceback.print_exc()

    @dclayMethod(unfederate_objects='bool')
    def delete(self, unfederate_objects):
        if unfederate_objects:
            self.unfederate(recursive=False)  # implies an unfederate of the events and the objects of those events
        self.session_detach()
        # clean events
        self.events = list()


"""
Object: Vehicle or Pedestrian detected
        Objects are classified by type: Pedestrian, Bicycle, Car, Track, ...
        Only if it is not a pedestrian, the values speed and yaw are set.
"""


class Object(DataClayObject):
    """
    @ClassField id_object str
    @ClassField type str
    @ClassField events_history dict<int, CityNS.classes.Event>
    @ClassField timestamp int
    @ClassField trajectory_px list<float>
    @ClassField trajectory_py list<float>
    @ClassField trajectory_pt list<int>
    @ClassField geohash str
    @ClassField retrieval_id str
    @ClassField timestamp_last_tp_comp int
    @ClassField frame_last_tp int
    @ClassField pixel_x int
    @ClassField pixel_y int
    @ClassField pixel_w int
    @ClassField pixel_h int
    """

    @dclayMethod(id_object='str', obj_type='str', x='int', y='int', w='int', h='int')
    def __init__(self, id_object, obj_type, x, y, w, h):
        self.id_object = id_object
        self.type = obj_type
        self.events_history = dict()
        self.timestamp = 0
        self.trajectory_px = []
        self.trajectory_py = []
        self.trajectory_pt = []
        self.geohash = ""
        self.retrieval_id = ""  # added for retrieval purposes for IBM
        self.timestamp_last_tp_comp = -1
        self.frame_last_tp = -1
        self.pixel_x = x
        self.pixel_y = y
        self.pixel_w = w
        self.pixel_h = h

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.events_history[event.timestamp] = event
        if self.timestamp < event.timestamp:
            self.timestamp = event.timestamp

    # Updates the trajectory prediction
    @dclayMethod(tpx='list<float>', tpy='list<float>', tpt='list<anything>', timestamp_last_tp_comp='int',
                 frame_tp='int')
    def add_prediction(self, tpx, tpy, tpt, timestamp_last_tp_comp, frame_tp):
        import numpy
        self.trajectory_px = tpx
        self.trajectory_py = tpy
        self.trajectory_pt = tpt
        self.timestamp_last_tp_comp = timestamp_last_tp_comp
        obj_hist_ts = next(reversed(sorted(self.events_history)))
        self.frame_last_tp = frame_tp
        print(f"""TP LOG FILE: {frame_tp} {obj_hist_ts} {self.id_object} {self.trajectory_px} {self.trajectory_py} """
              f"""{self.trajectory_pt}""")

    # Returns the Object and its Events history (Deque format)
    @dclayMethod(events_length_max='int', return_="anything")
    def get_events_history(self, events_length_max):
        from collections import deque, OrderedDict
        # Events in following format(dqx, dqy, dqt)
        dqx = deque()
        dqy = deque()
        dqt = deque()
        i = 0
        for _, event in reversed(OrderedDict(sorted(self.events_history.items())).items()):
            if i == events_length_max:
                break
            dqx.insert(0, event.latitude_pos)
            dqy.insert(0, event.longitude_pos)
            dqt.insert(0, event.timestamp)  # dequeues should be ordered with increasingly timestamps
            i += 1
        return dqx, dqy, dqt

    @dclayMethod(return_='str')
    def __repr__(self):
        num_events = len(self.events_history)
        return f"Object {self.id_object} of type {self.type} with {num_events} events"  # Events {self.events_history}"


    @dclayMethod(return_='dict<str,anything>')
    def get_compressed_data(self):
        return {"id_object": self.id_object, "type": self.type, "trajectory_px": self.trajectory_px,
                "trajectory_py": self.trajectory_py, "trajectory_pt": self.trajectory_pt, "geohash": self.geohash,
                "x": self.pixel_x, "y": self.pixel_y, "w": self.pixel_w, "h": self.pixel_h, "timestamp": self.timestamp}

    @dclayMethod(unfederated_object='bool')
    def delete(self, unfederate_object):
        for event in list(self.events_history.values()):
            event.delete()
        self.events_history.clear()
        if unfederate_object:
            self.unfederate()
        self.session_detach()


"""
Event: Instantiation of an Object for a given position and time.
"""


class Event(DataClayObject):
    """
    @ClassField id_event int
    @ClassField detected_object CityNS.classes.Object
    @ClassField timestamp int
    @ClassField speed anything
    @ClassField yaw anything
    @ClassField longitude_pos anything
    @ClassField latitude_pos anything
    """

    @dclayMethod(id_event='int', detected_object='CityNS.classes.Object', timestamp='int', speed='anything',
                 yaw='anything', longitude_pos='anything', latitude_pos='anything')
    def __init__(self, id_event, detected_object, timestamp, speed, yaw, longitude_pos, latitude_pos):
        self.id_event = id_event
        self.detected_object = detected_object
        self.timestamp = timestamp
        self.speed = speed
        self.yaw = yaw
        self.longitude_pos = longitude_pos
        self.latitude_pos = latitude_pos

    @dclayMethod(return_='str')
    def __repr__(self):
        return "(long=%s,lat=%s,time=%s,speed=%s,yaw=%s,id=%s,id_object=%s)" % (
        str(self.longitude_pos), str(self.latitude_pos),
        str(self.timestamp), str(self.speed), str(self.yaw),
        str(self.id_event), str(self.detected_object.id_object))

    @dclayMethod(return_='dict<str, anything>')
    def get_compressed_data(self):
        return {"id_event": self.id_event, "detected_object": self.detected_object.id_object,
                "timestamp": self.timestamp, "speed": self.speed, "yaw": self.yaw, "latitude_pos": self.latitude_pos,
                "longitude_pos": self.longitude_pos}

    @dclayMethod()
    def delete(self):
        # self.detected_object = None
        self.session_detach()



class FederationCompressedInfo(DataClayObject):
    """
    @ClassField events list<anything>
    @ClassField objects dict<str, anything>
    @ClassField snap_alias str
    @ClassField timestamp int

    @dclayImport traceback
    @dclayImport uuid
    @dclayImportFrom dataclay import getRuntime
    """

    @dclayMethod(snapshot='CityNS.classes.EventsSnapshot', dkb='CityNS.classes.DKB')
    def __init__(self, snapshot, dkb):
        self.events = []
        self.snap_alias = snapshot.snap_alias
        self.timestamp = snapshot.timestamp
        self.objects = dict()
        for event in snapshot.events:
            self.events.append(event.get_compressed_data())
            obj = event.detected_object
            obj_id = obj.id_object
            if obj_id not in self.objects and obj_id not in list(dkb.federated_objects):
                self.objects[obj_id] = obj.get_compressed_data()
                dkb.federated_objects.add(obj_id)


    @dclayMethod()
    def when_federated(self):
        try:
            kb = DKB.get_by_alias("DKB")
            snapshot = EventsSnapshot(self.snap_alias)
            snapshot.timestamp = self.timestamp
            for compressed_obj_id, compressed_object in self.objects.items():
                obj_class = compressed_object["type"]
                geohash = compressed_object["geohash"]
                x = compressed_object["x"]
                y = compressed_object["y"]
                w = compressed_object["w"]
                h = compressed_object["h"]
                obj = kb.get_or_create(compressed_obj_id, obj_class, x, y, w, h)
                object_id = obj.get_object_id()
                class_id = obj.get_class_extradata().class_id
                obj.geohash = geohash
                obj.retrieval_id = str(object_id) + ":" + str(class_id)

            for compressed_event in self.events:
                detected_object_id = compressed_event["detected_object"]
                detected_object = kb.objects[detected_object_id]
                event = Event(compressed_event["id_event"], detected_object, compressed_event["timestamp"],
                              compressed_event["speed"], compressed_event["yaw"], compressed_event["longitude_pos"],
                              compressed_event["latitude_pos"])
                detected_object.add_event(event)
                snapshot.add_event(event)


                ### FOR LOGGING ###
                id_cam = detected_object_id.split("_")[0]
                iteration = self.snap_alias.split("_")[1]
                ts = snapshot.timestamp
                lat = compressed_event["latitude_pos"]
                lon = compressed_event["longitude_pos"]
                speed = compressed_event["speed"]
                yaw = compressed_event["yaw"]
                if detected_object.frame_last_tp != -1:
                    print(
                        f"""WF LOG FILE: {id_cam} {iteration} {ts} {detected_object.type} {lat} {lon} """
                        f"""{detected_object.geohash} {speed} {yaw} {detected_object_id} {detected_object.pixel_x} """
                        f"""{detected_object.pixel_y} {detected_object.pixel_w} {detected_object.pixel_h} """
                        f"""{detected_object.frame_last_tp} {next(reversed(sorted(detected_object.events_history)))} """
                        f"""{detected_object.trajectory_px} {detected_object.trajectory_py} """
                        f"""{detected_object.trajectory_pt}""")
                else:
                    print(
                        f"""WF LOG FILE: {id_cam} {iteration} {ts} {detected_object.type} {lat} {lon} """
                        f"""{detected_object.geohash} {speed} {yaw} {detected_object_id} {detected_object.pixel_x} """
                        f"""{detected_object.pixel_y} {detected_object.pixel_w} {detected_object.pixel_h} """
                        f"""{detected_object.frame_last_tp} {-1} 0,0,0,0,0 0,0,0,0,0 0,0,0,0,0""")

                kb.add_events_snapshot(snapshot)
                try:
                    # trigger prediction via REST with alias specified for last EventsSnapshot
                    apihost = 'https://192.168.7.42:31001'  # 'https://192.168.7.40:31001'
                    auth_key = \
                        '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
                    namespace = '_'
                    blocking = 'false'
                    result = 'false'
                    # trigger = 'tp-trigger'
                    # url = apihost + '/api/v1/namespaces/' + namespace + '/triggers/' + trigger
                    tp_action = 'tpAction'
                    cd_action = 'cdAction'
                    url = apihost + '/api/v1/namespaces/' + namespace + '/actions/' + tp_action + \
                          '?blocking=false&result=false'  # asynchronous invocation
                    url_cd = apihost + '/api/v1/namespaces/' + namespace + '/actions/' + cd_action + \
                             '?blocking=false&result=false'  # asynchronous invocation
                    user_pass = auth_key.split(':')
                    # alias = snap_alias
                    alias = "DKB"
                    snapshot.session.post(url, params={'blocking': blocking, 'result': result},
                                          json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]),
                                          verify=False)  # keep alive the connection
                    snapshot.session.post(url_cd, params={'blocking': blocking, 'result': result},
                                          json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]),
                                          verify=False)  # keep alive the connection
                except Exception:
                    traceback.print_exc()
                    print("Error in REST API connection in when_federated.")
        except Exception:
            traceback.print_exc()