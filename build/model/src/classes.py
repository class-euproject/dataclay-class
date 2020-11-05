from dataclay import DataClayObject, dclayMethod

"""
City Knowledge Base: collection of Events Snapshots
"""
class DKB(DataClayObject):
    """
    @ClassField kb list<CityNS.classes.EventsSnapshot>
    @ClassField K int
    @ClassField connectedCars list<anything>
    @ClassField smartCars list<anything>

    @dclayImportFrom geolib import geohash
    """
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

    # returns a set of all relevant objects from K latest snapshots inside the specified geohashes. If
    # with_neighbors == True, return also neighbors; if == False, then return
    # If with_tp == True, return only objects with trajectory prediction; if == False, then return only objects without
    #           trajectory prediction. If == None, then return all objects (with/without tp)
    # If connected == True, return connected car objects only, if == False then return all non-connected cars.
    # If == None, then return all objects
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
                            """
                            if connected is None or not connected and obj.type not in self.connectedCars+self.smartCars\
                                    or connected and obj.type in self.connectedCars+self.smartCars:
                                objs.add(obj)
                            elif 
                                objs.add(obj)
                            """

        return objs

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def remove_events_snapshot(self, event_snp): 
        pass


"""
Events Snapshots: List of the objects detected in an snapshot. Each object
contains a list of events (last event for current snapshot and events history).
"""
class EventsSnapshot(DataClayObject):
    """
    @ClassField objects_refs list<str>
    @ClassField snap_alias str
    """
    # @ClassField timestamp anything # TODO: to be added

    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.objects_refs = []
        self.snap_alias = alias

    @dclayMethod(object_alias="str")
    def add_object_refs(self, object_alias):
        self.objects_refs.append(object_alias)

    # Returns the list of Object refs
    @dclayMethod(return_='list<str>')
    def get_objects_refs(self):
        return self.objects_refs

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


# TODO: add new class that inherits from object which is smartCar and connectedCar
"""
Object: Vehicle or Pedestrian detected
        Objects are classified by type: Pedestrian, Bicycle, Car, Track, ...
        Only if it is not a pedestrian, the values speed and yaw are set.
"""
class Object(DataClayObject):
    """
    @ClassField id_object str
    @ClassField type str
    @ClassField events_history list<CityNS.classes.Event>
    @ClassField trajectory_px list<float>
    @ClassField trajectory_py list<float>
    @ClassField trajectory_pt list<anything>
    @ClassField geohash str
    """
    
    @dclayMethod(id_object='str', obj_type='str')
    def __init__(self, id_object, obj_type):
        self.id_object = id_object
        self.type = obj_type
        self.events_history = []
        self.trajectory_px = []
        self.trajectory_py = []
        self.trajectory_pt = []
        self.geohash = ""

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.events_history.append(event)

    # Updates the trajectory prediction
    @dclayMethod(tpx='list<float>', tpy='list<float>', tpt='list<anything>')
    def add_prediction(self, tpx, tpy, tpt):
        self.trajectory_px = tpx
        self.trajectory_py = tpy
        self.trajectory_pt = tpt
    
    # Returns the Object and its Events history (Deque format)
    @dclayMethod(return_="anything")
    def get_events_history(self):
        from collections import deque
        # Events in following format(dqx, dqy, dqt)
        dqx = deque()
        dqy = deque()
        dqt = deque()
        for event in self.events_history:
            dqx.append(event.longitude_pos)
            dqy.append(event.latitude_pos)
            dqt.append(event.timestamp)
        return dqx, dqy, dqt

    @dclayMethod(return_='str')
    def __str__(self):
        return "Object %s of type %s with Events %s" % (str(self.id_object), str(self.type), str(self.events_history))


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
