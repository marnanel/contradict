from contradict.formats.StenoDict import StenoDict

class RtfDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'rtf'

	@classmethod
	def title(cls):
		return 'RTF dictionary'

	@classmethod
	def can_handle(cls, fh):
		if fh.read(6) == '{\\rtf1':
			return True
		else:
			return False

	@classmethod
	def load_from_file(cls, filename):
		pass

	@classmethod
	def can_save_to_file(cls):
		return True

	@classmethod
	def save_to_file(cls, filename):
		pass
