# Automatically created by dataClay
import os
import sys

from dataclay import dclayMethod, dclayEmptyMethod, DataClayObject
from dataclay.contrib.dummy_pycompss import *

from logging import getLogger
getLogger('dataclay.deployed_classes').debug('Package path: /stubs/sources/CityNS/classes')
StorageObject = DataClayObject

###############################################################
######### <Class-based imports>:


######### </Class-based imports>
###############################################################

try:
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    pass

# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: DKB
class DKB(DataClayObject):

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def remove_events_snapshot(self, event_snp): 
        pass
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
    @dclayMethod()
    def reset_dkb(self):
        self.kb = []
    @dclayMethod(eventsSt='list<CityNS.classes.EventsSnapshot>')
    def aggregate_events(self, events_st):
        for event in events_st:
            self.add_events_snapshot(event)
    @dclayMethod()
    def __init__(self):
        self.kb = []
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod(event_snp='CityNS.classes.EventsSnapshot')
    def add_events_snapshot(self, event_snp): 
        self.kb.append(event_snp)
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: Event
class Event(DataClayObject):

    @dclayMethod(id_event='int', timestamp='anything', longitude_pos='float', latitude_pos='float')
    def __init__(self, id_event, timestamp, longitude_pos, latitude_pos):
        self.id_event = id_event
        self.timestamp = timestamp
        self.longitude_pos = longitude_pos
        self.latitude_pos = latitude_pos
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod(return_='str')
    def __str__(self):
        return "(long=%s,lat=%s,time=%s,id=%s)" % (str(self.longitude_pos),str(self.latitude_pos),str(self.timestamp),str(self.id_event))
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: Object
class Object(DataClayObject):

    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
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
    @dclayMethod(id_object='int', obj_type='str', speed='float', yaw='float')
    def __init__(self, id_object, obj_type, speed, yaw):
        self.id_object = id_object
        self.type = obj_type
        self.speed = speed
        self.yaw = yaw
        self.events_history = []
        self.trajectory_px = []
        self.trajectory_py = []
        self.trajectory_pt = []
    @dclayMethod(tpx='list<float>', tpy='list<float>', tpt='list<anything>')
    def add_prediction(self, tpx, tpy, tpt):
        self.trajectory_px = tpx
        self.trajectory_py = tpy
        self.trajectory_pt = tpt
    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.events_history.append(event)
    @dclayMethod(return_='str')
    def __str__(self):
        return "Object %s of type %s with Events %s" % (str(self.id_object), str(self.type), str(self.events_history))
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: EventsSnapshot
class EventsSnapshot(DataClayObject):

    @dclayMethod()
    def delete(self):
        self.objects_refs = list()
    @dclayMethod(return_='list<str>')
    def get_objects_refs(self):
        return self.objects_refs
    @dclayMethod() 
    def when_federated(self):
        import requests
        print("Calling when federated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.add_events_snapshot(self)
        # TODO: trigger prediction via REST with alias specified for last EventsSnapshot
        APIHOST = 'https://192.168.7.40:31001'
        AUTH_KEY = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
        NAMESPACE = '_'
        BLOCKING = 'true'
        RESULT = 'true'
        TRIGGER = 'tp-trigger'
        url = APIHOST + '/api/v1/namespaces/' + NAMESPACE + '/triggers/' + TRIGGER
        user_pass = AUTH_KEY.split(':')
        alias = self.snap_alias
        response = requests.post(url, params={'blocking':BLOCKING, 'result':RESULT, 'ALIAS':str(alias)}, auth=(user_pass[0], user_pass[1]), verify=False)
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod()
    def when_unfederated(self):
        print("Calling when unfederated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.remove_events_snapshot(self)
    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.objects_refs = []
        self.snap_alias = alias
    @dclayMethod(object_alias="str")
    def add_object_refs(self, object_alias):
        self.objects_refs.append(object_alias)
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: DKB
class DKB(DataClayObject):

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def remove_events_snapshot(self, event_snp): 
        pass
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
    @dclayMethod()
    def reset_dkb(self):
        self.kb = []
    @dclayMethod(eventsSt='list<CityNS.classes.EventsSnapshot>')
    def aggregate_events(self, events_st):
        for event in events_st:
            self.add_events_snapshot(event)
    @dclayMethod()
    def __init__(self):
        self.kb = []
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod(event_snp='CityNS.classes.EventsSnapshot')
    def add_events_snapshot(self, event_snp): 
        self.kb.append(event_snp)
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: Event
class Event(DataClayObject):

    @dclayMethod(id_event='int', timestamp='anything', longitude_pos='float', latitude_pos='float')
    def __init__(self, id_event, timestamp, longitude_pos, latitude_pos):
        self.id_event = id_event
        self.timestamp = timestamp
        self.longitude_pos = longitude_pos
        self.latitude_pos = latitude_pos
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod(return_='str')
    def __str__(self):
        return "(long=%s,lat=%s,time=%s,id=%s)" % (str(self.longitude_pos),str(self.latitude_pos),str(self.timestamp),str(self.id_event))
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: Object
class Object(DataClayObject):

    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
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
    @dclayMethod(id_object='int', obj_type='str', speed='float', yaw='float')
    def __init__(self, id_object, obj_type, speed, yaw):
        self.id_object = id_object
        self.type = obj_type
        self.speed = speed
        self.yaw = yaw
        self.events_history = []
        self.trajectory_px = []
        self.trajectory_py = []
        self.trajectory_pt = []
    @dclayMethod(tpx='list<float>', tpy='list<float>', tpt='list<anything>')
    def add_prediction(self, tpx, tpy, tpt):
        self.trajectory_px = tpx
        self.trajectory_py = tpy
        self.trajectory_pt = tpt
    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.events_history.append(event)
    @dclayMethod(return_='str')
    def __str__(self):
        return "Object %s of type %s with Events %s" % (str(self.id_object), str(self.type), str(self.events_history))
    pass
# End of class definition
# dataClay header
# This is a Stub, to be used for the user client
from dataclay import dclayMethod, DataClayObject

# Imports required by the following class

# Definition of dataClay object class: EventsSnapshot
class EventsSnapshot(DataClayObject):

    @dclayMethod()
    def delete(self):
        self.objects_refs = list()
    @dclayMethod(return_='list<str>')
    def get_objects_refs(self):
        return self.objects_refs
    @dclayMethod() 
    def when_federated(self):
        import requests
        print("Calling when federated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.add_events_snapshot(self)
        # TODO: trigger prediction via REST with alias specified for last EventsSnapshot
        APIHOST = 'https://192.168.7.40:31001'
        AUTH_KEY = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
        NAMESPACE = '_'
        BLOCKING = 'true'
        RESULT = 'true'
        TRIGGER = 'tp-trigger'
        url = APIHOST + '/api/v1/namespaces/' + NAMESPACE + '/triggers/' + TRIGGER
        user_pass = AUTH_KEY.split(':')
        alias = self.snap_alias
        response = requests.post(url, params={'blocking':BLOCKING, 'result':RESULT}, json={"ALIAS": str(alias)}, auth=(user_pass[0], user_pass[1]), verify=False)
    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
    @dclayMethod()
    def when_unfederated(self):
        print("Calling when unfederated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB")
        kb.remove_events_snapshot(self)
    @dclayMethod(alias='str')
    def __init__(self, alias):
        self.objects_refs = []
        self.snap_alias = alias
    @dclayMethod(object_alias="str")
    def add_object_refs(self, object_alias):
        self.objects_refs.append(object_alias)
    pass
# End of class definition
