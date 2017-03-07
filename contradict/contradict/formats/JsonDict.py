from contradict.formats.StenoDict import StenoDict
import json
import codecs

class JsonDict(StenoDict):

	@classmethod
	def keyword(cls):
		return 'json'

	@classmethod
	def title(cls):
		return 'JSON dictionary'

	@classmethod
	def can_handle(cls, fh):
		byte = fh.read(1)
		if byte!='{':
			return False

		while True:
			byte = fh.read(1)

			if byte=='':
				return False

			if ord(byte) in (32, 9, 10, 13):
				# whitespace
				continue

			if byte in ('"', '}'):
				return True

			return False

	@classmethod
	def load_from_file(cls, filename):
		f = codecs.open(filename, 'r', encoding='utf-8')
		result = json.load(f)
		f.close()
		return result

	@classmethod
	def can_save_to_file(cls):
		return True

	@classmethod
	def save_to_file(cls, filename, contents):
		f = codecs.open(filename, 'w', encoding='utf-8')
		json.dump(contents, f,
			sort_keys = True,
			separators = (',\n', ': '),
			)
		f.close()
