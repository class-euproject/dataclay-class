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
    @ClassField cloud_backend_id anything
    @ClassField list_objects CityNS.classes.ListOfObjects
    @ClassField ORIGINAL_TIMESTAMP int

    @dclayImportFrom geolib import geohash
    @dclayImportFrom collections import OrderedDict
    """

    @dclayMethod(k='int')
    def __init__(self, k=10):
        self.kb = dict()
        self.K = k
        self.frame_number = -1
        self.connectedCars = ["31", "32", "41"] # TODO: change as below. Also replace definition from list<anything>
        # dict<anything>: self.connectedCars = {"31": 'X.X.X.X', "32": 'Y.Y.Y.Y'} # TODO: as dictionaries
        self.cloud_backend_id = None
        # self.list_objects = ListOfObjects()
        self.ORIGINAL_TIMESTAMP = 0

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

    @dclayMethod(event_snp='CityNS.classes.EventsSnapshot')
    def add_events_snapshot(self, event_snp): 
        self.kb[event_snp.timestamp] = event_snp
        self.frame_number += 1

    @dclayMethod(return_="list<anything>")
    def get_objects_from_dkb(self):
        objs = []
        obj_refs = []
        for event_snap in reversed(OrderedDict(sorted(self.kb.items())).values()): # get latest updates for objects
            for obj_ref in event_snap.objects_refs:  # TODO: update this with objects instead of objects_refs
                if obj_ref not in obj_refs:
                    obj_refs.append(obj_ref)
                    obj = Object.get_by_alias(obj_ref)
                    objs.append((obj.id_object, obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt))
        return objs

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
        for i, event_snap in enumerate(reversed(OrderedDict(sorted(self.kb.items())).values())): # get latest updates for objects
            if i > self.K or num_objects is not None and len(objs) == num_objects:
                break
            for obj in event_snap.objects.values():
                if num_objects is not None and len(objs) == num_objects:
                    break
                retrieval_id = obj.retrieval_id
                if retrieval_id not in obj_refs:
                    obj_refs.append(retrieval_id)
                    geohash = obj.geohash
                    if geohashes is None or len(geohashes) == 0 or geohash in geohashes or with_neighbors is None \
                            or with_neighbors and geohash in [el for n in geohashes for el in geohash.neighbours(n)]:
                        trajectory_px = obj.trajectory_px
                        if with_tp is None or not with_tp and len(trajectory_px) == 0 \
                                or with_tp and len(trajectory_px) > 0:
                            obj_type = obj.type
                            if connected is None or not connected and obj_type not in self.connectedCars\
                                    or connected and obj_type in self.connectedCars:
                                # objs.append((id_object, trajectory_px, obj.trajectory_py, obj.trajectory_pt, geohash,
                                #     [list(ev.convert_to_dict().values()) for ev in list
                                #     (OrderedDict(sorted(obj.events_history.items())).values())]))
                                obj_type = obj.type
                                dequeues = obj.get_events_history(events_length_max[obj_type])
                                timestamp = dequeues[2][-1]  # timestamp dequeue and [-1] to get ts of last event
                                if len(dequeues[0]) >= events_length_min[obj_type]:
                                    if with_tp is None or not with_tp: #and
                                        if dequeues[2][-1] > obj.timestamp_last_tp_comp:
                                            #or with_tp:  # condition of > is only active for the TP invocation
                                            objs.append((retrieval_id, trajectory_px, obj.trajectory_py,
                                                obj.trajectory_pt,
                                                geohash, dequeues, obj.id_object,
                                                int(event_snap.snap_alias.split("_")[1]), obj.pixel_w,
                                                obj.pixel_h))
                                    else:  # for CD
                                        objs.append((trajectory_px, obj.trajectory_py, obj.trajectory_pt, geohash,
                                            obj.id_object, obj.type))
        return objs


    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def remove_events_snapshot(self, event_snp): 
        pass

    @dclayMethod(object_id='str', object_class='str', x='int', y='int', w='int', h='int',
                 return_='CityNS.classes.Object')
    def get_or_create(self, object_id, object_class, x, y, w, h):
        return self.list_objects.get_or_create(object_id, object_class, x, y, w, h)


class ListOfObjects(DataClayObject):
    """
    @ClassField objects dict<str, CityNS.classes.Object>
    @ClassField federated_objects list<str>

    @dclayImport threading
    @dclayImport traceback
    """

    @dclayMethod()
    def __init__(self):
        self.objects = dict()
        self.federated_objects = []
        self.global_lock = threading.Lock()

    @dclayMethod(object_id='str', object_class='str', x='int', y='int', w='int', h='int',
                 return_='CityNS.classes.Object')
    def get_or_create(self, object_id, object_class, x, y, w, h):
        with self.global_lock:
            if object_id not in self.objects:
                obj = Object(object_id, object_class, x, y, w, h)
                self.objects[object_id] = obj
            else:
                self.objects[object_id].pixel_x = x
                self.objects[object_id].pixel_y = y
                self.objects[object_id].pixel_w = w
                self.objects[object_id].pixel_h = h
            return self.objects[object_id]

    @dclayMethod(return_="dict<str, anything>")
    def __getstate__(self):
        return {"objects": self.objects, 
                "federated_objects": self.federated_objects} 

    @dclayMethod(state="dict<str, anything>")
    def __setstate__(self, state):
        self.objects = state["objects"]
        self.federated_objects = state["federated_objects"]
        self.global_lock = threading.Lock()


class FederationInfo(DataClayObject):
    """
    @ClassField objects_refs_per_snapshot list<anything>
    @ClassField objects_per_snapshot list<anything>
    @ClassField snap_aliases_per_snapshot list<str>
    @ClassField timestamps_per_snapshot list<int>

    @dclayImport traceback
    @dclayImport uuid
    @dlcayImportFrom dataclay import getRuntime
    """

    @dclayMethod(snapshots='list<CityNS.classes.EventsSnapshot>')
    def __init__(self, snapshots):
        self.objects_refs_per_snapshot = []
        self.objects_per_snapshot = []
        self.snap_aliases_per_snapshot = []
        self.timestamps_per_snapshot = []
        for snapshot in snapshots:
            snp_objects = dict()
            timestamp = snapshot.timestamp
            for obj_id, obj in snapshot.objects.items():
                snp_objects[str(obj_id)] = obj.convert_to_dict(timestamp)

            self.objects_per_snapshot.append(snp_objects)
            self.objects_refs_per_snapshot.append(snapshot.objects_refs)
            self.snap_aliases_per_snapshot.append(snapshot.snap_alias)
            self.timestamps_per_snapshot.append(timestamp)

    @dclayMethod() 
    def when_federated(self):
        from dataclay import getRuntime
        try:
            kb = DKB.get_by_alias("DKB")
            backend_id = kb.cloud_backend_id
            for idx, snap_alias in enumerate(self.snap_aliases_per_snapshot):
                snapshot_objects_refs = []
                snapshot_objects = self.objects_per_snapshot[idx]
                snapshot_timestamp = self.timestamps_per_snapshot[idx]
                snapshot = EventsSnapshot(snap_alias)
                snapshot.timestamp = snapshot_timestamp

                for obj_id, obj_dict in snapshot_objects.items():
                    obj_class = obj_dict["type"]
                    event_dict = obj_dict["event"]
                    geohash = obj_dict["geohash"]
                    x = obj_dict["x"]
                    y = obj_dict["y"]
                    w = obj_dict["w"]
                    h = obj_dict["h"]

                    ## TODO: TO BE USED IN THE FUTURE OR NOT NEEDED AS IT IS NOT INFO FEDERATED FROM EDGE ##
                    trajectory_px = obj_dict["trajectory_px"]
                    trajectory_py = obj_dict["trajectory_py"]
                    trajectory_pt = obj_dict["trajectory_pt"]
                    ## ##
                    
                    obj = kb.get_or_create(obj_id, obj_class, x, y, w, h)
                    object_id = obj.get_object_id()
                    class_id = obj.get_class_extradata().class_id
                    snapshot_objects_refs.append(str(object_id) + ":" + str(class_id))
                    obj.geohash = geohash
                    obj.retrieval_id = str(object_id) + ":" + str(class_id)
                    event = Event(event_dict["id_event"], obj, event_dict["timestamp"], 
                                  event_dict["speed"], event_dict["yaw"], event_dict["longitude_pos"],
                                  event_dict["latitude_pos"])
                    obj.add_event(event)
                    snapshot.objects[obj.id_object] = obj
                    ### FOR LOGGING ###
                    id_cam = obj_id.split("_")[0]
                    iteration = snap_alias.split("_")[1]
                    ts = snapshot.timestamp
                    lat = event_dict["latitude_pos"]
                    lon = event_dict["longitude_pos"]
                    speed = event_dict["speed"]
                    yaw = event_dict["yaw"]
                    if obj.frame_last_tp != -1:
                        print(
                            f'''WF LOG FILE: {id_cam} {iteration} {ts} {obj_class} {lat} {lon} {geohash} {speed} {yaw} \
{obj_id} {x} {y} {w} {h} {obj.frame_last_tp} {next(reversed(sorted(obj.events_history)))} \
{obj.trajectory_px} {obj.trajectory_py} {obj.trajectory_pt}''')
                    else:
                        print(
                            f'''WF LOG FILE: {id_cam} {iteration} {ts} {obj_class} {lat} {lon} {geohash} {speed} {yaw} \
{obj_id} {x} {y} {w} {h} {obj.frame_last_tp} {-1} 0,0,0,0,0 0,0,0,0,0 0,0,0,0,0''')

                snapshot.objects_refs = snapshot_objects_refs
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


"""
Events Snapshots: List of the objects detected in an snapshot. Each object
contains a list of events (last event for current snapshot and events history).
"""
class EventsSnapshot(DataClayObject):
    """
    @ClassField objects_refs list<str>
    @ClassField objects dict<str, CityNS.classes.Object>
    @ClassField snap_alias str
    @ClassField timestamp int

    @dclayImportFrom geolib import geohash
    @dclayImport pygeohash as pgh
    @dclayImport requests
    """

    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.objects_refs = []
        self.objects = dict()
        self.snap_alias = alias
        self.session = requests.Session()
        self.timestamp = 0

    @dclayMethod(object_alias="str")
    def add_object_refs(self, object_alias):
        self.objects_refs.append(object_alias)

    ## FOR THE SIMULATOR ONLY ##
    @dclayMethod(obj="CityNS.classes.Object")
    def add_object(self, obj):
        self.objects[obj.id_object] = obj

    # Returns the list of Object refs
    @dclayMethod(return_='list<str>')
    def get_objects_refs(self):
        return self.objects_refs

    # Returns the list of Object ids
    @dclayMethod(return_='list<str>')
    def get_objects_ids(self):
        return self.objects.keys()

    @dclayMethod(events_detected='anything', kb='CityNS.classes.DKB')
    def add_events_from_trackers(self, events_detected, kb):
        from datetime import datetime
        import uuid
        classes = ["person", "car", "truck", "bus", "motor", "bike", "rider", "traffic light", "traffic sign", "train"]
        # snapshot_ts = int(datetime.now().timestamp() * 1000) # replaced for below
        # self.timestamp = events_detected[0]
        if self.snap_alias.split("_")[1] == "0":  # frame 0
            self.timestamp = events_detected[0]
            kb.ORIGINAL_TIMESTAMP = self.timestamp
        else:
            self.timestamp = kb.ORIGINAL_TIMESTAMP + int(self.snap_alias.split("_")[1]) * 1000 // 24
        # self.timestamp = 1611592497727 + int(self.snap_alias.split("_")[1])*400 # TODO: to debug purpose only
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
            object_alias = str(id_cam) + "_" + str(tracker_id)
            obj = kb.get_or_create(object_alias, classes[tracker_class], x, y, w, h)
            event = Event(uuid.uuid4().int, obj, self.timestamp, vel_pred, yaw_pred, float(lon), float(lat))
            obj.add_event(event)
            obj.geohash = pgh.encode(lat, lon, precision=7)
            if obj.id_object not in self.objects:
                self.objects[obj.id_object] = obj
    
    @dclayMethod()
    def when_unfederated(self):
        kb = DKB.get_by_alias("DKB")
        kb.remove_events_snapshot(self)

    @dclayMethod()
    def delete(self):
        self.objects_refs = list()


    @dclayMethod(return_="dict<str, anything>")
    def __getstate__(self):
        return {"objects_refs": self.objects_refs,
                "objects": self.objects, 
                "snap_alias": self.snap_alias,
                "timestamp": self.timestamp}

    @dclayMethod(state="dict<str, anything>")
    def __setstate__(self, state):
        self.objects_refs = state["objects_refs"]
        self.objects = state["objects"]
        self.snap_alias = state["snap_alias"]
        self.timestamp = state["timestamp"]
        self.session = requests.Session()

    @dclayMethod(return_='str')
    def __repr__(self):
        return f"Events Snapshot: \n\tobjects: {self.objects}, \n\tobjects_refs: {self.objects_refs}, \n\tsnap_alias: " \
               f"{self.snap_alias}, timestamp: {self.timestamp}"


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

    @dclayMethod(snap_timestamp='int', return_="dict<str, anything>")
    def convert_to_dict(self, snap_timestamp):
        event = self.events_history[snap_timestamp].convert_to_dict()
        return {"id_object": self.id_object, "type": self.type, "event": event, 
                "trajectory_px": self.trajectory_px, "trajectory_py": self.trajectory_py, 
                "trajectory_pt": self.trajectory_pt, "geohash": self.geohash,
                "x": self.pixel_x, "y": self.pixel_y, "w": self.pixel_w, "h": self.pixel_h}

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        # self.events_history.append(event)
        self.events_history[event.timestamp] = event

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
        print(f'''TP LOG FILE: {frame_tp} {obj_hist_ts} {self.id_object} {self.trajectory_px} {self.trajectory_py} \
{self.trajectory_pt}''')
    
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
        return f"Object {self.id_object} of type {self.type} with {num_events} Events {self.events_history}" # str(self.events_history.values())


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

    @dclayMethod(return_='dict<str, anything>')
    def convert_to_dict(self):
        return {"id_event": self.id_event, "detected_object": self.detected_object.id_object,
                "timestamp": self.timestamp,
                "speed": self.speed, "yaw": self.yaw, "latitude_pos": self.latitude_pos,
                "longitude_pos": self.longitude_pos}
        
    @dclayMethod(return_='str')
    def __repr__(self):
        return "(long=%s,lat=%s,time=%s,speed=%s,yaw=%s,id=%s)" % (str(self.longitude_pos), str(self.latitude_pos),
                                                                   str(self.timestamp), str(self.speed), str(self.yaw),
                                                                   str(self.id_event))

