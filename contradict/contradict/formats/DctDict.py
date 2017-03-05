from contradict.formats.StenoDict import StenoDict

class DctDict(StenoDict):

	def keyword(self):
		return 'dct'

	def title(self):
		return 'DCT dictionary'

	def can_handle(self, fh):
		magicNumber = fh.read(19)
		if magicNumber in (
			'\x00\x01\x00\x00Standard Jet DB',
			'\x00\x01\x00\x00Standard ACE DB',
		):
			return True

		return False

	def load_from_file(self, filename):
		pass

	def can_save_to_file(self):
		return False

	def save_to_file(self, filename):
		raise ValueError("Can't write to .dct dictionaries")
