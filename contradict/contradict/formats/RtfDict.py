from contradict.formats.StenoDict import StenoDict

class RtfDict(StenoDict):

	def keyword(self):
		return 'rtf'

	def title(self):
		return 'RTF dictionary'

	def can_handle(self, fh):
		if fh.read(6) == '{\\rtf1':
			return True
		else:
			return False

	def load_from_file(self, filename):
		pass

	def can_save_to_file(self):
		return True

	def save_to_file(self, filename):
		pass
