from contradict.formats.StenoDict import StenoDict

class TableDict(StenoDict):

	def keyword(self):
		return 'table'

	def title(self):
		return 'Table'

	def can_handle(self, fh):
		# XXX do this with a regexp
		return False

	def load_from_file(self, filename):
		pass

	def can_save_to_file(self):
		return False

	def save_to_file(self, filename):
		raise ValueError("Can't write to .dct dictionaries")
