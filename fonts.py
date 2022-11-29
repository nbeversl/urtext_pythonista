from objc_util import ObjCClass

fonts = {
	'Fira Code': ObjCClass('UIFont').fontWithName_size_('Fira Code', 12),
	'FiraCode-Bold': ObjCClass('UIFont').fontWithName_size_('FiraCode-Bold', 12)
}
