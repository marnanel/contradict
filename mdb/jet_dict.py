# Stripped-down Jet (MDB) reader for Plover.

import struct

TABLE_CONTROL_PAGE_TYPE = chr(2)

PAGE_SIZE = 4096
REALINDEX_ENTRY_SIZE = 12
COLUMN_ENTRY_SIZE = 25

COLUMN_COUNT_OFFSET = 45
REALINDEX_COUNT_OFFSET = 51
COLUMNS_START_OFFSET = 63

SIZE_TO_FORMAT = {
	1: "<B",
	2: "<H",
	4: "<I",
}

USEFUL_COLUMNS = ('Steno', 'English', 'Flags')

class JetDictionary(object):
	def __init__(self, filename):
		self._fh = open(filename, 'rb')

		self._find_control()
		print 'Control:', self._control_page, self._dictionary_fields

	def _find_control(self):
		# First we need to find the control page for the Dictionary table.
		# Ordinarily this would involve finding the catalogue table, then
		# then using it to look up the address. But since we assume this is
		# a standard dictionary database, there should be exactly one
		# table whose control page looks like a dictionary. So we can
		# just spin through and look for that.

		# The earliest possible index of the dictionary table is 3.
		self._control_page = 3

		while True:
			self._fh.seek(self._control_page * PAGE_SIZE)
			page_type = self._fh.read(1)
			if not page_type:
				# hit the end of the file; give up
				raise ValueError("no dictionary found")

			if page_type==TABLE_CONTROL_PAGE_TYPE:
				print '----', self._control_page

				column_count = self.get_int(COLUMN_COUNT_OFFSET, size=2)
				index_count = self.get_int(REALINDEX_COUNT_OFFSET, size=4)

				# Skip the realindexes.
				cursor = COLUMNS_START_OFFSET + index_count*REALINDEX_ENTRY_SIZE

				columns = {}
				result = {}

				for i in range(column_count):
					columns[i] = {
						'number': self.get_int(cursor+5, 2),
						'type': self.get_int(cursor, 1),
						'offset_V': self.get_int(cursor+7, 2),
						'offset_F': self.get_int(cursor+21, 2),
					}
					cursor += COLUMN_ENTRY_SIZE

				for i in range(column_count):

					name_length = self.get_int(cursor, 2)
					cursor += 2

					name = self.get_string(cursor, name_length)

					if name in USEFUL_COLUMNS:
						result[name] = columns[i]

					cursor += name_length

				if len(result)==len(USEFUL_COLUMNS):
					# we've caught them all!
					self._dictionary_fields = result
					return

			self._control_page += 1

	def get_int(self, offset=0, size=2):

		self._fh.seek(self._control_page*PAGE_SIZE + offset)
		encoded = self._fh.read(size)

		return struct.unpack(SIZE_TO_FORMAT[size], encoded)[0]

	def get_string(self, offset=0, length=0):

		self._fh.seek(self._control_page*PAGE_SIZE + offset)
		encoded = self._fh.read(length)
		return bytes.decode(encoded, encoding='UTF-16')

if __name__=='__main__':
	print JetDictionary('/tmp/stened.dct')

