import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileScanner(FileSystemEventHandler):

    def on_created(self, event):
        """Called when a file or directory is created.

        :param event:
            Event representing file/directory creation.
        :type event:
            :class:`DirCreatedEvent` or :class:`FileCreatedEvent`
        """

        # if ends with .d
        # 1. make sure it's a directory
        # 2. wait till the size stays constant of it and all it's file
        # 3. trigger status acquired
        # 4. zip file
        # 5. upload file to converter
        # 6  wait for file conversion to finish
        # 7. store as mzML file
        # 8. trigger status converted

        print(event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = NewFileScanner()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
