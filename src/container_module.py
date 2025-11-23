import pickle

from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior

# Assuming stdop is defined elsewhere or passed as an argument
# For now, let's define it here for the module to be self-contained
# You might need to adjust this based on your project structure
try:
    std_set = pickle.load(open("assets/std_settings.pkl", "rb"))
    stdop = std_set["STDOP"]
except:
    stdop = "Default User (XDEF)"


class Container(Screen, ThemableBehavior):
    editor = ObjectProperty()
    ops_list = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_dict = pickle.load(open("assets/std_settings.pkl", "rb"))
        self.ops_dict = self.settings_dict["OPERATOR"]
        self.ops_list = []
        for i in self.ops_dict:
            self.ops_list.append(
                self.ops_dict[i]["givenname"]
                + " "
                + self.ops_dict[i]["lastname"]
                + " ("
                + i
                + ")"
            )

        self.ops_list.sort()

        self.ids.op.spnfld.text = stdop
