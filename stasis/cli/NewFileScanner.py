import logging
import os
import shutil
import time
import queue
import threading

# hack to import properties
import appconfig

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from stasis.cli import StasisClient, DataformerClient

zipping_q = queue.Queue()
conversion_q = queue.Queue()

stasis_cli = StasisClient("https://dev-api.metabolomics.us")
dataform_cli = DataformerClient("http://phobos.fiehnlab.ucdavis.edu", "9090", "/home/diego/.carrot_storage")


def agilent_worker():
    while True:
        print('agilent_worker looking for something to do...')
        item = zipping_q.get()
        size = 0

        while (os.stat(item).st_size > size):
            time.sleep(5)
            size = os.stat(item).st_size

        # 4. zip file
        compress(item)

        zipping_q.task_done()


def general_worker():
    while True:
        print('general_worker looking for something to do...')
        item = conversion_q.get()

        print("from general worker %s" % item)

        # 5. upload file to converter
        # 6  wait for file conversion to finish
        # 7. store as mzML file
        if (dataform_cli.convert(item, 'mzml')):
            # 8. trigger status converted
            stasis_cli.set_tracking(item, "converted")
        else:
            raise Exception("Error uploading/converting file {item}")

        conversion_q.task_done()


def compress(file):
    """Compresses a folder adding '.zip' to the original name

    Parameters
    ----------
        file : str
            The file/folder to be compressed
    """
    print("compressing file %s..." % file)
    filename, ext = os.path.splitext(file)
    zipped = shutil.make_archive(filename + ext, "zip", filename+ext, file)
    print(f"... zipped {zipped}")

    # 4.5 Add to conversion queue
    conversion_q.put(zipped)


class NewFileScanner(FileSystemEventHandler):
    def on_created(self, event):
        """Called when a file or directory is created.

        Parameters
        ----------
            event : DirCreatedEvent or FileCreatedEvent
                Event representing file/directory creation.
        """

        file = str(event.src_path)

        if (event.is_directory):
            # if it's a .d folder
            if (event.src_path.endswith('.d')):
                print("event %s" % event)
                # 3. trigger status acquired
                stasis_cli.set_tracking(file, "acquired")
                # 3.5 add to zipping queue
                zipping_q.put(event.src_path)
        else:
            # if it's a regular file
            fileName, fileExtension = os.path.splitext(file)

            if (fileExtension.lower() in appconfig.extensions and not '.mzml'):
                print("event %s" % event)
                # 2. wait till the size stays constant
                size = 0
                while (size < os.stat(file).st_size):
                    time.sleep(1)
                    size = os.stat(str(file)).st_size
                    print(size)

                # 3. trigger status acquired
                stasis_cli.set_tracking(file, "acquired")
                # 3.5 add to conversion queue
                conversion_q.put(file)
                print('valid file -> convert')


def monitor(paths):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = NewFileScanner()

    observer = Observer()
    for p in paths:
        print(f'adding path {p} to observer')
        observer.schedule(event_handler, p, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":

    threads = [
        threading.Thread(target=agilent_worker),
        threading.Thread(target=general_worker)
    ]

    for t in threads:
        print(f"starting thread {t}...")
        t.daemon = True
        t.start()

    monitor(appconfig.paths)

    zipping_q.join()
    conversion_q.join()

    for t in threads:
        t.join()
