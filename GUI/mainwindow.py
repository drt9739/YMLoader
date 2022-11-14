import asyncio
import requests
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from functools import partial
from Scripts.thread import *
from Scripts.files import *
from Scripts.pages import *
from yandex_music import Client
from Scripts.files import icon_status


class MainWindow(QMainWindow):
    def __init__(self, token: str, path_download: str, path_icon: str):
        """
        Инициализация главного окна
        :param token: str -> для создания объекта yandex_music.Client
        :param path_download: str -> путь до папки, куда будет скачиваться музыка
        :param path_icon: str -> путь до папки, куда будут сохранятся иконки треков
        """
        super().__init__()
        self.row, self.column = 1, 0
        self.flag = False

        if token is not None:
            self.client = Client(token)
        else:
            self.flag = True
        self.pathD, self.pathI = path_download, path_icon

        self.page = 1
        self.pagesTracks = []

        uic.loadUi('GUI/main.ui', self)
        self.threadDownload = DownloadThread(self)
        self.load_ui()

    def load_ui(self):
        """
        Загрузка UI и присвоение кнопкам функций
        :return: None
        """

        self.rightchev.clicked.connect(self.next_page)
        self.leftchev.clicked.connect(self.previous_page)
        self.rightchevs.clicked.connect(self.last_page)
        self.lefichevs.clicked.connect(self.first_page)
        self.settingbtn.clicked.connect(self.setting_window)
        self.searchbtn.clicked.connect(self.search)

        data = all_playlist()
        playlists = [self.create_playlist(el) for el in data]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(playlists))

    async def create_playlist(self, playlist_id: int):
        """
        Создание плейлиста
        :param playlist_id: int
        :return: None
        """

        self.create_obj_playlist()

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap('GUI/Icons/play-circle.svg'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.showtrack.setIcon(icon1)
        self.iconplaylist.setPixmap(QPixmap(os.path.abspath('GUI') + f'\\Icons\\{playlist_id}.jpg'))

        # Имена Объектов

        self.playlist1.setObjectName(str(playlist_id))
        self.nameplaylist.setObjectName("name_playlist" + str(playlist_id))
        self.iconplaylist.setObjectName("icon_playlist" + str(playlist_id))
        self.showtrack.setObjectName("show_track" + str(playlist_id))

        self.showtrack.clicked.connect(partial(self.open_playlist, playlist_id))

        self.showtrack.setIconSize(QtCore.QSize(44, 44))

        self.gridLayout.addWidget(self.playlist1, 0, self.column, 1, 1)

        # Надписи

        _translate = QtCore.QCoreApplication.translate
        self.nameplaylist.setText(_translate("MainWindow", playlist_name(playlist_id)))

        self.column += 1

    def create_obj_playlist(self):
        """
        Создаёт все нужные объекты для фрейма плейлиста
        :return: None
        """
        self.playlist1 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playlist1.sizePolicy().hasHeightForWidth())
        self.playlist1.setSizePolicy(sizePolicy)
        self.playlist1.setMinimumSize(QtCore.QSize(170, 170))
        self.playlist1.setMaximumSize(QtCore.QSize(170, 170))
        self.playlist1.setStyleSheet("QFrame{background-color: rgba(206, 206, 206, 100);border-radius:10px}\n"
                                     "QFrame:hover{background-color: rgba(230,230,230, 100)}")

        self.playlist1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playlist1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.iconplaylist = QtWidgets.QLabel(self.playlist1)
        self.iconplaylist.setGeometry(QtCore.QRect(25, 5, 120, 120))
        self.iconplaylist.setMinimumSize(QtCore.QSize(120, 120))
        self.iconplaylist.setMaximumSize(QtCore.QSize(120, 120))
        self.iconplaylist.setText("")

        self.iconplaylist.setScaledContents(True)

        self.nameplaylist = QtWidgets.QLabel(self.playlist1)
        self.nameplaylist.setGeometry(QtCore.QRect(0, 125, 171, 51))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light Condensed")
        font.setPointSize(10)
        self.nameplaylist.setFont(font)
        self.nameplaylist.setStyleSheet("background-color:None;\ncolor: #fff;")
        self.nameplaylist.setAlignment(QtCore.Qt.AlignCenter)
        self.nameplaylist.setWordWrap(True)

        self.showtrack = QtWidgets.QPushButton(self.playlist1)
        self.showtrack.setGeometry(QtCore.QRect(113, 81, 51, 51))
        self.showtrack.setStyleSheet("QPushButton{border-radius:25px;}\n"
                                     "QPushButton:hover{background-color: rgb(199, 199, 199)}\n"
                                     "QPushButton:pressed{background-color:rgba(255, 255, 255, 100)}\n")
        self.showtrack.setText("")

    async def create_track(self, track_id: int):
        """
        Создание трека
        :param track_id:  int
        :return: None
        """

        await self.create_obj_tracks()
        data = icon_status()

        if self.flag is not True:
            name, author = await self.track_info(track_id)
        else:
            name, author = sql_select('name, author', 'track', f'id = {track_id}')[0]

        if track_id in data:
            self.icon.setPixmap(QtGui.QPixmap(f"TrackIcons/{track_id}.jpg"))

        elif track_id not in data and self.flag is not True:
            self.client.tracks(track_id)[0].download_cover(f'{self.pathI}\\{track_id}.jpg')
            self.icon.setPixmap(QtGui.QPixmap(f"TrackIcons/{track_id}.jpg"))

            await sql_insert('track', (track_id, name, author, 0, 1, self.client.tracks(track_id)[0]['duration_ms']))

        else:
            self.icon.setPixmap(QtGui.QPixmap('TrackIcons/offline.jpg'))

        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.gridLayout_2.addWidget(self.track, self.row, 0, 1, 1)

        self.btndownload.clicked.connect(partial(self.download, track_id))

        duration_ms = sql_select('duration_ms', 'track', f'id = {track_id}')[0][0]
        second = (duration_ms // 1000) % 60

        if second >= 10:
            duration = str((duration_ms // 1000) // 60) + ':' + str(second)
        else:
            duration = str((duration_ms // 1000) // 60) + ':0' + str(second)

        _translate = QtCore.QCoreApplication.translate
        self.name.setText(_translate("MainWindow", name if len(name) <= 25 else name[:25].strip() + '...'))
        self.author.setText(_translate("MainWindow", author))
        self.duration.setText(_translate("MainWindow", duration))

        self.row += 1

    async def create_obj_tracks(self):
        """
        Создаёт все нужные объекты для фрейма трека
        :return: None
        """
        self.track = QtWidgets.QFrame(self.scrollAreaWidgetContents)

        self.track.setMinimumSize(QtCore.QSize(100, 70))
        self.track.setMaximumSize(QtCore.QSize(580, 70))
        self.track.setStyleSheet("QFrame{background-color: rgba(59, 59, 59, 200);;\n"
                                 "border-radius: 15px;\n"
                                 "color: rgb(255,255,255);\n"
                                 "border:1px solid rgb(255, 255, 255)}\n"
                                 "QFrame:hover{background-color: rgba(98, 98, 98, 100)}\n")
        self.track.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.track.setFrameShadow(QtWidgets.QFrame.Raised)
        self.track.setObjectName("track")
        self.name = QtWidgets.QLabel(self.track)
        self.name.setGeometry(QtCore.QRect(77, -3, 391, 41))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light Condensed")
        font.setPointSize(19)
        self.name.setFont(font)
        self.name.setStyleSheet("border:None;\n"
                                "background-color: rgba(255, 255, 255, 0);")
        self.name.setObjectName("name")
        self.author = QtWidgets.QLabel(self.track)
        self.author.setGeometry(QtCore.QRect(77, 30, 391, 41))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light Condensed")
        font.setPointSize(13)
        self.author.setFont(font)
        self.author.setStyleSheet("border:None;\n"
                                  "background-color: rgba(255, 255, 255, 0);")
        self.author.setObjectName("author")
        self.btndownload = QtWidgets.QPushButton(self.track)
        self.btndownload.setGeometry(QtCore.QRect(512, 10, 50, 50))
        self.btndownload.setStyleSheet("QPushButton{border:3px solid rgb(255, 255, 255);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgba(0,0,0,0)}\n"
                                       "QPushButton:hover{background-color:rgba(229, 229, 229, 100)}\n"
                                       "QPushButton:pressed{background-color:rgba(100, 98, 98, 240)}\n")
        self.btndownload.setText("")

        self.btndownload.setIconSize(QtCore.QSize(44, 44))
        self.btndownload.setObjectName("btn_download")
        self.icon = QtWidgets.QLabel(self.track)
        self.icon.setGeometry(QtCore.QRect(12, 5, 60, 60))
        self.icon.setStyleSheet("border:None;\n")
        self.icon.setText("")
        self.duration = QtWidgets.QLabel(self.track)
        self.duration.setGeometry(QtCore.QRect(430, 13, 71, 41))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light Condensed")
        font.setPointSize(15)
        self.duration.setFont(font)
        self.duration.setStyleSheet("border:None;\n"
                                    "background-color: rgba(255, 255, 255, 0);")
        self.duration.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.duration.setObjectName("duration")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI/Icons/download.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btndownload.setIcon(icon)

    def open_playlist(self, playlist_id: int):
        """
        Открытие треков из представленных плейлистов
        :param playlist_id: int
        :return: None
        """

        self.clear_track_frame()
        self.page = 1
        self.list.setText(str(self.page))
        if self.flag is not True:
            if playlist_id == 1:
                tracks = list(map(lambda x: int(x['id']), self.client.users_likes_tracks()))
                self.pagesTracks = get_pages(tracks)
                tracks = [self.create_track(el) for el in tracks[:15]]

                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tracks))

            elif playlist_id == 2:
                tracks = list(map(lambda x: x['id'], self.client.chart()['chart']['tracks']))
                self.pagesTracks = get_pages(tracks)

                tracks = [self.create_track(el) for el in tracks[:15]]

                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tracks))

            elif playlist_id == 3:
                tracks = list(map(lambda x: x['id'], self.client.feed()['generated_playlists'][0]['data']['tracks']))
                self.pagesTracks = get_pages(tracks)
                tracks = [self.create_track(el) for el in tracks[:15]]

                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tracks))

            elif playlist_id == 4:
                tracks = list(map(lambda x: x['id'], self.client.feed()['generated_playlists'][1]['data']['tracks']))
                self.pagesTracks = get_pages(tracks)

                tracks = [self.create_track(el) for el in tracks[:15]]

                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tracks))

            elif playlist_id == 5:
                tracks = list(map(lambda x: x['id'], self.client.feed()['generated_playlists'][2]['data']['tracks']))
                self.pagesTracks = get_pages(tracks)

                tracks = [self.create_track(el) for el in tracks[:15]]

                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка бро")
            msg.setText("Прости бро, сегодня без музыки.\nТы забыл авторизоваться в свой аккаунт")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def clear_track_frame(self):
        """
        Очищает все треки
        :return: None
        """
        children = self.scrollAreaWidgetContents.findChildren(QtWidgets.QFrame)
        for frame in children:
            self.gridLayout_2.removeWidget(frame)
        self.row = 0

    async def track_info(self, track_id: int):
        """
        Функция для получения информации о треке
        :param track_id: int
        :return: None
        """
        name = self.client.tracks(track_id)[0]['title']
        try:
            author = ' '.join(self.client.tracks(track_id)[0]['artists'][0]['name'].split('/'))
        except IndexError:
            author = ' '.join(self.client.tracks(track_id)[0]['albums'][0]['title'].split('/'))
        return name, author

    def download(self, track_id):
        """
        Для скачивания трека на устройство в формате .mp3
        :param track_id: int
        :return: None
        """
        self.threadDownload.track_id = track_id
        self.threadDownload.path = self.pathD
        self.threadDownload.client = self.client
        self.threadDownload.start()

    def next_page(self):
        """
        Следующая страница треков
        :return: None
        """
        if self.page < len(self.pagesTracks):
            self.clear_track_frame()
            self.page += 1
            self.list.setText(str(self.page))
            tracks = [self.create_track(el) for el in self.pagesTracks[self.page - 1]]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Конец!")
            msg.setText("Достигнут конец конца")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def previous_page(self):
        """
        Прошла страница треков
        :return: None
        """
        if self.page > 1:
            self.clear_track_frame()
            self.page -= 1
            self.list.setText(str(self.page))
            tracks = [self.create_track(el) for el in self.pagesTracks[self.page - 1]]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Конец!")
            msg.setText("Достигнуто начало конца")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def last_page(self):
        """
        Последняя страница треков
        :return: None
        """
        if self.page < len(self.pagesTracks):
            self.clear_track_frame()
            self.page = len(self.pagesTracks)
            self.list.setText(str(self.page))
            tracks = [self.create_track(el) for el in self.pagesTracks[self.page - 1]]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Конец!")
            msg.setText("Достигнут конец конца")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def first_page(self):
        """
        Первая страница треков
        :return: None
        """
        if self.page > 1:
            self.clear_track_frame()
            self.page = 1
            self.list.setText(str(self.page))
            tracks = [self.create_track(el) for el in self.pagesTracks[0]]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Конец!")
            msg.setText("Достигнуто начало конца")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def setting_window(self):
        """
        Открывает окно с настройками
        :return: None
        """
        self.settings = SettingWindow(self, self.pathD, self.pathI)
        self.settings.show()

    def search(self):
        """
        Поиск треков по названию
        :return: None
        """
        self.clear_track_frame()
        text = self.lineEdit.text()
        if self.flag is not True:
            result = list(map(lambda x: x['id'], self.client.search(text, type_='track')["tracks"]['results'] +
                              self.client.search(text, type_='track', page=1)["tracks"]['results']))
            pages = get_pages(result)
            self.page = 1
            self.list.setText(str(self.page))
            self.pagesTracks = pages

            tracks = [self.create_track(el) for el in self.pagesTracks[0]]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tracks))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка!")
            msg.setText(f"Это действие не возможно сделать в оффлайн режиме")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()


class SettingWindow(QMainWindow):
    def __init__(self, other, path_download: str, path_icon: str):
        """
        Инициализация окна настроек
        :param other: class(QMainWindow)
        :param path_download: str
        :param path_icon: str
        """
        super().__init__()
        self.path_download = path_download.replace('\\', '/')
        self.path_icon = path_icon.replace('\\', '/')
        self.other = other

        uic.loadUi('GUI/settings.ui', self)
        self.load_ui()

    def load_ui(self):
        """
        Создания UI
        :return: None
        """
        self.check_token()

        self.pathdownload.setText(self.path_download)
        self.pathicon.setText(self.path_icon)

        state = load_json('config.txt')['custom_path']
        self.checkBox.setChecked(state)
        self.opendownloadbtn.setEnabled(state)
        self.openiconbtn.setEnabled(state)

        self.checkBox.stateChanged.connect(self.checkbox_state)
        self.opendownloadbtn.clicked.connect(self.open_download)
        self.openiconbtn.clicked.connect(self.open_icon)
        self.loginbtn.clicked.connect(self.login_to_account)
        self.logoutbtn.clicked.connect(self.logout)

    def check_token(self):
        """
        Проверка авторизован ли пользователь или нет
        :return: None
        """
        token = load_json('config.txt')['token']
        if token is not None:
            client = Client(token)
            self.other.client = client
            name = ' '.join(client.accountStatus()['account']['display_name'].split()[1:])
            self.label_5.setText(f'{name}, здравствуйте 👋\nВы уже успешно залогинены в аккаунт')
        else:
            self.label_5.setText('Пользователь не залогинен или токен не действителен')

    def checkbox_state(self):
        """
        Изменение параметра кастомный путь
        :return: None
        """
        if self.checkBox.isChecked():
            self.opendownloadbtn.setEnabled(True)
            self.openiconbtn.setEnabled(True)

            config = load_json('config.txt')
            config['custom_path'] = True
            save_json('config.txt', config)
        else:
            self.opendownloadbtn.setEnabled(False)
            self.openiconbtn.setEnabled(False)

            config = load_json('config.txt')
            config['custom_path'] = False
            save_json('config.txt', config)

    def open_download(self):
        """
        Открытие диалога для изменения пути скачивания треков
        :return: None
        """
        path = str(QFileDialog.getExistingDirectory(self, 'Выберите директорию для скачивания музыка'))
        if path != '' and os.path.exists(path):
            self.pathdownload.setText(path)
            self.other.pathD = os.path.abspath(path)

    def open_icon(self):
        """
        Открытие диалога для изменения пути скачивания обложек треков
        :return: None
        """
        path = str(QFileDialog.getExistingDirectory(self, 'Выберите директорию для скачивания обложек треков'))
        if path != '' and os.path.exists(path):
            self.pathicon.setText(path)
            self.other.pathI = os.path.abspath(path)

    def login_to_account(self):
        """
        Авторизация в аккаунт яндекс музыки
        :return: None
        """
        data = {
            "grant_type": "password",
            "username": self.login.text(),
            "password": self.password.text(),
            'client_secret': '53bc75238f0c4d08a118e51fe9203300',
            'client_id': '23cabbbdc6cd418abb4b39c32c41195d'
        }
        if self.login.text() != '' or self.password.text() != '':
            try:
                token = eval(requests.post('https://oauth.mobile.yandex.net/1/token', data=data).text)['access_token']
                config = load_json('config.txt')
                config['token'] = token
                save_json('config.txt', config)
                self.login.setText('')
                self.password.setText('')

            except KeyError as err:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка!")
                msg.setText(f"Вы ввели не правильный логин или пароль ")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка!")
            msg.setText(f"Вы не ввели логин/пароль ")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

        self.check_token()

    def logout(self):
        """
        Выход из аккаунта яндекс музыки
        :return: None
        """
        config = load_json('config.txt')
        config['token'] = None
        save_json('config.txt', config)
        self.label_5.setText('Вы успешно вышли из аккаунта')
        self.other.flag = False
