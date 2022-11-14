from PyQt5.QtCore import QThread
from PyQt5.Qt import pyqtSignal


class DownloadThread(QThread):
    finish_signal = pyqtSignal(object, object, object)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.client = None
        self.track_id = None
        self.path = None

    def run(self):
        print(self.track_id)
        if self.track_id is not None:
            name, author = self.track_info(self.track_id)
            try:
                self.client.tracks_download_info(self.track_id)[0].download(self.path + f'\\{name[:16]} - {author}.mp3')
                print('ok')
            except Exception as err:
                print(err)
        else:
            print('Не указан ID')

    def track_info(self, track_id):
        name = self.client.tracks(track_id)[0]['title']
        author = ' '.join(self.client.tracks(track_id)[0]['artists'][0]['name'].split('/'))
        return name, author
