# highly experimental code
# partly based on: https://github.com/brianb/mdbtools/blob/master/src/libmdb/table.c

class Detailed(object):
	def __init__(self):
		self._details = {}
		self._gather_details()

	def _gather_details(self):
		pass

	def __repr__(self):
		result = '--- object of class %s ---\n' % (repr(self.__class__))
		for (key, value) in self._details.items():
			result += '%30s %s\n' % (key, value)

		result += '--- ends ---\n'

		return result

	def __getitem__(self, key):
		return self._details[key]

	def __setitem__(self, key, value):
		self._details[key] = value

class Column(Detailed):
	pass

class Page(Detailed):

	def __init__(self, data, pagenumber=None, parent=None):

		self._data = data
		self._parent = parent
		Detailed.__init__(self)
		self['page_number'] = pagenumber

	def _gather_details(self):
		Detailed._gather_details(self)
		self._details['type'] = 'page'

	def get_int(self, offset=0, count=2):

		cursor = offset

		result = 0
		for i in range(count):
			addend = ord(self._data[cursor+i])
			result += addend << (i*8)

		return result

	def get_string(self, offset, length):
		return bytes.decode(self._data[offset:offset+length],
					encoding='UTF-16')

class TablePage(Page):

	def _gather_details(self):
		db = self._parent

		self._details['type'] = 'table'
		self._details['num_rows'] = self.get_int(db._tab_num_rows_offset, 4)
		self._details['num_var_cols'] = self.get_int(db._tab_num_cols_offset-2, 2)
		self._details['num_cols'] = self.get_int(db._tab_num_cols_offset, 2)
		self._details['num_idxs'] = self.get_int(db._tab_num_idxs_offset, 4)
		self._details['num_ridxs'] = self.get_int(db._tab_num_ridxs_offset, 4)
		self._details['first_data_page'] = self.get_int(db._tab_num_ridxs_offset, 4)

		# now pick up the columns

		cursor = db._tab_cols_start_offset + (self._details['num_ridxs']*db._tab_ridx_entry_size)
		print 'cursor:', cursor

		for i in range(self['num_cols']):

			column = Column()
			column['type'] = self.get_int(cursor, 1)
			column['var_col'] = self.get_int(cursor + db._col_num_offset, 2)
			column['row_col'] = self.get_int(cursor + db._tab_row_col_num_offset, 2)
			column['fixed_offset'] = self.get_int(cursor + db._tab_col_offset_fixed, 2)
			self[i] = column
			cursor += db._tab_col_entry_size

		# the names are stored last

		for i in range(self['num_cols']):

			name_length = self.get_int(cursor, db._col_name_length_size)
			cursor += db._col_name_length_size

			self[i]['name'] = self.get_string(cursor, name_length)
			cursor += name_length

PAGE_TYPES = {
	2: TablePage,
	}

class Mdb(object):
	def __init__(self, filename):
		self._filename = filename
		self._fh = open(filename, 'rb')

		# FIXME rewrite in terms of self.get_int()
		self._fh.seek(0x14)
		signature = [ord(self._fh.read(1)) for i in range(4)]
		signature.reverse()

		if signature==[0, 0, 0, 0]:
			self._format = 'Jet3'
			self._set_Jet3_constants()
		elif signature==[0, 0, 0, 1]:
			self._format = 'Jet4'
			self._set_Jet4_constants()
		elif signature==[0, 0, 0, 2]:
			self._format = 'AccDB2007'
			self._set_Jet4_constants()
		elif signature==[0, 0, 1, 3]:
			self._format = 'AccDB2010' # weird, isn't it
			self._set_Jet4_constants()
		else:
			raise ValueError("Unknown format signature: "+repr(signature))

	def _set_Jet3_constants(self):
		self._page_size = 2048
		self._row_count_offset = 0x08
		self._tab_num_rows_offset = 12
		self._tab_num_cols_offset = 25
		self._tab_num_idxs_offset = 27
		self._tab_num_ridxs_offset = 31
		self._tab_usage_map_offset = 35
		self._tab_first_dpg_offset = 36
		self._tab_cols_start_offset = 43
		self._tab_ridx_entry_size = 8
		self._col_flags_offset = 13
		self._col_size_offset = 16
		self._col_num_offset = 1
		self._tab_col_entry_size = 18
		self._tab_free_map_offset = 39
		self._tab_col_offset_var = 3
		self._tab_col_offset_fixed = 14
		self._tab_row_col_num_offset = 5
		self._col_name_length_size = 1

	def _set_Jet4_constants(self):
		self._page_size = 4096
		self._row_count_offset = 0x0c
		self._tab_num_rows_offset = 16
		self._tab_num_cols_offset = 45
		self._tab_num_idxs_offset = 47
		self._tab_num_ridxs_offset = 51
		self._tab_usage_map_offset = 55
		self._tab_first_dpg_offset = 56
		self._tab_cols_start_offset = 63
		self._tab_ridx_entry_size = 12
		self._col_flags_offset = 15
		self._col_size_offset = 23
		self._col_num_offset = 5
		self._tab_col_entry_size = 25
		self._tab_free_map_offset = 59
		self._tab_col_offset_var = 7
		self._tab_col_offset_fixed = 21
		self._tab_row_col_num_offset = 9
		self._col_name_length_size = 2

	def catalog(self):

		return Table(db=self,
			control_page=2)

	def get_page(self, which):
		self._fh.seek(self._page_size*which)
		data = self._fh.read(self._page_size)

		pageclass = PAGE_TYPES.get(ord(data[0]), Page)

		return pageclass(data, which, self)

def main():
	mdb = Mdb('/tmp/stened.mdb')
	p2 = mdb.get_page(2)
	print p2
	
if __name__=='__main__':
	main()
