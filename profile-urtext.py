from urtext.project import UrtextProject
import cProfile

pr = cProfile.Profile()
pr.enable()

#r = UrtextProject('/Users/nathanielbeversluis/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive/docs')
r = UrtextProject('/Users/n_beversluis/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive/nate-big-project')

pr.disable()
pr.print_stats(sort='time')

print('COMPILING')
pr.enable()
r._compile()
pr.disable()
pr.print_stats(sort='time')



