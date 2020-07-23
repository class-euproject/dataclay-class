# Automatically created by dataClay
import os
import sys

from dataclay import dclayMethod, dclayEmptyMethod, DataClayObject
from dataclay.contrib.dummy_pycompss import *

from logging import getLogger
getLogger('dataclay.deployed_classes').debug('Package path: /stubs/sources')
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

