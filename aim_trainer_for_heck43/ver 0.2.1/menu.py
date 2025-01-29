from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DGG, DirectSlider, DirectCheckButton, DirectOptionMenu
from panda3d.core import TextNode, WindowProperties
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpScaleInterval, LerpPosInterval, Wait
from direct.task import Task

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.frame = None
        self.settings_frame = None
        self.settings_visible = False
        self.menu_buttons = []  # Список для хранения кнопок меню
        
        # Список доступных разрешений
        self.resolutions = [
            "800x600",    # 4:3
            "1024x768",   # 4:3
            "1280x720",   # 16:9 (HD)
            "1366x768",   # 16:9
            "1600x900",   # 16:9
            "1920x1080",  # 16:9 (Full HD)
        ]
        
        # Получаем текущее разрешение из настроек или используем значение по умолчанию
        self.current_resolution = self.game.settings.get('resolution', '1280x720')
        # Если текущее разрешение не в списке, используем значение по умолчанию
        if self.current_resolution not in self.resolutions:
            self.current_resolution = '1280x720'
        
        self.create_menu()
        self.create_settings_menu()
        
    def create_menu(self):
        # Создаем основной фрейм меню
        self.frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            pos=(0, 0, 2)  # Начальная позиция выше экрана для анимации
        )
        
        # Заголовок
        self.title = DirectLabel(
            text="Aim Training",
            scale=0.15,
            pos=(0, 0, 0.4),
            parent=self.frame,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter
        )
        
        # Анимация заголовка
        self.title_animation = Sequence(
            LerpScaleInterval(self.title, 1.0, 0.17),
            LerpScaleInterval(self.title, 1.0, 0.13),
        )
        self.title_animation.loop()
        
        # Кнопка "Play"
        self.play_button = DirectButton(
            text="Play",
            scale=0.07,
            pos=(0, 0, 0.1),
            parent=self.frame,
            command=self.start_game,
            frameColor=(0.2, 0.6, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=DGG.RAISED
        )
        self.menu_buttons.append(self.play_button)
        
        # Кнопка "Settings"
        self.settings_button = DirectButton(
            text="Settings",
            scale=0.07,
            pos=(0, 0, 0),
            parent=self.frame,
            command=self.toggle_settings,
            frameColor=(0.4, 0.4, 0.4, 1),
            text_fg=(1, 1, 1, 1),
            relief=DGG.RAISED
        )
        self.menu_buttons.append(self.settings_button)
        
        # Кнопка "Exit"
        self.exit_button = DirectButton(
            text="Exit",
            scale=0.07,
            pos=(0, 0, -0.1),
            parent=self.frame,
            command=self.exit_game,
            frameColor=(0.6, 0.2, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=DGG.RAISED
        )
        self.menu_buttons.append(self.exit_button)
        
        # Добавляем события при наведении мыши на кнопки
        for button in self.menu_buttons:
            button.bind(DGG.WITHIN, self.button_hover_start, [button])
            button.bind(DGG.WITHOUT, self.button_hover_end, [button])
            button.setTag('original_scale', str(0.07))

    def create_settings_menu(self):
        # Создаем фрейм настроек
        self.settings_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-1, 1, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Создаем notebook для вкладок
        self.notebook = DirectNotebook(
            parent=self.settings_frame,
            pos=(0, 0, 0),
            frameSize=(-0.9, 0.9, -0.7, 0.7),
            frameColor=(0.2, 0.2, 0.2, 1)
        )
        
        # Создаем вкладки
        graphics_tab = DirectTab(
            parent=self.notebook,
            frameSize=(-0.9, 0.9, -0.7, 0.7)  # Устанавливаем размер вкладки
        )
        
        controls_tab = DirectTab(
            parent=self.notebook,
            frameSize=(-0.9, 0.9, -0.7, 0.7)
        )
        
        weapon_tab = DirectTab(
            parent=self.notebook,
            frameSize=(-0.9, 0.9, -0.7, 0.7)
        )
        
        # Добавляем вкладки в notebook
        self.notebook.addPage("Graphics", graphics_tab)
        self.notebook.addPage("Controls", controls_tab)
        self.notebook.addPage("Weapon", weapon_tab)
        
        # Настройки графики
        resolution_label = DirectLabel(
            text="Resolution",
            scale=0.05,
            pos=(-0.3, 0, 0.3),
            parent=graphics_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        # Создаем выпадающий список разрешений
        self.resolution_menu = DirectOptionMenu(
            text_scale=0.5,
            scale=0.07,
            items=self.resolutions,
            initialitem=self.resolutions.index(self.current_resolution),  # Используем индекс текущего разрешения
            command=self.update_resolution,
            pos=(0.1, 0, 0.3),
            parent=graphics_tab,
            frameSize=(-2, 2, -0.5, 1),
            text_fg=(1, 1, 1, 1),
            highlightColor=(0.3, 0.3, 0.3, 1)
        )

        # Добавляем чекбокс для показа изображений
        self.show_images_checkbox = DirectCheckButton(
            text="Show Target Images",
            scale=0.05,
            pos=(-0.3, 0, 0.1),
            command=self.toggle_show_images,
            parent=graphics_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            boxPlacement='right'
        )
        # Устанавливаем начальное состояние чекбокса
        self.show_images_checkbox['indicatorValue'] = self.game.settings.get('show_target_images', True)
        
        # Добавляем чекбокс для FOV
        DirectLabel(
            text="FOV",
            scale=0.05,
            pos=(-0.3, 0, 0.2),
            parent=graphics_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        self.fov_slider = DirectSlider(
            range=(60, 120),
            value=self.game.settings.get('fov', 90),
            pageSize=5,
            command=self.update_fov,
            pos=(0.1, 0, 0.2),
            scale=0.3,
            parent=graphics_tab
        )
        
        # Настройки управления
        DirectLabel(
            text="Mouse Sensitivity",
            scale=0.05,
            pos=(-0.3, 0, 0.5),
            parent=controls_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        self.sensitivity_slider = DirectSlider(
            range=(0.1, 20.0),  # Увеличили максимум с 10.0 до 20.0
            value=self.game.settings.get('sensitivity', self.game.DEFAULT_SETTINGS.get('sensitivity', 1.0)),
            pageSize=0.1,
            command=self.update_sensitivity,
            pos=(0.1, 0, 0.5),
            scale=0.3,
            parent=controls_tab
        )
        
        # Настройки оружия
        DirectLabel(
            text="Position X (Left/Right)",
            scale=0.05,
            pos=(-0.3, 0, 0.5),
            parent=weapon_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        self.x_slider = DirectSlider(
            range=(-1.0, 1.0),
            value=self.game.settings.get('weapon_position_x', self.game.DEFAULT_SETTINGS['weapon_position_x']),
            pageSize=0.1,
            command=self.update_x_position,
            pos=(0.1, 0, 0.5),
            scale=0.3,
            parent=weapon_tab
        )
        
        DirectLabel(
            text="Position Y (Forward/Back)",
            scale=0.05,
            pos=(-0.3, 0, 0.3),
            parent=weapon_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        self.y_slider = DirectSlider(
            range=(0.0, 2.0),
            value=self.game.settings.get('weapon_position_y', self.game.DEFAULT_SETTINGS['weapon_position_y']),
            pageSize=0.1,
            command=self.update_y_position,
            pos=(0.1, 0, 0.3),
            scale=0.3,
            parent=weapon_tab
        )
        
        DirectLabel(
            text="Position Z (Up/Down)",
            scale=0.05,
            pos=(-0.3, 0, 0.1),
            parent=weapon_tab,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1)
        )
        
        self.z_slider = DirectSlider(
            range=(-1.0, 1.0),
            value=self.game.settings.get('weapon_position_z', self.game.DEFAULT_SETTINGS['weapon_position_z']),
            pageSize=0.1,
            command=self.update_z_position,
            pos=(0.1, 0, 0.1),
            scale=0.3,
            parent=weapon_tab
        )
        
        # Reset Button
        DirectButton(
            text="Reset Position",
            text_scale=0.05,
            command=self.reset_position,
            pos=(0, 0, -0.2),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            parent=weapon_tab
        )
        
        # Кнопка "Back"
        self.back_button = DirectButton(
            text="Back",
            scale=0.06,
            pos=(0, 0, -0.6),
            parent=self.settings_frame,
            command=self.toggle_settings,
            frameColor=(0.4, 0.4, 0.4, 1),
            text_fg=(1, 1, 1, 1),
            relief=DGG.RAISED
        )
        
        self.back_button.bind(DGG.WITHIN, self.button_hover_start, [self.back_button])
        self.back_button.bind(DGG.WITHOUT, self.button_hover_end, [self.back_button])
        self.back_button.setTag('original_scale', str(0.06))
        
        # Изначально скрываем меню настроек
        self.settings_frame.hide()
        
    def toggle_settings(self):
        """Переключает видимость меню настроек"""
        if not self.settings_visible:
            # Показываем настройки
            self.settings_frame.show()
            self.settings_visible = True
            # Скрываем и отключаем основное меню
            for button in self.menu_buttons:
                button['state'] = DGG.DISABLED
                button.hide()
        else:
            # Скрываем настройки
            self.settings_frame.hide()
            self.settings_visible = False
            # Показываем и включаем основное меню
            for button in self.menu_buttons:
                button['state'] = DGG.NORMAL
                button.show()
            # Сохраняем настройки при закрытии меню
            self.game.save_settings()

    def update_sensitivity(self):
        """Обновляет чувствительность мыши"""
        value = round(self.sensitivity_slider['value'], 2)
        self.game.settings['sensitivity'] = value
        self.game.update_mouse_sensitivity()  # Обновляем чувствительность мыши

    def update_resolution(self, resolution):
        """Обновляет разрешение экрана"""
        if resolution in self.resolutions:
            width, height = map(int, resolution.split('x'))
            # Сохраняем разрешение в настройках
            self.game.settings['resolution'] = resolution
            self.game.save_settings()
            # Применяем новое разрешение
            wp = WindowProperties()
            wp.setSize(width, height)
            base.win.requestProperties(wp)

    def toggle_score(self, status):
        self.game.show_score = status
        self.game.apply_settings({'show_score': status})

    def toggle_timer(self, status):
        self.game.show_timer = status
        self.game.apply_settings({'show_timer': status})

    def toggle_show_images(self, status):
        self.game.settings['show_target_images'] = status
        self.game.save_settings()
        # Обновляем видимость всех существующих манекенов
        if hasattr(self.game, 'targets'):
            for target in self.game.targets:
                target.update_visibility()

    def update_fov(self):
        new_fov = int(self.fov_slider['value'])
        self.game.apply_settings({'fov': new_fov})
        
    def update_x_position(self):
        value = round(self.x_slider['value'], 2)
        self.game.settings['weapon_position_x'] = value
        messenger.send('update_weapon_position')
        
    def update_y_position(self):
        value = round(self.y_slider['value'], 2)
        self.game.settings['weapon_position_y'] = value
        messenger.send('update_weapon_position')
        
    def update_z_position(self):
        value = round(self.z_slider['value'], 2)
        self.game.settings['weapon_position_z'] = value
        messenger.send('update_weapon_position')
        
    def reset_position(self):
        self.x_slider['value'] = self.game.DEFAULT_SETTINGS['weapon_position_x']
        self.y_slider['value'] = self.game.DEFAULT_SETTINGS['weapon_position_y']
        self.z_slider['value'] = self.game.DEFAULT_SETTINGS['weapon_position_z']
        self.game.settings['weapon_position_x'] = self.game.DEFAULT_SETTINGS['weapon_position_x']
        self.game.settings['weapon_position_y'] = self.game.DEFAULT_SETTINGS['weapon_position_y']
        self.game.settings['weapon_position_z'] = self.game.DEFAULT_SETTINGS['weapon_position_z']
        messenger.send('update_weapon_position')
        
    def button_hover_start(self, button, event):
        # Увеличиваем кнопку при наведении
        original_scale = float(button.getTag('original_scale'))
        Sequence(
            LerpScaleInterval(button, 0.1, original_scale * 1.2)
        ).start()
        
    def button_hover_end(self, button, event):
        # Возвращаем оригинальный размер кнопки
        original_scale = float(button.getTag('original_scale'))
        Sequence(
            LerpScaleInterval(button, 0.1, original_scale)
        ).start()
        
    def show(self):
        self.frame.show()
        # Показываем курсор мыши в меню
        props = WindowProperties()
        props.setCursorHidden(False)
        self.game.win.requestProperties(props)
        
        # Анимация появления меню
        Sequence(
            LerpPosInterval(self.frame, 0.5, (0, 0, 0), (0, 0, 2), blendType='easeOut')
        ).start()
        
    def hide(self):
        # Анимация исчезновения меню
        hide_sequence = Sequence(
            LerpPosInterval(self.frame, 0.3, (0, 0, -2), (0, 0, 0), blendType='easeIn'),
            Wait(0.3)  # Ждем окончания анимации
        )
        hide_sequence.start()
        
        # Останавливаем анимацию заголовка
        self.title_animation.pause()
        
    def start_game(self):
        self.hide()
        # Запускаем игру после окончания анимации
        taskMgr.doMethodLater(0.3, self._start_game_delayed, 'start_game_delayed')
        
    def _start_game_delayed(self, task):
        self.frame.hide()
        self.game.start_game()
        return task.done
        
    def exit_game(self):
        self.game.userExit()
        
    def cleanup(self):
        if self.frame:
            # Останавливаем все анимации
            self.title_animation.pause()
            self.frame.destroy()
            
class DirectTab(DirectFrame):
    def __init__(self, parent=None, **kw):
        # Определяем опции по умолчанию
        optiondefs = (
            ('relief', None, None),
            ('frameColor', (0, 0, 0, 0), None),
        )
        # Объединяем пользовательские опции с опциями по умолчанию
        self.defineoptions(kw, optiondefs)
        # Вызываем конструктор родительского класса
        DirectFrame.__init__(self, parent)
        # Инициализируем опции
        self.initialiseoptions(DirectTab)

class DirectNotebook(DirectFrame):
    def __init__(self, parent=None, **kw):
        # Определяем опции по умолчанию
        optiondefs = (
            ('relief', DGG.SUNKEN, None),
            ('frameColor', (0.8, 0.8, 0.8, 1), None),
        )
        # Объединяем пользовательские опции с опциями по умолчанию
        self.defineoptions(kw, optiondefs)
        # Вызываем конструктор родительского класса
        DirectFrame.__init__(self, parent)
        # Инициализируем опции
        self.initialiseoptions(DirectNotebook)
        
        self.tabs = []
        self.pages = []
        self.current_page = None
        
        # Создаем фрейм для кнопок вкладок
        self.tab_frame = DirectFrame(
            parent=self,
            pos=(0, 0, self['frameSize'][3]),
            frameSize=(self['frameSize'][0], self['frameSize'][1], 0, 0.1),
            frameColor=(0.7, 0.7, 0.7, 1)
        )
        
    def addPage(self, text, page):
        index = len(self.tabs)
        tab_width = 0.2
        
        # Создаем кнопку вкладки
        tab = DirectButton(
            parent=self.tab_frame,
            text=text,
            text_scale=0.04,
            frameSize=(-tab_width/2, tab_width/2, -0.05, 0.05),
            pos=(index * tab_width - self['frameSize'][1]/2 + tab_width/2, 0, 0),
            command=self.selectPage,
            extraArgs=[index],
            relief=DGG.RAISED,
            frameColor=(0.6, 0.6, 0.6, 1) if not self.tabs else (0.4, 0.4, 0.4, 1)
        )
        
        self.tabs.append(tab)
        self.pages.append(page)
        
        # Если это первая страница, показываем ее
        if not self.current_page:
            page.show()
            self.current_page = page
        else:
            page.hide()
            
    def selectPage(self, index):
        # Скрываем текущую страницу
        if self.current_page:
            self.current_page.hide()
        
        # Обновляем цвета вкладок
        for i, tab in enumerate(self.tabs):
            if i == index:
                tab['frameColor'] = (0.6, 0.6, 0.6, 1)
            else:
                tab['frameColor'] = (0.4, 0.4, 0.4, 1)
        
        # Показываем выбранную страницу
        self.pages[index].show()
        self.current_page = self.pages[index]
