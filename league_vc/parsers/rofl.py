import sys
import json


class ROFLParser:
    """
    Parse a .rofl replay and get its metadata.
    """
    byteorder = sys.byteorder
    length_fields_offset = 262
    length_fields_bytesize = 26

    @classmethod
    def int_from_bytes(cls, buffer):
        return int.from_bytes(buffer, byteorder=cls.byteorder, signed=False)

    def __init__(self, path):
        self.file = open(path, 'rb')
        self.length_fields = self.extract_length_fields()
        self.metadata = self.extract_metadata()

    def read(self, offset, size):
        self.file.seek(offset)
        return self.file.read(size)

    def extract_length_fields(self):
        """
        Get the length fields and offsets from the ROFL files.
        """
        buffer = self.read(self.length_fields_offset, self.length_fields_bytesize)
        return {
            'header_length': self.int_from_bytes(buffer[0:2]),
            'file_length': self.int_from_bytes(buffer[2:6]),
            'metadata_offset': self.int_from_bytes(buffer[6:10]),
            'metadata_length': self.int_from_bytes(buffer[10:14]),
            'payload_header_offset': self.int_from_bytes(buffer[14:18]),
            'payload_header_length': self.int_from_bytes(buffer[18:22]),
            'payload_offset': self.int_from_bytes(buffer[22:26]),
        }

    def extract_metadata(self):
        """
        Load the metadata from the replay.
        """
        metadata_bytes = self.read(self.length_fields['metadata_offset'],
                                   self.length_fields['metadata_length'])

        return json.loads(metadata_bytes)
