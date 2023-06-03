"""
Credits and gratitude to the thread and code samples at:
https://forum.omz-software.com/topic/5440/prevent-duplicate-launch-from-shortcut

... also available at:
https://github.com/TPO-POMGOM/Pythonista-utilities.

...for this app_single_launch file, which prevents multiple instances of the same
app being launched in iOS

"""

import gc
import json
from pathlib import Path
import time
from typing import Any

import ui

__all__ = [
    'AppSingleLaunch',
]


DEBUG = False
LOCK_PATH = '~/Documents/single_launch.lock'


def _object_for_id(id_: int) -> Any:
    """ Return an object, given its id. """

    # Do a complete garbage collect, to avoid false positives in case the
    # object was still in use recently. In the context of AppSingleLaunch,
    # this would happen if an app was closed, then launched again immediately.
    gc.collect()
    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj
    return None


class AppSingleLaunch:
    """ Wrapper class for all module functionnality. """

    def __init__(self, app: str):
        """ Initialize an AppSingleLaunch instance.

        Arguments:
        - app: application name, which should be unique (but this is not
        enforced). """
        self.app = app

    def is_active(self) -> bool:
        """ Test if the application is already active.

        Returns:
        - True if the application is already running, in which case the caller
          should do nothing and exit.
        - False if the application is not already running, in which case the
          caller should launch the application in a normal way, and declare its
          main view by calling the will_present() method."""
        if DEBUG:
            print(f"is_active(), app = {self.app}")
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            lock_view = _object_for_id(lock_view_id)
            if DEBUG:
                print("- Lock file =", lock_app, lock_view_id,
                      "valid" if lock_view else "invalid")
            if lock_app == self.app and lock_view:
                if DEBUG:
                    print(f"- App {self.app} already active")
                return True
        if DEBUG:
            print(f"- App {self.app} not active")
        return False

    def will_present(self, view: ui.View) -> None:
        """ Declare that the application is about to present its main view.

        Arguments:
        - view: ui.View instance for the app's main view. """
        if DEBUG:
            print(f"will_present({id(view)}), app = {self.app}")
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            lock_view = _object_for_id(lock_view_id)
            if DEBUG:
                print("- Lock file =", lock_app, lock_view_id,
                      "valid" if lock_view else "invalid")
            if lock_app == self.app and lock_view:
                raise ValueError(f"App {self.app} is already active, cannot "
                                 f"call will_present() against it.")
            else:
                if lock_view and isinstance(lock_view, ui.View):
                    if DEBUG:
                        print(f"- Closing app {lock_app}")
                    lock_view.close()
                    time.sleep(1)  # Required for view to close properly
                # else: lock is a leftover from a previous Pythonista session
                #       and can be safely ignored.
        with open(lock_path, 'w') as lock_file:
            json.dump([self.app, id(view)], lock_file)
        if DEBUG:
            print(f"- Launching app {self.app}\n- Lock file =", self.app, id(view))

    def will_close(self) -> None:
        """ Declare that the application is about to close its main view. """
        lock_path = Path(LOCK_PATH).expanduser()
        if lock_path.exists():
            with open(lock_path) as lock_file:
                (lock_app, lock_view_id) = tuple(json.load(lock_file))
            if lock_app != self.app:
                raise ValueError(f"App {self.app} if not active, "
                                 f"{lock_app} is active")
            lock_path.unlink()
