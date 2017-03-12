from contradict.formats.StenoDict import StenoDict
import codecs
import rtfcre_dict

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
		return rtfcre_dict.load_dictionary(filename)

	@classmethod
	def can_save_to_file(cls):
		return True

        @classmethod
        def mime_type(cls):
		# application/rtf appears to be more current than text/rtf:
		# https://www.iana.org/assignments/media-types/media-types.xhtml
		# And anyway, it describes what we're doing better.
                return 'application/rtf'

	@classmethod
	def save_to_file(cls, filename, contents):
		return rtfcre_dict.save_dictionary(contents, open(filename, 'wb'))
