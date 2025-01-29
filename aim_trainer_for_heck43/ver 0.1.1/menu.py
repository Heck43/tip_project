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
        
        # Список доступных разрешений
        self.resolutions = [
            "800x600",    # 4:3
            "1024x768",   # 4:3
            "1280x720",   # 16:9 (HD)
            "1366x768",   # 16:9
            "1600x900",   # 16:9
            "1920x1080",  # 16:9 (Full HD)
            "2560x1440"   # 16:9 (2K)
        ]
        self.current_resolution = 2  # По умолчанию 1280x720
        
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
        
        # Добавляем события при наведении мыши на кнопки
        for button in [self.play_button, self.settings_button, self.exit_button]:
            button.bind(DGG.WITHIN, self.button_hover_start, [button])
            button.bind(DGG.WITHOUT, self.button_hover_end, [button])
            button.setTag('original_scale', str(0.07))

    def create_settings_menu(self):
        # Создаем фрейм настроек
        self.settings_frame = DirectFrame(
            frameColor=(0.15, 0.15, 0.15, 0.9),
            frameSize=(-0.6, 0.6, -0.6, 0.6),
            pos=(2, 0, 0),  # Начальная позиция справа от экрана
            parent=self.frame
        )
        
        # Заголовок настроек
        self.settings_title = DirectLabel(
            text="Settings",
            scale=0.1,
            pos=(0, 0, 0.45),
            parent=self.settings_frame,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter
        )
        
        # Настройка разрешения экрана
        self.resolution_label = DirectLabel(
            text="Resolution",
            scale=0.06,
            pos=(-0.4, 0, 0.3),
            parent=self.settings_frame,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft
        )
        
        # Создаем выпадающий список для разрешений
        self.resolution_menu = DirectOptionMenu(
            text="Resolution",
            scale=0.06,
            pos=(0.1, 0, 0.3),
            items=self.resolutions,
            initialitem=self.current_resolution,
            highlightColor=(0.65, 0.65, 0.65, 1),
            parent=self.settings_frame,
            command=self.update_resolution,
            text_fg=(1, 1, 1, 1),
            text_scale=0.8,
            frameSize=(-0.6, 2.0, -0.5, 0.5),
            popupMarker_scale=0.8
        )
        
        # Настройка чувствительности мыши
        self.sensitivity_label = DirectLabel(
            text="Mouse Sensitivity",
            scale=0.06,
            pos=(-0.4, 0, 0.15),
            parent=self.settings_frame,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft
        )
        
        self.sensitivity_slider = DirectSlider(
            range=(5.0, 30.0),
            value=15.0,
            pageSize=1.0,
            scale=0.4,
            pos=(0.1, 0, 0.15),
            parent=self.settings_frame,
            command=self.update_sensitivity
        )
        
        # Показывать счет
        self.show_score = DirectCheckButton(
            text="Show Score",
            scale=0.06,
            pos=(-0.2, 0, 0),
            parent=self.settings_frame,
            command=self.toggle_score,
            text_fg=(1, 1, 1, 1),
            boxPlacement="right"
        )
        
        # Показывать время
        self.show_timer = DirectCheckButton(
            text="Show Timer",
            scale=0.06,
            pos=(-0.2, 0, -0.15),
            parent=self.settings_frame,
            command=self.toggle_timer,
            text_fg=(1, 1, 1, 1),
            boxPlacement="right"
        )
        
        # Кнопка "Back"
        self.back_button = DirectButton(
            text="Back",
            scale=0.06,
            pos=(0, 0, -0.4),
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
        if not self.settings_visible:
            # Показываем меню настроек с анимацией
            self.settings_frame.show()
            Sequence(
                LerpPosInterval(self.settings_frame, 0.3, (0, 0, 0), (2, 0, 0), blendType='easeOut')
            ).start()
        else:
            # Скрываем меню настроек с анимацией
            Sequence(
                LerpPosInterval(self.settings_frame, 0.3, (2, 0, 0), (0, 0, 0), blendType='easeIn'),
                Wait(0.3)
            ).start()
            taskMgr.doMethodLater(0.3, lambda task: self.settings_frame.hide(), 'hide_settings')
            
        self.settings_visible = not self.settings_visible
        
    def update_sensitivity(self):
        sensitivity = self.sensitivity_slider['value']
        # Обновляем чувствительность мыши в игре
        self.game.mouse_sensitivity = sensitivity
        
    def toggle_score(self, status):
        # Обновляем видимость счета в игре
        self.game.show_score = status
        
    def toggle_timer(self, status):
        # Обновляем видимость таймера в игре
        self.game.show_timer = status
        
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
            
    def update_resolution(self, resolution):
        # Получаем выбранное разрешение и разбиваем его на ширину и высоту
        width, height = map(int, resolution.split('x'))
        
        # Применяем новое разрешение
        props = WindowProperties()
        props.setSize(width, height)
        self.game.win.requestProperties(props)
