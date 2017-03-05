
# XXX they should act as dictionaries themselves

class StenoDict(object):
	def __init__(self):
		self._dictionary = {}
		pass

class JsonDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'json'

	@classmethod
	def title(cls):
		return 'JSON dictionary'

	def can_handle(self, fh):
		return False

	def load(self, filename):
		pass

	def save(self, filename):
		pass

class RtfDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'rtf'

	@classmethod
	def title(cls):
		return 'RTF dictionary'

	def can_handle(self, fh):
		return False

	def load(self, filename):
		pass

	def save(self, filename):
		pass

class DctDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'dct'

	@classmethod
	def title(cls):
		return 'DCT dictionary (read-only)'

	def can_handle(self, fh):
		return False

	def load(self, filename):
		pass

	def save(self, filename):
		pass

