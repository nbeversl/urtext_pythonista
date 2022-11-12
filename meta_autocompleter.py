from auto_completer import AutoCompleter

class MetaAutoCompleter(AutoCompleter):
	""" Used for searching project meta key/value pairs """


	def process_textfield(self):

		entry = self.textfield.text.lower()
		meta_pairs = self.main_view._UrtextProjectList.get_all_meta_pairs()
		options = sorted(
			meta_pairs, 
			key=lambda pair: fuzz.ratio(entry, pair), 
			reverse=True)

		# setting the items property automatically updates the list
		self.items = options

