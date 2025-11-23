from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemableBehavior


class Information(BoxLayout, ThemableBehavior):
    editor = ObjectProperty()

    def reset(self, *args):
        if "info" in args:
            self.ids.sid.txtfld.text = ""
            self.ids.tag.txtfld.text = ""
            self.ids.lj.txtfld.text = ""
            self.ids.trgt.txtfld.text = ""
            self.ids.date.txtfld.text = ""
        if "idea" in args:
            self.ids.idea.txtfld.text = ""
