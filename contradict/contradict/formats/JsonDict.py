from contradict.formats.StenoDict import StenoDict
import json
import codecs

class JsonDict(StenoDict):

	def keyword(self):
		return 'json'

	def title(self):
		return 'JSON dictionary'

	def can_handle(self, fh):
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

	def load_from_file(self, filename):
		f = codecs.open(filename, 'r', encoding='utf-8')
		result = json.load(f)
		f.close()
		return result

	def save_to_file(self, filename, contents):
		f = codecs.open(filename, 'w', encoding='utf-8')
		json.dump(f, contents,
			sort_keys = True,
			separators = (',\n', ': '),
			)
		f.close()
