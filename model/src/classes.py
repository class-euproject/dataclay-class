from dataclay import DataClayObject, dclayMethod
"""
City Knoledge Base: collection of Events Events Snapshots
"""
class DKB(DataClayObject):
    """
    @ClassField KB list<CityNS.classes.EventsSnapshot>
    """
    @dclayMethod()
    def __init__(self):
        self.KB = []

    @dclayMethod(eventSt='CityNS.classes.EventsSnapshot')
    def aggregatte(self, eventSt):
        self.KB.append(eventSt)

    @dclayMethod(eventsSt='list<CityNS.classes.EventsSnapshot>')
    def aggregatteEvents(self, eventsSt):
        for event in eventsSt:
            self.aggregatte(event)

    @dclayMethod()
    def resetDKB(self):
        self.KB = []

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def addEventsSnapshot(self, eventSnp): 
        self.KB.append(eventSnp)

    @dclayMethod(eventSnp='CityNS.classes.EventsSnapshot')
    def removeEventsSnapshot(self, eventSnp): 
        pass

    @dclayMethod(return_='anything')
    def getVehicles(self):
        result = set() 
        for eventSnp in self.KB: 
           for objInSnapshot in eventSnp.objectsRefs:
              if objInSnapshot.type != "Pedestrian":  
                  result.add(objInSnapshot)
        return result

"""
Events Snapshots: List of the objects detected in an snapshot. Each object
contains a list of events (last event for current snapshot and events history).
"""
class EventsSnapshot(DataClayObject):
    """
    @ClassField objectsRefs list<str>
    """

    @dclayMethod()
    def __init__(self):
        self.objectsRefs = []

    @dclayMethod(new_object="str")
    def add_object_ref(self, new_object):
        self.objectsRefs.append(new_object)

    # Returns the list of Object refs
    @dclayMethod(return_='list<str>')
    def getObjectsRefs(self):
        return self.objectsRefs

    @dclayMethod() 
    def when_federated(self):
        print("Calling when federated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB");
        kb.addEventsSnapshot(self);
        # TODO: require prediction via REST
        # for objectRef in self.objectsRefs: 
             # call prediction with str
             
    @dclayMethod()
    def when_unfederated(self):
        print("Calling when unfederated in EventsSnapshot")
        kb = DKB.get_by_alias("DKB");
        kb.removeEventsSnapshot(self);

    @dclayMethod()
    def delete(self):
        self.objectsRefs = list()

"""
Object: Vehicle or Pedestrian detected
        Objects are classified by type: Pedestrian, Bicycle, Car, Track, ...
        Only if it is not a pedestrian, the values speed and yaw are set.
"""
class Object(DataClayObject):
    """
    @ClassField idObject int
    @ClassField type str
    @ClassField speed float
    @ClassField yaw float
    @ClassField eventsHistory list<CityNS.classes.Event>
    @ClassField trajectoryP str
    """
    
    @dclayMethod(idObject='int', objType='str', speed='float', yaw='float')
    def __init__(self, idObject, objType, speed, yaw):
        self.idObject = idObject
        self.type = objType
        self.speed = speed
        self.yaw = yaw
        self.eventsHistory = []
        self.trajectoryP = None

    @dclayMethod(event='CityNS.classes.Event')
    def add_event(self, event):
        self.eventsHistory.append(event)

    # Updates the trajectory prediction
    @dclayMethod(tp='str')
    def add_prediction(self, tp):
        self.trajectoryP = tp
    
    # Returns the Object and its Events history (Deque format)
    @dclayMethod(return_="anything")
    def getObjectAndEventsHistory(self):
        # Events in following format(dqx, dqy, dqt)
        result = list()
        for event in self.eventsHistory: 
            result.append((event.longitudePos,event.latitudePos, event.timestamp))
        return result

    @dclayMethod(return_='str')
    def __str__(self):
        return "Object %s of type %s with Events %s" % (str(self.idObject), str(self.type), str(self.eventsHistory))

"""
Event: Instantiation of an Object for a given position and time.
"""
class Event(DataClayObject):
    """
    @ClassField idEvent int
    @ClassField timestamp anything
    @ClassField longitudePos float
    @ClassField latitudePos float
    """
    @dclayMethod(idEvent='int', timestamp='anything', longitudePos='float', latitudePos='float')
    def __init__(self, idEvent, timestamp, longitudePos, latitudePos):
        self.idEvent = idEvent
        self.timestamp = timestamp
        self.longitudePos = longitudePos
        self.latitudePos = latitudePos

    @dclayMethod(return_='str')
    def __str__(self):
        return "(long=%s,lat=%s,time=%s,id=%s)" % (str(self.longitudePos),str(self.latitudePos),str(self.timestamp),str(self.idEvent))
