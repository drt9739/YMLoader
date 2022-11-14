import os
import sys

from Scripts.files import *
from PyQt5.QtWidgets import QApplication
from GUI.mainwindow import MainWindow


def main():
    path = load_json('path.json')
    config = load_json('config.txt')
    # Абсолютный(не кастомный) путь для скачивания
    if config['custom_path'] is not True or os.path.exists(
            path['download']) is not True or os.path.exists(path['track_icons']):

        if path['download'] != os.path.abspath('Downloads'):
            path['download'] = os.path.abspath('Downloads')

        if path['track_icons'] != os.path.abspath('TrackIcons'):
            path['track_icons'] = os.path.abspath('TrackIcons')

        save_json('path.json', path)
        config['custom_path'] = False
        save_json('config.txt', config)

    # Установка постоянных переменных

    DOWNLOAD = path['download']
    TRACKICONS = path['track_icons']
    TOKEN = load_json('config.txt')['token']

    app = QApplication(sys.argv)
    ex = MainWindow(TOKEN, DOWNLOAD, TRACKICONS)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
