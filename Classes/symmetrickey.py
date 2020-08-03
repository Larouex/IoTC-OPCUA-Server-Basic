# ==================================================================================
#   File:   symmetrickey.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    SaS key class for all operations on connections and generation of
#           keys used to connect via DPS and Azure IoT Central
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import base64
import hmac
import hashlib

class SymmetricKey():

    def __init__(self, Log):
        self.logger = Log
        self.data = []

    # derives a symmetric device key for a device id 
    # using the group symmetric key
    def compute_derived_symmetric_key(self, device_id, symmetric_key):
        try:
            message = device_id.encode("utf-8")
            signing_key = base64.b64decode(symmetric_key.encode("utf-8"))
            signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
            device_key_encoded = base64.b64encode(signed_hmac.digest())
            self.logger.info("Generated Device Key: %s", str(device_key_encoded.decode("utf-8")))
            return device_key_encoded.decode("utf-8")
        except Exception as ex:
            self.logger.warning("Failed to Generate Device Key: %s", ex)

