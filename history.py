def browse_history(self, sender):
	self.take_snapshot()
	self.current_file_history = self._UrtextProjectList.current_project.get_history(self.current_open_file)
	if not self.current_file_history:
		return None
	ts_format = self._UrtextProjectList.current_project.settings['timestamp_format']
	string_timestamps = [
		datetime.datetime.fromtimestamp(
			int(i)).strftime(ts_format) for i in sorted(
				self.current_file_history.keys(), reverse=True
				)]
	self.history_stamps.items = string_timestamps
	self.tv.end_editing()
	self.size_field(self.history_view)
	self.history_view.height = 160     # 4 cels high
	self.history_view.hidden = False
	self.history_view.bring_to_front()

# class HistoryView(object):

# 	def tableview_did_select(self, tableview, section, row):
# 		state = main_view._UrtextProjectList.current_project.apply_patches(main_view.current_file_history, distance_back=row)
# 		main_view.updating_history = True
# 		main_view.tv.text = state
# 		on_main_thread(syntax_highlighter.setAttribs, main_view.tv, main_view.tvo)
# 		main_view.updating_history = False