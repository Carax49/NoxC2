# src/server/serializer/json.py

import json
from .base import SerializerBase

class JSONSerializer(SerializerBase):

    def __str__(self):
        return "JSON"

    def encode(self, data):
        try:
            return json.dumps(data).encode("utf-8")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Data is not JSON serializable: {e}") from e

    def decode(self, data):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e
        except (TypeError, UnicodeDecodeError) as e:
            raise ValueError(f"Cannot decode data: {e}") from e