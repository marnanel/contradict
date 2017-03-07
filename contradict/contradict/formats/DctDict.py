from contradict.formats.StenoDict import StenoDict

import subprocess
import os.path
import csv
import sys
from contradict.settings import MDB_EXPORT_BINARY

DICTIONARY_TABLE_NAME = 'dictionwary'
DICTIONARY_TABLE_COLUMNS = 'Steno,English,Flags,Date,TranCount,LastEditedDate'

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

KEYS = '?#STKPWHRAO*EU-FRPBLGTSDZ'

def _decode_steno(encoded, keys = KEYS):

	result = []

	# FIXME error handling

	while encoded:
		result.append('')
		stroke = int(encoded[:6], 16)

		needs_hyphen = (stroke & RIGHT_HAND) and not (stroke & VOWELS)

		for i in keys:
			if i=='-':
				if needs_hyphen:
					result[-1] += '-'
			else:
				if stroke & 0x800000:
					result[-1] += i
				stroke <<= 1

		encoded = encoded[6:]

	return '/'.join(result)

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

		mdb_export = subprocess.Popen(

			[MDB_EXPORT_BINARY,
			filename,
			DICTIONARY_TABLE_NAME],

			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			close_fds=True)

		# FIXME handle error cases:
		#  - mdb_export_binary does not exist
		#  - filename does not contain the right table

		first_line = mdb_export.stdout.readline().strip()

		if first_line != DICTIONARY_TABLE_COLUMNS:
			mdb_export.kill()
			raise ValueError("The dictionary was not in the expected format.")

		input_dictionary = csv.reader(mdb_export.stdout)

		# FIXME: header row handling should be more elegant than this!
		input_dictionary.next()

		result = {}

		for row in input_dictionary:
			steno = _decode_steno(row[0])
			translation = row[1]

			# FIXME tidy up "translation" (remove macros etc)
			# FIXME we need to honour some flags in row[2] too

			result[steno] = translation

		return result

	@classmethod
	def can_save_to_file(cls):
		return False

	@classmethod
	def save_to_file(cls, filename):
		raise ValueError("Can't write to .dct dictionaries")
