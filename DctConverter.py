import subprocess
import os.path
import csv

DICTIONARY_TABLE_NAME = 'dictionary'

class OutputRTF(object):
	# this does not yet output RTF; it's a stub
	def output(self, steno, translation):
		print '>', steno, '>', translation

class StenoDecoder(object):
	def __init__(self,
		# FIXME: what is the leftmost char,
		# and what should we do if it occurs?
		keys = '?#STKPWHRAO*EUFRPBLGTSDZ',
		):

		self.keys = keys

	def decode(self, s):
		result = []

		# FIXME add hyphen
		# FIXME error handling

		while s:
			result.append('')
			stroke = int(s[:6], 16)

			for i in self.keys:
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
		for row in self.input_dictionary:
			steno = self.steno_decoder.decode(row[0])
			translation = row[1]

			self.output_handler.output(steno, translation)

if __name__=='__main__':
	demo = DctConverter('old/dictionaries/stened.dct')
	demo.translate()
