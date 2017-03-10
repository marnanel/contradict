# highly experimental code
# partly based on: https://github.com/brianb/mdbtools/blob/master/src/libmdb/table.c

class Table(object):
	def __init__(self, db, control_page):
		self._db = db
		self._control_page = control_page

		if self.get_int(0, 1)!=2:
			raise ValueError("the catalog is not a table!")
		
		self._num_rows = self.get_int(self._db._tab_num_rows_offset, 4)
		self._num_var_cols = self.get_int(self._db._tab_num_cols_offset-2, 2)
		self._num_cols = self.get_int(self._db._tab_num_cols_offset, 2)
		self._num_idxs = self.get_int(self._db._tab_num_idxs_offset, 4)
		self._num_ridxs = self.get_int(self._db._tab_num_ridxs_offset, 4)
		self._first_data_page = self.get_int(self._db._tab_first_dpg_offset, 2)

		## columns

		self._columns = []

		print 'num_cols:', self._num_cols
		print 'col_entry_size:', self._db._tab_col_entry_size

		cursor = self._db._tab_cols_start_offset + (self._num_ridxs*self._db._tab_ridx_entry_size)
		print 'cursor:', cursor

		for i in range(self._num_cols):
			print
			print 'Column', i

			print 'type', self.get_int(cursor, 1)
			print 'var col number', self.get_int(cursor + self._db._col_num_offset, 2)
			print 'row col number', self.get_int(cursor + self._db._tab_row_col_num_offset, 2)
			print 'fixed offset', self.get_int(cursor + self._db._tab_col_offset_fixed, 2)

			cursor += self._db._tab_col_entry_size

		for i in range(self._num_cols):
			print
			print 'Column name:', i

			name_length = self.get_int(cursor, self._db._col_name_length_size)
			print 'Length:', name_length
			cursor += self._db._col_name_length_size

			name = self.get_string(cursor, name_length)
			print 'Name:', name

			cursor += name_length

	def get_int(self, offset, count=2):

		return self._db.get_int(
			page=self._control_page,
			offset=offset,
			count=count,
			)

	def get_string(self, offset, length):

		return self._db.get_string(
			page=self._control_page,
			offset=offset,
			length=length,
			)

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

	def get_int(self, page, offset=0, count=2):

		self._fh.seek(page*self._page_size + offset)

		shift = 0

		result = 0
		for i in range(count):
			addend = ord(self._fh.read(1))
			result += addend << shift
			shift += 8

		return result

	def get_string(self, page, offset, length):
		self._fh.seek(page*self._page_size + offset)

		return bytes.decode(self._fh.read(length),
				encoding='UTF-16')

	def _load_page(self, which):
		self._fh.seek(self._page_size*which)
		return self._fh.read(self._page_size)

	def catalog(self):

		return Table(db=self,
			control_page=2)

def main():
	mdb = Mdb('/tmp/stened.mdb')
	mdb.catalog()
	
if __name__=='__main__':
	main()
