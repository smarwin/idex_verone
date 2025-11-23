from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior


class LabJournal(Screen, ThemableBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
