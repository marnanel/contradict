# Stripped-down Jet (MDB) reader for Plover.

import struct

DATA_PAGE_TYPE = 1
TABLE_CONTROL_PAGE_TYPE = 2

PAGE_SIZE = 4096
REALINDEX_ENTRY_SIZE = 12
COLUMN_ENTRY_SIZE = 25

# Pages of all types:
PAGE_TYPE_OFFSET = 0

# Table control pages:
COLUMN_COUNT_OFFSET = 45
REALINDEX_COUNT_OFFSET = 51
COLUMNS_START_OFFSET = 63

# Data pages:
CONTROLLING_TABLE_OFFSET = 4
ROW_COUNT_OFFSET = 12
ROW_TABLE_OFFSET = 14

# Types of columns:
COLUMN_TYPE_TEXT = 10
COLUMN_TYPE_INT = 3

SIZE_TO_FORMAT = {
	1: "<B",
	2: "<H",
	4: "<I",
}

USEFUL_COLUMNS = ('Steno', 'English', 'Flags')

class JetDictionary(object):
	def __init__(self, filename):
		self._fh = open(filename, 'rb')

		self._control = self._find_control()
		print 'Control:', self._control

		self._find_data()

	def _find_control(self):
		# First we need to find the control page for the Dictionary table.
		# Ordinarily this would involve finding the catalogue table, then
		# then using it to look up the address. But since we assume this is
		# a standard dictionary database, there should be exactly one
		# table whose control page looks like a dictionary. So we can
		# just spin through and look for that.

		# The earliest possible index of the dictionary table is 3.
		page = 3

		while True:

			self._load_page(page)
			if not self._page:
				# hit the end of the file; give up
				raise ValueError("no dictionary found")

			page_type = self.get_int(PAGE_TYPE_OFFSET, 1)
			if page_type==TABLE_CONTROL_PAGE_TYPE:

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
					result['page'] = page
					return result

			page += 1

	def _find_data(self):

		# I suspect that data pages can't occur before the
		# corresponding control page, but I don't know
		# this for sure, so let's be on the safe side
		# and start reading from the beginning.
		page = 3

		while True:
			self._load_page(page)
			if not self._page:
				# hit the end of the file; we're done
				return

			page_type = self.get_int(PAGE_TYPE_OFFSET, 1)
			if page_type==DATA_PAGE_TYPE:

				controlling_table = self.get_int(CONTROLLING_TABLE_OFFSET, 4)
				if controlling_table==self._control['page']:
					row_count = self.get_int(ROW_COUNT_OFFSET, 2)

					print '----', page, 'has', row_count
					end_of_record = PAGE_SIZE-1
					for i in range(row_count):
						start_of_record = self.get_int(ROW_TABLE_OFFSET+i*2, 2)
						print '-- #', i, 'from', hex(start_of_record), 'to', hex(end_of_record)

						if start_of_record & 0x8000:
							#  0x8000 = deleted row
							continue
						elif start_of_record & 0x4000:
							#  0x4000 = 4-byte reference to another data page,
							#             which we're going to find and
							#             read anyway
							end_of_record -= 4
							continue

						field_count = self.get_int(start_of_record, 1)
						nullmask_size = (field_count+7)/8
						variable_field_count = self.get_int(end_of_record - (nullmask_size+1), 2)
						variable_fields_offset = end_of_record - (nullmask_size+1+variable_field_count*2)

						print field_count, variable_field_count, variable_fields_offset
						end_of_field = (variable_fields_offset - start_of_record)-3
						for j in range(variable_field_count):
							start_of_field = self.get_int(variable_fields_offset+j*2, 2)
							try:
								print self.get_string(start_of_field+start_of_record,
									(end_of_field-start_of_field)+1)
							except Exception, e:
								print repr(e)
							end_of_field = start_of_field-1

						# Records are stored backwards.
						end_of_record = start_of_record-1

			page += 1

	def get_int(self, offset=0, size=2):
		encoded = self._page[offset:offset+size]
		try:
			return struct.unpack(SIZE_TO_FORMAT[size], encoded)[0]
		except Exception, e:
			print repr(e)
			return 0

	def get_string(self, offset=0, length=0):
		encoded = self._page[offset:offset+length]
		try:
			return bytes.decode(encoded, encoding='UTF-16')
		except Exception, e:
			return repr(e)

	def _load_page(self, page_number):
		self._fh.seek(page_number*PAGE_SIZE)
		self._page = self._fh.read(PAGE_SIZE)

if __name__=='__main__':
	print JetDictionary('/tmp/stened.dct')

