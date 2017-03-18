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
		self._details['next'] = self.get_int(4, 4)
		self._details['autoincrement'] = self.get_int(db._tab_autoincrement_offset, 4)
		self._details['num_rows'] = self.get_int(db._tab_num_rows_offset, 4)
		self._details['num_var_cols'] = self.get_int(db._tab_num_cols_offset-2, 2)
		self._details['num_cols'] = self.get_int(db._tab_num_cols_offset, 2)
		self._details['num_idxs'] = self.get_int(db._tab_num_idxs_offset, 4)
		self._details['num_ridxs'] = self.get_int(db._tab_num_ridxs_offset, 4)
		self._details['first_data_page'] = self.get_int(db._tab_num_ridxs_offset, 4)

		# now pick up the columns

		cursor = db._tab_cols_start_offset + (self._details['num_ridxs']*db._tab_ridx_entry_size)

		columns = []
		for i in range(self['num_cols']):

			column = Column()
			column['type'] = self.get_int(cursor, 1)
			column['number'] = self.get_int(cursor+5, 2)
			column['offset_V'] = self.get_int(cursor+7, 2)
			column['number_bis'] = self.get_int(cursor+9, 2)
			column['offset_F'] = self.get_int(cursor+22,2)
			column['length'] = self.get_int(cursor+24,2)
			columns.append(column)

			cursor += db._tab_col_entry_size

		# the names are stored last

		for i in range(self['num_cols']):

			name_length = self.get_int(cursor, db._col_name_length_size)
			cursor += db._col_name_length_size

			columns[i]['name'] = self.get_string(cursor, name_length)
			cursor += name_length

		self._details['columns'] = sorted(columns,
			key = lambda c: c['number'])

class Table(object):
	def __init__(self, control_page):
		self._control_page = control_page

	def columns(self):
		return self._control_page['columns']

	def __repr__(self):

		def list_repr(l):
			return ','.join(l)+'\n'

		result = ''
		result += list_repr([x['name'] for x in self.columns()])
		return result

class DataPage(Page):

	def __init__(self, data, pagenumber=None, parent=None):
		self._wrt = None
		Page.__init__(self, data, pagenumber, parent)

	def set_with_respect_to(self, wrt):
		print 'WRT:', wrt
		self._wrt = wrt

	def _gather_details(self):
		db = self._parent
		wrt = self._wrt

		self._details['type'] = 'data'
		self._details['table'] = self.get_int(4, 4)
		self._details['count'] = self.get_int(db._data_numrows_offset, 2)

		self._details['offset_row'] = []
		cursor = db._data_numrows_offset + 2
		for i in range(self._details['count']):
			self._details['offset_row'].append(self.get_int(cursor, 2))
			cursor += 2

		self._details['data'] = []
		for offset in self._details['offset_row']:
			if offset & 0x8000:
				self._details['data'].append((offset, 'deleted'))
				continue

			if offset & 0x4000:
				self._details['data'].append((offset, 'lookup nyi'))
				continue

			result = {
				'at': offset,
				'num_cols': self.get_int(offset, 2),
			}

			self._details['data'].append(result)


PAGE_TYPES = {
	1: DataPage,
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
		self._tab_autoincrement_offset = 16
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
		self._data_numrows_offset = 8

	def _set_Jet4_constants(self):
		self._page_size = 4096
		self._row_count_offset = 0x0c
		self._tab_num_rows_offset = 16
		self._tab_autoincrement_offset = 20
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
		self._data_numrows_offset = 12

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
	#for i in (0x16,0x17,0x18,0x19):
	#	print mdb.get_page(i)
	page = mdb.get_page(2)
	print page
	table = Table(page)

	data = mdb.get_page(0xe)
	data.set_with_respect_to(table)
	print data
	
if __name__=='__main__':
	main()
