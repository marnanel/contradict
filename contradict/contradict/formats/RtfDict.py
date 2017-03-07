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
		raise ValueError("rtf loading support is not yet implemented")

	@classmethod
	def can_save_to_file(cls):
		return True

	@classmethod
	def _rtf_escape(s):
		for c in r'\{}':
			s = s.replace(c, '\\'+c)
		return s

	@classmethod
	def save_to_file(cls, filename, contents):
		fh = open(filename, 'wb')

		fh.write(r'{\rtf1\ansi{\*\cxrev100}'+
			r'\cxdict{\*\cxsystem contradict.marnanel.org}'+
			r'{\stylesheet{\s0 Normal;}}'+
			'\r\n')

		for (key, value) in contents.enumerate():
			fh.write(r'{\*\cxs %(steno)s}%(translation)s\r\n' % {
				'key': key,
				'value': value,
				})

		fh.write(r'}\r\n')
