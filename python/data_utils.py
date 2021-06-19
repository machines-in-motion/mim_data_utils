import struct
import array

import numpy as np

class DataLogger:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fh = None
        self.fields = []
        self.field_data = []
        self.file_index = -1

    def add_field(self, field_name, field_size):
        assert field_size > 0, 'Field size must be positive'
        assert type(field_size) == int, 'Expecting integer'
        assert self.fh is None, 'Cannot add field once logging started'

        self.fields.append((field_name, field_size))
        self.field_data.append(np.zeros(field_size, np.double))
        return len(self.fields) - 1

    def init_file(self):
        self.fh = open(self.filepath, "wb+")

        # Write the header.
        arr = array.array('l', [0, len(self.fields)])
        self.fh.write(arr.tobytes())

        for (name, size) in self.fields:
            byt = struct.pack("64s I", name.encode('utf8'), size)
            self.fh.write(byt)

    def close_file(self):
        assert self.fh, 'File is not open'
        self.fh.close()

    def begin_next_timestamp(self):
        if self.fh is None:
            self.init_file()

        self.file_index += 1
        self.fh.seek(0, 0) # Beginning of the file.
        self.fh.write(struct.pack('l', self.file_index))

        self.fh.seek(0, 2) # End of the file.

    def log_array(self, field_id, value):
        self.field_data[field_id][:] = value

    def log_array(self, field_id, value):
        self.field_data[field_id][:] = value

    def log_int(self, field_id, value):
        self.field_data[field_id][0] = float(value)

    def log_float(self, field_id, value):
        self.field_data[field_id][0] = value

    def end_timestep(self):
        # Write the recorded field_data to the file.
        for value in self.field_data:
            self.fh.write(value.tobytes())

        self.fh.flush()


class DataReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fh = open(self.filepath, 'rb+')

        self.fields = []
        self.data = {}

        self.read_header()
        self.read_fields()
        self.read_data()

    def read_header(self):
        byt = self.fh.read(16)
        self.idx, self.num_fields = struct.unpack('ll', byt)

        print('idx:', self.idx, 'fields:', self.num_fields)

    def read_fields(self):
        for _ in range(self.num_fields):
            byt = self.fh.read(64 + 4)
            name, size = struct.unpack("64s I", byt)
            name = name.decode('utf8').rstrip('\x00')
            self.fields.append((name, size))
            self.data[name] = np.zeros((self.idx + 1, size), np.double)

        print(self.fields)

    def read_data(self):
        for i in range(self.idx + 1):
            for (field_name, field_size) in self.fields:
                arr = array.array('d')
                arr.frombytes(self.fh.read(8 * field_size))
                self.data[field_name][i] = arr
