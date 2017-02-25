import subprocess
import os.path
import csv
import sys

DICTIONARY_TABLE_NAME = 'dictionary'

# This is steno-specific, so we want to rethink
# this if we do palantype etc here.
#
# We need a hyphen if there are no vowels or * present,
# but there are right-hand keys present.
#
# So the bitmasks are:
#   ?#ST KPWH RAO* EUFR PBLG TSDZ
#              111 11              - vowels and *
#                    11 1111 1111  - right-hand keys
VOWELS     = 0x007C00
RIGHT_HAND = 0x0003FF

# FIXME this does not do escaping yet
class OutputRTF(object):

	def __init__(self, fh=sys.stdout):
		self.fh = fh

	def start(self):
		# we need to think of a better name for this
		self.fh.write(r'{\rtf1\ansi{\*\cxrev100}'+
			r'\cxdict{\*\cxsystem dct2rtf}'+
			r'{\stylesheet{\s0 Normal;}}'+
			'\r\n')

	def output(self, steno, translation):
		self.fh.write(r'{\*\cxs %(steno)s}%(translation)s' % {
			'steno': steno,
			'translation': translation,
		} + '\r\n')

	def finish(self):
		print r'}' + '\r\n'

class StenoDecoder(object):
	def __init__(self,
		# FIXME: what is the leftmost char,
		# and what should we do if it occurs?
		keys = '?#STKPWHRAO*EU-FRPBLGTSDZ',
		):

		self.keys = keys

	def decode(self, s):
		result = []

		# FIXME add hyphen
		# FIXME error handling

		while s:
			result.append('')
			stroke = int(s[:6], 16)

			needs_hyphen = (stroke & RIGHT_HAND) and not (stroke & VOWELS)

			for i in self.keys:
				if i=='-':
					if needs_hyphen:
						result[-1] += '-'
				else:
					if stroke & 0x800000:
						result[-1] += i
					stroke <<= 1

			s = s[6:]

		return '/'.join(result)

class DctConverter(object):
	def __init__(self,
		dct_filename,
		mdb_export_binary='/usr/bin/mdb-export',
		output_handler=None,
		steno_decoder=None):

		mdb_export = subprocess.Popen(

			[mdb_export_binary,
			dct_filename,
			DICTIONARY_TABLE_NAME],

              		stdout=subprocess.PIPE,
			close_fds=True)

		# FIXME handle error cases:
		#  - dct_filename does not exist
		#  - mdb_export_binary does not exist
		#  - dct_filename is not MDB
		#  - dct_filename does not contain the right table

		self.input_dictionary = csv.reader(mdb_export.stdout)

		self.output_handler = output_handler or OutputRTF()
		self.steno_decoder = steno_decoder or StenoDecoder()


		# FIXME: we need to address the columns by name, not number

		# FIXME: header row handling should be more elegant than this!
		self.input_dictionary.next()

	def translate(self):
		self.output_handler.start()
		for row in self.input_dictionary:
			steno = self.steno_decoder.decode(row[0])
			translation = row[1]

			# FIXME tidy up "translation" (remove macros etc)
			# FIXME we need to honour some flags in row[2] too

			self.output_handler.output(steno, translation)

		self.output_handler.finish()

if __name__=='__main__':
	demo = DctConverter('old/dictionaries/stened.dct')
	demo.translate()
