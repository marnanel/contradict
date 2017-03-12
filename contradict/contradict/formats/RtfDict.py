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
	def _rtf_escape(s):
		for c in r'\{}':
			s = s.replace(c, '\\'+c)
		return s

	@classmethod
	def save_to_file(cls, filename, contents):
		fh = codecs.open(filename, 'wb',
			encoding="UTF-8")

		fh.write(r'{\rtf1\ansi{\*\cxrev100}'+
			r'\cxdict{\*\cxsystem contradict.marnanel.org}'+
			r'{\stylesheet{\s0 Normal;}}'+
			'\r\n')

		for (key, value) in contents.items():
			fh.write(r'{\*\cxs %(steno)s}%(translation)s' % {
				'steno': key,
				'translation': value,
				}+'\r\n')

		fh.write(r'}'+'\r\n')
		fh.close()

