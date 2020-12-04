from dataclay import DataClayObject, dclayMethod

"""
City Knowledge Base: collection of Events Snapshots
"""
class DKB(DataClayObject):
    """
    @ClassField kb list<CityNS.classes.EventsSnapshot>
    @ClassField K int
    @ClassField connectedCars list<str>
    @ClassField smartCars list<anything>

    @dclayImportFrom geolib import geohash
    """
    # kb should be a dict<timestamp, CityNS.classes.EventsSnapshot> so snapshots are ordered

    @dclayMethod(k='int')
    def __init__(self, k=10):
        self.kb = []
        self.K = k
        self.connectedCars = ["31", "32", "41"] # TODO: change as below. Also replace definition from list<anything>
        # dict<anything>: self.connectedCars = {"31": 'X.X.X.X', "32": 'Y.Y.Y.Y'} # TODO: as dictionaries
        self.smartCars = [] # TODO: change as above

    @dclayMethod(eventsSt='list<CityNS.classes.EventsSnapshot>')
    def aggregate_events(self, events_st):
        for event in events_st:
            self.add_events_snapshot(event)

    @dclayMethod()
    def reset_dkb(self):
        self.kb = []

    @dclayMethod(k='int')
    def set_k(self, k):
        self.K = k

    @dclayMethod(event_snp='CityNS.classes.EventsSnapshot')
    def add_events_snapshot(self, event_snp): 
        self.kb.append(event_snp)

    @dclayMethod(return_="list<anything>")
    def get_objects_from_dkb(self):
        objs = []
        obj_refs = []
        for event_snap in reversed(self.kb): # get latest updates for objects
            for obj_ref in event_snap.objects_refs:
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
    @dclayMethod(geohashes='set<str>', with_neighbors='bool', with_tp='bool', connected='bool', return_="set<Object>")
    def get_objects(self, geohashes=[], with_neighbors=None, with_tp=None, connected=None):
        objs = set()
        obj_refs = []
        for i, event_snap in enumerate(reversed(self.kb)): # get latest updates for objects
            if i > self.K:
                break
            for obj_ref in event_snap.objects_refs:
                if obj_ref not in obj_refs:
                    obj_refs.append(obj_ref)
                    obj = Object.get_by_alias(obj_ref)
                    if geohashes is None or len(geohashes) == 0 or obj.geohash in geohashes or with_neighbors is None \
                            or with_neighbors and obj.geohash in [el for n in geohashes for el in geohash.neighbours(n)]:
                        if with_tp is None or not with_tp and len(obj.trajectory_px) == 0 \
                                or with_tp and len(obj.trajectory_px) > 0:
                            if connected is None or not connected and obj.type not in self.connectedCars+self.smartCars\
                                    or connected and obj.type in self.connectedCars+self.smartCars:
                                objs.add(obj)

        return objs

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def remove_events_snapshot(self, event_snp): 
        pass


class ListOfObjects(DataClayObject):
    """
    @ClassField objects dict<str, CityNS.classes.Object>

    @dclayImport threading
    """

    @dclayMethod()
    def __init__(self):
        self.objects = dict()

    @dclayMethod()
    def initialize_locks(self):
        self.locks = dict()
        # self.lock = threading.Lock()

    @dclayMethod(object_id='str', object_class='str')
    def get_or_create(self, object_id, object_class):
        if object_id not in self.locks:
            self.locks[object_id] = threading.Lock()
        with self.locks[object_id]: 
            if object_id not in self.objects:
                obj = Object(object_id, object_class)
                self.objects[object_id] = obj
            return self.objects[object_id]

class ListOfEvents(DataClayObject):
    """
    @ClassField events list<CityNS.classes.Event>
    """

    @dclayMethod(detected_events="list<CityNS.classes.Event>")
    def __init__(self, detected_events):
        self.events = detected_events


"""
Events Snapshots: List of the objects detected in an snapshot. Each object
contains a list of events (last event for current snapshot and events history).
"""
class EventsSnapshot(DataClayObject):
    """
    @ClassField objects_refs list<str>
    @ClassField objects dict<str, CityNS.classes.Object>
    @ClassField snap_alias str

    @dclayImportFrom geolib import geohash
    @dclayImport pygeohash as pgh
    """
    # @ClassField timestamp anything # TODO: to be added based on value from Deduplicator (oldest timestamp from tkDNN sent to deduplicator) 

    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.objects_refs = []
        self.objects = dict()
        self.snap_alias = alias

    @dclayMethod(object_alias="str")
    def add_object_refs(self, object_alias):
        self.objects_refs.append(object_alias)

    # Returns the list of Object refs
    @dclayMethod(return_='list<str>')
    def get_objects_refs(self):
        return self.objects_refs

    @dclayMethod(events_detected='anything', list_objects='CityNS.classes.ListOfObjects')
    def add_events_from_trackers(self, events_detected, list_objects):
        from datetime import datetime
        import uuid
        classes = ["person", "car", "truck", "bus", "motor", "bike", "rider", "traffic light", "traffic sign", "train"]
        # snapshot_ts = int(datetime.now().timestamp() * 1000) # replaced for below
        snapshot_ts = events_detected[0]
        for index, ev in enumerate(events_detected[1]):
            id_cam = ev[0]
            tracker_id = ev[1]
            tracker_class = ev[2]
            vel_pred = ev[3]
            yaw_pred = ev[4]
            lat = ev[5]
            lon = ev[6]
            # object_alias = "obj_" + str(index) # replaced by below
            object_alias = "obj_" + str(id_cam) + "_" + str(tracker_id) 
            obj = list_objects.get_or_create(object_alias, classes[tracker_class])
            event = Event(uuid.uuid4().int, obj, snapshot_ts, vel_pred, yaw_pred, float(lon), float(lat))
            self.add_object_refs(object_alias)
            obj.add_event(event)
            obj.geohash = pgh.encode(lat, lon, precision=7)
            if obj.id_object not in self.objects:
                self.objects[obj.id_object] = obj

    """
    Method that stores (make_persistent) all events in one single call to avoid extra visits to dataClay
    """
    @dclayMethod(detected_events="CityNS.classes.ListOfEvents")
    def add_events(self, detected_events):
        for event in detected_events.events:
            obj = event.detected_object
            obj.add_event(event)
            obj.geohash = pgh.encode(event.latitude_pos, event.longitude_pos, precision=7)
            if obj.id_object not in self.objects:
                self.objects[obj.id_object] = obj

    @dclayMethod() 
    def when_federated(self):
        import requests
        print("Calling when federated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.add_events_snapshot(self)
        # trigger prediction via REST with alias specified for last EventsSnapshot
        apihost = 'https://192.168.7.40:31001'
        auth_key = \
            '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
        namespace = '_'
        blocking = 'true'
        result = 'true'
        trigger = 'tp-trigger'
        url = apihost + '/api/v1/namespaces/' + namespace + '/triggers/' + trigger
        user_pass = auth_key.split(':')
        alias = self.snap_alias
        requests.post(url, params={'blocking': blocking, 'result': result},
                      json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]), verify=False)
             
    @dclayMethod()
    def when_unfederated(self):
        print("Calling when unfederated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.remove_events_snapshot(self)

    @dclayMethod()
    def delete(self):
        self.objects_refs = list()


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
    @ClassField trajectory_pt list<anything>
    @ClassField geohash str
    """
    # events_history changed into dict<int, CityNS.classes.Event> instead of list<...>. collections.OrderedDict(sorted(events_history.items()))
    
    @dclayMethod(id_object='str', obj_type='str')
    def __init__(self, id_object, obj_type):
        self.id_object = id_object
        self.type = obj_type
        self.events_history = dict()
        self.trajectory_px = []
        self.trajectory_py = []
        self.trajectory_pt = []
        self.geohash = ""

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        # self.events_history.append(event)
        self.events_history[event.timestamp] = event

    # Updates the trajectory prediction
    @dclayMethod(tpx='list<float>', tpy='list<float>', tpt='list<anything>')
    def add_prediction(self, tpx, tpy, tpt):
        self.trajectory_px = tpx
        self.trajectory_py = tpy
        self.trajectory_pt = tpt
    
    # Returns the Object and its Events history (Deque format)
    @dclayMethod(return_="anything")
    def get_events_history(self):
        from collections import deque, OrderedDict
        # Events in following format(dqx, dqy, dqt)
        dqx = deque()
        dqy = deque()
        dqt = deque()
        for _, event in OrderedDict(sorted(self.events_history.items())).items():
            dqx.append(event.longitude_pos)
            dqy.append(event.latitude_pos)
            dqt.append(event.timestamp)
        return dqx, dqy, dqt

    @dclayMethod(return_='str')
    def __str__(self):
        return "Object %s of type %s with Events %s" % (str(self.id_object), str(self.type), str(self.events_history)) # str(self.events_history.values())


"""
Event: Instantiation of an Object for a given position and time.
"""
class Event(DataClayObject):
    """
    @ClassField id_event int
    @ClassField detected_object CityNS.classes.Object
    @ClassField timestamp anything
    @ClassField speed anything
    @ClassField yaw anything
    @ClassField longitude_pos anything
    @ClassField latitude_pos anything
    """
    @dclayMethod(id_event='int', detected_object='CityNS.classes.Object', timestamp='anything', speed='anything',
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
    def __str__(self):
        return "(long=%s,lat=%s,time=%s,speed=%s,yaw=%s,id=%s)" % (str(self.longitude_pos), str(self.latitude_pos),
                                                                   str(self.timestamp), str(self.speed), str(self.yaw),
                                                                   str(self.id_event))

    @dclayMethod()
    def when_federated(self):
        self.detected_object.add_event(self)
