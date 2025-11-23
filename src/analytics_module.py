from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemableBehavior

from Widgets import AnaChip  # Assuming AnaChip is in Widgets.py


class Analytics(BoxLayout, ThemableBehavior):
    anas = [
        "PXRD",
        "SCXRD",
        "HT-PXRD",
        "IR",
        "UV/VIS",
        "FLUORESCENCE",
        "NMR",
        "CHNS",
        "ICP",
        "STEM",
        "EDX",
        "RAMAN",
    ]
    prev = NumericProperty(None)
    editor = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.add_ana_chips())

    def on_height(self, *args):
        if not self.prev:
            self.prev = 0
        diff = args[1] - self.prev
        self.prev = args[1]
        try:
            self.parent.height += diff
        except:
            pass

    def add_ana_chips(self):
        self.method_list = []
        self.anas = sorted(self.anas)
        for i in self.anas:
            chip = AnaChip(label=i)
            self.method_list.append(chip)
            self.ids.ana_methods.add_widget(chip)

    def reset(self, *args):
        if "ap" in args:
            self.ids.ap.txtfld.text = ""

        if "methods" in args:
            for i in self.method_list:
                i.deselect()

        if "ana" in args:
            self.ids.anadet.txtfld.text = ""
