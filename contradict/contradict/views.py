from django.shortcuts import render
from .forms import DictionaryUploadForm
from .settings import MEDIA_ROOT
import os
import random
from contradict.formats.DctDict import DctDict
from contradict.formats.JsonDict import JsonDict
from contradict.formats.RtfDict import RtfDict

# this would be better done with introspection
FORMATS = [
		DctDict,
		RtfDict,
		JsonDict,
	]

def _random_filename():
	return os.path.join(
		MEDIA_ROOT,
		''.join(
		[hex(random.randrange(16))[2]
			for i in range(10)])
		)

def _filestore_filename(request):
	return os.path.join(MEDIA_ROOT,
		request.session['our_id'])

def _store_dictionary(f, request):

	dest = open(_filestore_filename(request),
		'wb')

        for chunk in f.chunks():
        	dest.write(chunk)

def _find_format(request):
	fh = open(_filestore_filename(request), 'rb')

	for dformat in FORMATS:
		if dformat().can_handle(fh):
			fh.close()
			return dformat

	fh.close()
	return None

def _handle_upload(request):
	# FIXME: here we scan the file
	# and possibly convert it to json

	# Returns some kind of description of whether it worked!
	# XXX make that less vague

	uploaded_file = request.FILES.get('dictionary')
	file_id = _random_filename()

	request.session['our_id'] = file_id
	request.session['their_name'] = uploaded_file.name
	request.session['dict_size'] = uploaded_file.size

	_store_dictionary(uploaded_file, request)

	# now, what kind of dictionary do we have?
	dformat_class = _find_format(request)

	if dformat_class is None:
		request_vars['unknown-format'] = True
		return

	dformat = dformat_class()

	request.session['format-name'] = dformat.title()

def root_view(request):

	render_vars = {}

	# first off-- are they uploading?

	if request.method=='POST':
		form = DictionaryUploadForm(request.POST,
			request.FILES)

		if form.is_valid():

			# yes, they're uploading.

			_handle_upload(request)
			render_vars['uploaded'] = True

	# now, either they have a file or they don't.
	# if they do, show some information about it.
	# if they don't, they need the upload form.

	if request.session.has_key('our_id') and \
		os.path.exists(_filestore_filename(request)):

			# they HAD a file; we deleted it

			render_vars['deleted'] = request.session['their_name']

			request.session.clear()

	if request.session.has_key('our_id'):

		# they do have a file

		render_vars['our_id'] = request.session['our_id']
		render_vars['their_name'] = request.session['their_name']
	else:

		# they don't have a file;
		# let them upload one

		render_vars['form'] = DictionaryUploadForm()

	for (field, value) in request.session.items():
		if not render_vars.has_key(field):
			render_vars[field] = value

	return render(request, 'root_page.html', render_vars)
