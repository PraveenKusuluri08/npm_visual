# import neomodel
# from datetime import datetime
#

# class NeomodelConnectionTest(neomodel.StructuredNode):
#     __primarykey__ = "name"
#     name = neomodel.StringProperty(unique_index=True)
#     name2 = neomodel.StringProperty(unique_index=True)
#
#     # Add a created_at timestamp field
#     created_at = neomodel.DateTimeProperty(default=datetime.now)
#

from npmvisual._models.dependency import Dependency
from npmvisual._models.package import Package
from npmvisual._models.neomodel_connection_test import NeomodelConnectionTest


"""
This exists to resolve circular imports. Import from this file instead of npmvisual/_models/

This is an implementation of the interface pattern. 

"""
