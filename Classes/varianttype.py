# ==================================================================================
#   File:   varianttype.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Helper to translate how we think of Types in IoT Central to 
#           the mapping of Variant Types as Defined in OPC/UA
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import logging

class VariantType():
    
    def __init__(self, logger):
        self.logger = logger

    def map_variant_type(self, iotc_data_type):

        data_types = {
            "Boolean": 1,
            "Date": 13,
            "DateTime": 13,
            "Double": 11,
            "Duration": 3,
            "Float": 10,
            "Geopoint": 3,
            "Integer": 6,
            "Long": 8,
            "String": 12,
            "Time": 13,
            "Vector": 3,
        }
        return data_types.get(iotc_data_type, None)

        # OPCUA REFERENCE
        # Boolean = 1
        # Byte = 3
        # ByteString = 15
        # DataValue = 23
        # DateTime = 13
        # DiagnosticInfo = 25
        # Double = 11
        # ExpandedNodeId = 18
        # ExtensionObject = 22
        # Float = 10
        # Guid = 14
        # Int16 = 4
        # Int32 = 6
        # Int64 = 8
        # LocalizedText = 21
        # NodeId = 17
        # Null = 0
        # QualifiedName = 20
        # SByte = 2
        # StatusCode = 19
        # String = 12
        # UInt16 = 5
        # UInt32 = 7
        # UInt64 = 9
        # Variant = 24
        # XmlElement = 16