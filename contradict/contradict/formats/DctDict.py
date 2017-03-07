from contradict.formats.StenoDict import StenoDict

class DctDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'dct'

	@classmethod
	def title(cls):
		return 'DCT dictionary'

	@classmethod
	def can_handle(cls, fh):
		magicNumber = fh.read(19)
		if magicNumber in (
			'\x00\x01\x00\x00Standard Jet DB',
			'\x00\x01\x00\x00Standard ACE DB',
		):
			return True

		return False

	@classmethod
	def load_from_file(cls, filename):
		pass

	@classmethod
	def can_save_to_file(cls):
		return False

	@classmethod
	def save_to_file(cls, filename):
		raise ValueError("Can't write to .dct dictionaries")
