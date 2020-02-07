import cProfile
from urtext.project import UrtextProject
urtext_project_path = '../archive/nate-big-project'

def make_project():
     project = UrtextProject(urtext_project_path)
cProfile.run('make_project()', sort='time')