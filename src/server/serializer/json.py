# src/server/serializer/json.py

from .base import SerializerBase
import json

class JSONSerializer(SerializerBase):

    def encode(self, data):
        payload = json.dumps(data)
        return payload.encode()

    def decode(self, data):
        revc_data = json.loads(data)
        return revc_data