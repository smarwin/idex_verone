from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.button import Button
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivy.uix.textinput import TextInput
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.chip import MDChip
from kivy.metrics import dp
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.togglebutton import ToggleButton
from chempy import Substance
import pickle


def chemify(formula, fontsize):
    """This function creates chemical formulas with sub and sup strings"""

    smallsize = 0.7 * fontsize

    try:
        chemical = Substance.from_formula(formula).html_name
        chemical = chemical.replace("<sub>", f"[sub][size={smallsize}sp]")
        chemical = chemical.replace("</sub>", "[/size][/sub]")
        chemical = chemical.replace("<sup>", f"[sup][size={smallsize}sp]")
        chemical = chemical.replace("</sup>", "[/size][/sup]")
    except:
        chemical = formula

    return chemical


class AnaChip(MDChip):
    status = BooleanProperty(False)
    active_color = ListProperty()
    active_textcolor = ListProperty()
    inactive_color = ListProperty()
    inactive_textcolor = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.create_chip())

    def create_chip(self):
        if not self.active_color:
            self.active_color = self.theme_cls.accent_color
        if not self.active_textcolor:
            self.active_textcolor = self.theme_cls.text_color

        if not self.inactive_color:
            self.inactive_color = self.theme_cls.primary_color
        if not self.inactive_textcolor:
            self.inactive_textcolor = self.theme_cls.opposite_text_color

        self.color = self.inactive_color
        self.ids.label.color = self.theme_cls.opposite_text_color
        self.ids.label.bold = True

        self.closebtn = MDIconButton(
            icon="close",
            size_hint_y=None,
            height=dp(20),
            disabled=True,
            user_font_size=dp(20),
            pos_hint={"center_y": 0.5},
        )
        self.checkbtn = MDIconButton(
            icon="check",
            size_hint_y=None,
            height=dp(20),
            disabled=True,
            user_font_size=dp(20),
            pos_hint={"center_y": 0.5},
        )

        self.ids.box_check.add_widget(self.closebtn)

    def on_status(self, instance, value):
        if value:
            self.color = self.active_color
            self.ids.lbl.color = self.active_textcolor
        else:
            self.color = self.inactive_color
            self.ids.lbl.color = self.inactive_textcolor

        if self.check:
            if self.ids.box_check.children[0].icon == "check":
                self.ids.box_check.clear_widgets()
                self.ids.box_check.add_widget(self.closebtn)
            else:
                self.ids.box_check.clear_widgets()
                self.ids.box_check.add_widget(self.checkbtn)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.status:
                self.status = False
            else:
                self.status = True

    def deselect(self):
        self.color = self.inactive_color
        self.ids.lbl.color = self.inactive_textcolor
        self.status = False

        if self.check:
            if self.ids.box_check.children[0].icon == "check":
                self.ids.box_check.clear_widgets()
                self.ids.box_check.add_widget(self.closebtn)


class BtnBox(ButtonBehavior, BoxLayout):
    pass


class ButtonGrid_Info(ButtonBehavior, HoverBehavior, GridLayout, ThemableBehavior):
    sampleid = StringProperty()
    idea = StringProperty()
    info = StringProperty()
    root = ObjectProperty()
    spinner = ObjectProperty()
    module = StringProperty()
    op = StringProperty()
    bg_color = ListProperty([1, 1, 1, 0])

    def __init__(self, **kwargs):
        super(ButtonGrid_Info, self).__init__(**kwargs)

    def on_release(self):
        self.root.fill_modules(self.sampleid, self.module, op=self.op)

        if self.root.importpopup:
            self.root.importpopup.dismiss()

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        if self.spinner.spnfld.is_open:
            return

        self.bg_color = self.theme_cls.primary_color

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.bg_color = [1, 1, 1, 0]


class ButtonGrid_Reac(ButtonBehavior, HoverBehavior, GridLayout, ThemableBehavior):
    sampleid = StringProperty()
    reactants = StringProperty()
    products = StringProperty()
    root = ObjectProperty()
    spinner = ObjectProperty()
    module = StringProperty()
    op = StringProperty()
    bg_color = ListProperty([1, 1, 1, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self):
        self.root.fill_modules(self.sampleid, self.module, op=self.op)

        if self.root.importpopup:
            self.root.importpopup.dismiss()

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        if self.spinner.spnfld.is_open:
            return

        self.bg_color = self.theme_cls.accent_light

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.bg_color = [1, 1, 1, 0]


class ButtonGrid_SWI(ButtonBehavior, HoverBehavior, GridLayout, ThemableBehavior):
    sampleid = StringProperty()
    reactants = StringProperty()
    root = ObjectProperty()
    spinner = ObjectProperty()
    module = StringProperty()
    op = StringProperty()
    bg_color = ListProperty([1, 1, 1, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self):
        self.root.fill_modules(self.sampleid, self.module, op=self.op)

        if self.root.importpopup:
            self.root.importpopup.dismiss()

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        if self.spinner.spnfld.is_open:
            return

        self.bg_color = self.theme_cls.accent_light

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.bg_color = [1, 1, 1, 0]


class ButtonGrid_One(ButtonBehavior, HoverBehavior, GridLayout, ThemableBehavior):
    sampleid = StringProperty()
    one_cnt = StringProperty()
    root = ObjectProperty()
    spinner = ObjectProperty()
    module = StringProperty()
    op = StringProperty()
    bg_color = ListProperty([1, 1, 1, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self):
        self.root.fill_modules(self.sampleid, self.module, op=self.op)
        print(self.module)
        if self.root.importpopup:
            self.root.importpopup.dismiss()

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        if self.spinner.spnfld.is_open:
            return

        self.bg_color = self.theme_cls.accent_light

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.bg_color = [1, 1, 1, 0]


class ConfirmPopup(ModalView, ThemableBehavior):
    id = StringProperty()
    obj = ObjectProperty()
    title = StringProperty()
    text = StringProperty()
    is_open = BooleanProperty(False)

    def __init__(self, function, **kwargs):
        super().__init__(**kwargs)
        self.fnctn = function

    def on_open(self, *args):
        self.is_open = True
        Window.bind(on_key_down=self.key_action)

    def on_dismiss(self, *args):
        self.is_open = False
        Window.unbind(on_key_down=self.key_action)

    def key_action(self, *args):
        if args[1] == 13 or args[1] == 271:
            self.on_accept()
            return True

        elif args[1] == 27:
            self.dismiss()
            return True

    def on_accept(self):
        self.fnctn()
        self.dismiss()


class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class CstmSpin(ButtonBehavior, BoxLayout):
    menu_items = ListProperty()
    current_item = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def on_current_item(self,*args):
    #     print("what")

    def on_menu_items(self, *args):
        self.menu = MDDropdownMenu(
            caller=self,
            items=self.menu_items,
            position="auto",
            width_mult=4,
            callback=self.set_item,
            opening_time=0
            # max_height = 60
        )

    def set_item(self, item):
        self.ids.lbl.text = item.text
        self.menu.dismiss()


class DateBox(BoxLayout):
    _font_size = NumericProperty(16)
    _hint_text = StringProperty()
    _halign = StringProperty("center")
    txt = StringProperty()
    txtfld = ObjectProperty()
    lbl = ObjectProperty()
    # def open_datepicker(self):
    #     date_dialog = MDDatePicker(callback=self.get_date)
    #     date_dialog.open()
    #
    # def get_date(self, date):
    #     splt = str(date).split("-")
    #     german_date = ".".join(reversed(splt))
    #     setattr(self.txtfld, "text", str(german_date))


class DDSpinner(Spinner):
    values = ListProperty()
    _font_size = NumericProperty(14)
    _starttext = StringProperty()


class DownButton(MDIconButton):
    box = ObjectProperty()


class DeleteButton(MDIconButton):
    box = ObjectProperty()


class EditorPanel(MDExpansionPanel):
    editor = ObjectProperty()
    opening_time = NumericProperty(0)
    closing_time = NumericProperty(0)
    # children_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def on_children_height(self, *args):

    def check_open_panel(self, instance):
        """
        Called when you click on the panel. Called methods to open or close
        a panel.
        """
        panel = instance.parent

        if len(panel.children) == 2:
            panel.remove_widget(panel.children[0])
            chevron = panel.children[0].children[0].children[0]
            self.set_chevron_up(chevron)
            self.close_panel(panel)
            self.dispatch("on_close")

        else:
            self.open_panel(panel)
            self.set_chevron_down()
            self.dispatch("on_open")


class ExpBtn(ButtonBehavior, HoverBehavior, BoxLayout, ThemableBehavior):
    met_color = ListProperty()
    met_text_color = ListProperty([1, 1, 1, 1])
    sidtag = StringProperty()
    sample = StringProperty()
    met_text = StringProperty()
    text_color = ListProperty([0, 0, 0, 1])
    bg_color = ListProperty([0, 0, 0, 0])
    editor = ObjectProperty()

    def on_state(self, widget, value):
        if value == "down":
            self.bg_color = self.theme_cls.accent_color
        else:
            self.bg_color = [0, 0, 0, 0]

    def on_enter(self, *args):
        if self.editor.ids.exp_op.spnfld.is_open:
            return
        self.bg_color = self.theme_cls.accent_light
        self.ids.lbl.color = [0, 0, 0, 1]

    def on_leave(self, *args):
        self.bg_color = [0, 0, 0, 0]
        self.ids.lbl.color = self.text_color


class FltBtn(Button, ThemableBehavior):
    pass


class FocusButton(FocusBehavior, Button, HoverBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IcnBtn(ButtonBehavior, BoxLayout, HoverBehavior, ThemableBehavior):
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    valign = StringProperty("middle")
    halign = StringProperty("center")
    icon = StringProperty("chevron-up")
    radius = ListProperty([4, 4, 4, 4])
    font_size = NumericProperty(20)

    def on_enter(self, *args):
        if self.icon != "close":
            self.bg_color = self.theme_cls.primary_color
            self.text_color = self.theme_cls.opposite_text_color

    def on_leave(self, *args):
        if self.icon != "close":
            self.bg_color = [1, 1, 1, 1]
            self.text_color = self.theme_cls.text_color


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()


class ImportPopup(ModalView, ThemableBehavior):
    radius = ListProperty([7, 7, 7, 7])
    content_cls = ObjectProperty()
    ops_list = ListProperty()
    op = StringProperty()
    btngrid_list = ListProperty()
    editor = ObjectProperty()
    module = StringProperty()
    home = StringProperty()
    names_dict = {
        "info": [
            ("Sample ID", 1),
            ("Info (Tag, Target, Date)", 8),
        ],
        "idea": [
            ("Sample ID", 1),
            ("Idea", 8),
        ],
        "reaction": [
            ("Sample ID", 1),
            ("Reactants", 4),
            ("", None),
            ("Products", 4)
        ],
        "swi": [
            ("Sample ID", 1),
            ("Reactants (Eq)", 8),
        ],
        "additives": [
            ("Sample ID", 1),
            ("Additives", 8),
        ],
        "method": [
            ("Sample ID", 1),
            ("Method Details", 8),
        ],
        "expdet": [
            ("Sample ID", 1),
            ("Experimental Details", 8),
        ],
        "tp": [
            ("Sample ID", 1),
            ("Temperature Program (Segment: T[sub][size=10sp]start[/size][/sub] | Ramp | T[sub][size=10sp]end[/size][/sub] | Dwell)", 8),
        ],

        "ap": [
            ("Sample ID", 1),
            ("Appearance", 8),
        ],
        "anadet": [
            ("Sample ID", 1),
            ("Analytical Details", 8),
        ],
        "prod": [
            ("Sample ID", 1),
            ("Products", 8),
        ],
        "res": [
            ("Sample ID", 1),
            ("Conclusion", 8),
        ]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.key_action)

        # self.ids.op.bind(text=lambda instance, op: self.create_content(op))
        self.ids.op.spnfld.text = self.op

        for i in self.names_dict[self.module]:
            # if self.module == "reaction":
            #     customwidth =

            col_title = Factory.ALbl(
                text=i[0],
                size_hint_x=i[1],
                width=50
            )
            self.ids.col_titles.add_widget(col_title)

        Clock.schedule_once(lambda dt: self.create_content(self.op))
        self.ids.filter.txtfld.focus = True

    def key_action(self, *args):
        # focus search
        if args[3] == "f" and "ctrl" in args[4]:
            self.ids.filter.txtfld.focus = True

            return True

        if args[1] == 13 or args[1] == 271 or args[1] == 27:
            self.dismiss()
            return True

    def create_content(self, op):
        self.btngrid_list = []
        expdict = pickle.load(
            open(self.home + "/" + op + "/" + op + "_experiments.idx", "rb"))

        # Get the search filter and split them into its elements
        searchinput = self.ids.filter.text
        search_elements = []
        if searchinput != "" or not searchinput.startswith(" "):
            search_elements_with_empty_strings = searchinput.split(" ")
            for i in search_elements_with_empty_strings:
                if i != "":
                    search_elements.append(i)

        if self.module == "info":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            if searchinput != "":
                for f in search_elements:
                    search_ids = search_results
                    search_results = []
                    for n in search_ids:
                        for d in list(expdict[n]["INFORMATION"].values())[0:-1]:
                            if f in d and n not in search_results:
                                search_results.append(n)

            for i in search_results:
                info = ""
                tag = expdict[i]["INFORMATION"]["TAG"]
                trgt = chemify(expdict[i]["INFORMATION"]["TARGET"], 15)
                date = expdict[i]["INFORMATION"]["DATE"]
                # idea = expdict[i]["INFORMATION"]["IDEA"]
                # idea = idea.replace("\n", " ")
                # if len(idea) > 30:
                #     idea = idea[0:30] + "..."

                if tag:
                    info = tag

                if info and trgt:
                    info += ",   " + trgt
                elif trgt:
                    info = trgt

                if info and date:
                    info += ",   " + date
                elif date:
                    info = date

                btngrid_dict = {
                    "root": self.editor,
                    "spinner": self.ids.op,
                    "module": self.module,
                    "op": self.ids.op.method,
                    "sampleid": i,
                    "one_cnt": info,
                    # "idea": idea
                }

                self.btngrid_list.append(btngrid_dict)

        if self.module == "idea":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            if searchinput != "":
                for f in search_elements:
                    search_ids = search_results
                    search_results = []
                    for n in search_ids:
                        d = expdict[n]["INFORMATION"]["IDEA"]
                        if f in d or f in n and n not in search_results:
                            search_results.append(n)

            for i in search_results:
                idea = expdict[i]["INFORMATION"]["IDEA"]
                idea = idea.replace("\n", " ")
                if len(idea) > 120:
                    idea = idea[0:120] + "..."

                btngrid_dict = {
                    "root": self.editor,
                    "spinner": self.ids.op,
                    "module": self.module,
                    "op": self.ids.op.method,
                    "sampleid": i,
                    "one_cnt": idea,
                }

                self.btngrid_list.append(btngrid_dict)

        if self.module == "reaction":
            self.ids.rv_import.viewclass = "ButtonGrid_Reac"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    rctn = expdict[n]["REACTION"]["REACTANTS"]
                    prd = expdict[n]["REACTION"]["PRODUCTS"]
                    if f in rctn or f in prd or f in n and n not in search_results:
                        search_results.append(n)

            for i in search_results:
                if expdict[i]["REACTION"]["REACTANTS"] or expdict[i]["REACTION"]["PRODUCTS"]:
                    try:
                        btngrid_dict = {
                            "root": self.editor,
                            "spinner": self.ids.op,
                            "module": self.module,
                            "op": self.ids.op.method,
                            "sampleid": i,
                            "reactants": expdict[i]["REACTION"]["REACTANTSBAL"],
                            "products": expdict[i]["REACTION"]["PRODUCTSBAL"]
                        }
                    except:
                        btngrid_dict = {
                            "root": self.editor,
                            "spinner": self.ids.op,
                            "module": self.module,
                            "op": self.ids.op.method,
                            "sampleid": i,
                            "reactants": "",
                            "products": ""
                        }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "swi":
            self.ids.rv_import.viewclass = "ButtonGrid_SWI"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    for d in expdict[n]["SWI"]["REACTANTS"]:
                        if f in d["REACTANT"] or f in n and n not in search_results:
                            search_results.append(n)

            for i in search_results:
                rceq_list = ""
                for m in expdict[i]["SWI"]["REACTANTS"]:
                    if m["REACTANT"]:
                        trgt = chemify(m["REACTANT"], 15)

                        if m == expdict[i]["SWI"]["REACTANTS"][-1]:
                            rceq_list += trgt + " (" + m["EQUIVALENT"] + ")"
                        else:
                            rceq_list += trgt + \
                                " (" + m["EQUIVALENT"] + "),   "

                if rceq_list != "":
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "reactants": rceq_list
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "additives":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            try:
                # if searchinput != "":
                for f in search_elements:
                    search_ids = search_results
                    search_results = []
                    for n in search_ids:
                        if f in expdict[n]["SWI"]["ADDITIVES"] or f in n and n not in search_results:
                            search_results.append(n)

                for i in search_results:
                    epd = expdict[i]["SWI"]["ADDITIVES"]
                    epd = epd.replace("\n", " ")
                    if epd:
                        if len(epd) > 120:
                            epd = epd[0:120] + "..."
                        btngrid_dict = {
                            "root": self.editor,
                            "spinner": self.ids.op,
                            "module": self.module,
                            "op": self.ids.op.method,
                            "sampleid": i,
                            "one_cnt": epd
                        }

                        self.btngrid_list.append(btngrid_dict)
            except:
                pass

        if self.module == "method":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    for d in expdict[n]["TP"]["METHOD"].values():
                        if f in d or f in n and n not in search_results:
                            search_results.append(n)

            for i in search_results:
                md_list = ""
                rev_md = expdict[i]["TP"]["METHOD"]
                for m in reversed(list(rev_md)):
                    if rev_md[m] == "":
                        pass
                    else:
                        if md_list == "":
                            md_list = rev_md[m]
                        else:
                            md_list = rev_md[m] + ",   " + md_list

                if md_list.split(",") != 1:
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": md_list
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "expdet":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    if f in expdict[n]["TP"]["EXPERIMENTAL DETAILS"] or f in n and n not in search_results:
                        search_results.append(n)

            for i in search_results:
                epd = expdict[i]["TP"]["EXPERIMENTAL DETAILS"]
                epd = epd.replace("\n", " ")
                if epd:
                    if len(epd) > 120:
                        epd = epd[0:120] + "..."
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": epd
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "tp":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    for d in expdict[n]["TP"]["PROGRAM"]:
                        for e in d:
                            if f in d[e] or f in n and n not in search_results:
                                search_results.append(n)

            for i in search_results:
                tp_list = ""
                rev_tp = expdict[i]["TP"]["PROGRAM"]

                for m in rev_tp:
                    for n in m:
                        if m[n] == "":
                            k = "-"
                        else:
                            k = m[n]

                        if n == "DWELL" and m != rev_tp[-1]:
                            tp_list += k + "   -->   "
                        elif n == "DWELL" and m == rev_tp[-1]:
                            tp_list += k
                        elif n == "SEGMENT":
                            tp_list += k + ":  "
                        else:
                            tp_list += k + "  |  "

                if tp_list != "-  |  -  |  -  |  -":
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": tp_list
                    }

                    self.btngrid_list.append(btngrid_dict)

        # if self.module == "ana":
        #     self.ids.rv_import.viewclass = "ButtonGrid_One"
        #
        #     # only iterate over entries that fulfill the search criteria
        #     search_results = list(expdict.keys())
        #     search_results.sort(reverse=True)
        #
        #     # if searchinput != "":
        #     for f in search_elements:
        #         search_ids = search_results
        #         search_results = []
        #         for n in search_ids:
        #             m = expdict[n]["ANALYTICS"]["Methods"]
        #             o = expdict[n]["ANALYTICS"]["ANALYTICAL DETAILS"]
        #             for d in m:
        #                 if f in d and m[d] and n not in search_results:
        #                     search_results.append(n)
        #
        #             if f in o and n not in search_results:
        #                 search_results.append(n)
        #
        #     for i in search_results:
        #         ana_met = expdict[i]["Analytics"]["Methods"]
        #         ana_list = ""
        #         for j in ana_met:
        #             if ana_met[j]:
        #                 ana_list += j + ",   "
        #             if j == list(ana_met.keys())[-1] and ana_list != "":
        #                 ana_list = ana_list[0:-4]
        #
        #         ana_det = expdict[i]["Analytics"]["Details"]
        #         ana_det = ana_det.replace("\n"," ")
        #
        #         if ana_list != "" or ana_det != "":
        #             btngrid_dict = {
        #                 "root": self.root,
        #                 "popi": self,
        #                 "module": self.module,
        #                 "op": op,
        #                 "sampleid": i,
        #                 "ana_list": ana_list,
        #                 "ana_det": ana_det[0:80] + "..."
        #             }
        #
        #             self.btngrid_list.append(btngrid_dict)

        if self.module == "anadet":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    d = expdict[n]["ANALYTICS"]["ANALYTICAL DETAILS"]
                    if f in d or f in n and n not in search_results:
                        search_results.append(n)

            for i in search_results:
                ana = expdict[i]["ANALYTICS"]["ANALYTICAL DETAILS"]
                ana = ana.replace("\n", " ")
                if ana:
                    if len(ana) > 120:
                        ana = ana[0:120] + "..."
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": ana
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "ap":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    d = expdict[n]["ANALYTICS"]["APPEARANCE"]
                    if f in d or f in n and n not in search_results:
                        search_results.append(n)

            for i in search_results:
                ap = expdict[i]["ANALYTICS"]["APPEARANCE"]
                ap = ap.replace("\n", " ")
                if ap:
                    if len(ap) > 120:
                        ap = ap[0:120] + "..."
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": ap
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "prod":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    d = expdict[n]["RESULT"]["PRODUCTS"]
                    for m in d:
                        if f in m or f in d[m] or f in n and n not in search_results:
                            search_results.append(n)

            for i in search_results:
                prod = expdict[i]["RESULT"]["PRODUCTS"]
                prod_list = ""
                for n in prod:
                    splt = n["PRODUCT"].split("+")
                    product = ""
                    for s in splt:
                        if s == splt[-1]:
                            product += chemify(s, 15)
                        else:
                            product += chemify(s, 15) + " + "

                    if product:
                        if n == prod[-1]:
                            prod_list += n["IDENTIFIER"] + ":  " + product
                        else:
                            prod_list += n["IDENTIFIER"] + \
                                ":  " + product + ",   "

                    # for m in n:
                    #     if n[m] == "":
                    #         pass
                    #     else:
                    #         if n == prod[-1]:
                    #             prod_list += m + ":  " + n[m]
                    #         else:
                    #             prod_list += m + ":  " + n[m] + ",   "

                if prod_list:

                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": prod_list
                    }

                    self.btngrid_list.append(btngrid_dict)

        if self.module == "res":
            self.ids.rv_import.viewclass = "ButtonGrid_One"

            # only iterate over entries that fulfill the search criteria
            search_results = list(expdict.keys())
            search_results.sort(reverse=True)

            # if searchinput != "":
            for f in search_elements:
                search_ids = search_results
                search_results = []
                for n in search_ids:
                    d = expdict[n]["RESULT"]["CONCLUSION"]
                    if f in d or f in n and n not in search_results:
                        search_results.append(n)

            for i in search_results:
                concl = expdict[i]["RESULT"]["CONCLUSION"]
                concl = concl.replace("\n", " ")
                if concl:
                    if len(concl) > 120:
                        concl = concl[0:120] + "..."
                    btngrid_dict = {
                        "root": self.editor,
                        "spinner": self.ids.op,
                        "module": self.module,
                        "op": self.ids.op.method,
                        "sampleid": i,
                        "one_cnt": concl
                    }

                    self.btngrid_list.append(btngrid_dict)


class InfoPopup(ModalView, ThemableBehavior):
    title = StringProperty()
    text = StringProperty()
    is_open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_open(self, *args):
        self.is_open = True
        Window.bind(on_key_down=self.key_action)

    def on_dismiss(self, *args):
        self.is_open = False
        Window.unbind(on_key_down=self.key_action)

    def key_action(self, *args):
        if args[1] == 13 or args[1] == 271 or args[1] == 27:
            self.dismiss()
            return True


class LabelBox(BoxLayout):
    _font_size = NumericProperty(16)
    _lbl = StringProperty()
    txt = StringProperty("")
    _btmlbl = StringProperty()
    _halign = StringProperty("center")
    lblfld = ObjectProperty()
    lbl = ObjectProperty()
    btmlbl = ObjectProperty()


class PageToggler(HoverBehavior, ToggleButton, ThemableBehavior):
    def on_state(self, widget, value):
        if value == "down":
            self.color = self.theme_cls.primary_color
            self.background_color = [1, 1, 1, 1]
        else:
            self.color = [0, 0, 0, 1]
            self.background_color = [0, 0, 0, 0]

    def on_enter(self):
        if self.state == "down":
            return

        self.background_color = self.theme_cls.accent_color

    def on_leave(self):
        if self.state == "down":
            self.background_color = [1, 1, 1, 1]
        else:
            self.background_color = [0, 0, 0, 0]


class Panel(BoxLayout, ThemableBehavior):
    content = ObjectProperty(BoxLayout())
    title = StringProperty("Information")
    icon = StringProperty("information-outline")
    is_open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open(self):
        if not self.ids.content.children:
            self.ids.chevi.icon = "chevron-down"
            self.ids.content.add_widget(self.content)
            self.is_open = True

    def close(self):
        self.ids.chevi.icon = "chevron-right"
        self.ids.content.clear_widgets()
        self.is_open = False


class PlainTxtFld(TextInput):
    _hint_text = StringProperty()
    _height_multi = NumericProperty(6)
    _halign = StringProperty("center")

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.select_all())


class PopLabel(BoxLayout, ThemableBehavior):
    title = StringProperty()
    value = StringProperty()


class ReactBox(BoxLayout):
    _font_size = NumericProperty(16)
    _lbl = StringProperty()
    _hint_text = StringProperty()
    _btmlbl = StringProperty()
    _halign = StringProperty("center")
    _height_multi = NumericProperty(6)
    _multiline = BooleanProperty(False)
    _writetab = BooleanProperty(False)
    text = StringProperty()
    txt = StringProperty("")
    txtfld = ObjectProperty()
    lbl = ObjectProperty()
    btmlbl = ObjectProperty()


class ReactantBtn(ButtonBehavior, HoverBehavior, GridLayout, ThemableBehavior):
    reactants = ObjectProperty()
    container = ObjectProperty()
    reactant = StringProperty()
    tag = StringProperty()
    molarmass = StringProperty()
    tmelt = StringProperty()
    tboil = StringProperty()
    tdecomp = StringProperty()
    txt_color = ListProperty([0, 0, 0, 1])
    bg_color = ListProperty([0, 0, 0, 0])

    def on_state(self, widget, value):
        if value == "down":
            self.bg_color = self.theme_cls.accent_color
        else:
            self.bg_color = [0, 0, 0, 0]

    def on_enter(self, *args):
        popup_list = [
            self.reactants.infopop.is_open,
            self.reactants.savedialog.is_open,
            self.reactants.deletedialog.is_open,
            self.container.ids.op.spnfld.is_open
        ]

        for i in popup_list:
            if i:
                return

        self.bg_color = self.theme_cls.accent_light
        # self.ids.lbl.color = [0,0,0,1]

    def on_leave(self, *args):
        self.bg_color = [0, 0, 0, 0]
        # self.ids.lbl.color = [0,0,0,1]


class SearchPopup(ModalView, ThemableBehavior):
    is_open = BooleanProperty(False)

    editor = ObjectProperty()
    container = ObjectProperty()
    op = StringProperty()
    sid = StringProperty()
    tag = StringProperty()
    trgt = StringProperty()
    search_elements = ListProperty()
    metabb = StringProperty()
    metcol = ListProperty()
    mettxtcol = ListProperty()

    reactants = StringProperty()
    products = StringProperty()
    netweight = StringProperty()
    expdet = StringProperty()
    aplmet = StringProperty()
    anadet = StringProperty()
    ap = StringProperty()
    concl = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        std_set = pickle.load(open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        self.home = std_set["HOME"]

    def key_action(self, *args):
        if args[1] == 13 or args[1] == 271 or args[1] == 27:
            self.dismiss()
            return True

    def on_open(self, *args):
        self.is_open = True
        Window.bind(on_key_down=self.key_action)

    def on_dismiss(self, *args):
        self.is_open = False
        Window.unbind(on_key_down=self.key_action)

    def update_popup(self):
        self.exp_dict = pickle.load(open(
            self.home + "/" + self.op + "/" + self.op + "_experiments.idx", "rb"))[self.sid]

        # INFO
        self.ids.info.clear_widgets()

        self.trgt = self.trgt.replace("size=10", "size=12")
        # info_showlist = ["Sample-ID","Tag","fTarget", "Operator", "Date", "Idea"]
        for i in self.exp_dict["INFORMATION"]:

            if i == "IDEA":
                self.ids.info.add_widget(WrappedPopLabel(
                    title=i, value=self.exp_dict["INFORMATION"][i]))

            elif i == "TARGET":
                trgt = chemify(self.exp_dict["INFORMATION"][i], 15)
                self.ids.info.add_widget(PopLabel(title=i, value=trgt))
            else:
                self.ids.info.add_widget(
                    PopLabel(title=i, value=self.exp_dict["INFORMATION"][i]))

        # REACTION
        try:
            self.reactants = self.exp_dict["REACTION"]["REACTANTSBAL"]
            self.products = self.exp_dict["REACTION"]["PRODUCTSBAL"]
        except:
            self.reactants = self.exp_dict["REACTION"]["REACTANTS"]
            self.products = self.exp_dict["REACTION"]["PRODUCTS"]

        # SampleWeighIn
        self.ids.swi_grid.clear_widgets()

        columnnames = ["Reactants", "Eq",
                       "M / g·mol[sup][size=10sp]-1[/size][/sup]", "n / mmol", "m / mg"]
        self.netweight = self.exp_dict["SWI"]["NET WEIGHT"]

        for i in columnnames:
            swilbl = SWILbl(text=i, bold=True)
            self.ids.swi_grid.add_widget(swilbl)

        for i in self.exp_dict["SWI"]["REACTANTS"]:
            for j in i:
                if j == "REACTANT":
                    u = chemify(i[j], 15)

                else:
                    u = i[j]

                swilbl = SWILbl(text=str(u), pad=60)
                self.ids.swi_grid.add_widget(swilbl)

        # Method Details
        self.ids.method_grid.clear_widgets()

        for i in self.exp_dict["TP"]["METHOD"]:
            if self.exp_dict["TP"]["METHOD"][i] == "":
                self.ids.method_grid.add_widget(
                    PopLabel(title=i, value="None"))
            else:
                self.ids.method_grid.add_widget(
                    PopLabel(title=i, value=self.exp_dict["TP"]["METHOD"][i]))

        # TP
        self.ids.tp_grid.clear_widgets()
        columnnames = ["Seg.", "T[sub][size=13sp]start[/size][/sub]",
                       "Ramp", "T[sub][size=13sp]end[/size][/sub]", "Dwell"]
        columnunits = list(self.exp_dict["TP"]["UNITS"].values())
        # for i,j in enumerate(self.exp_dict["TP"]["UNITS"]):
        #     if i%2 == 0:
        #         columnunits.append(j)

        for i in range(5):
            if i == 0:
                tplbl = SWILbl(text=columnnames[i], bold=True)
                self.ids.tp_grid.add_widget(tplbl)
            else:
                tplbl = SWILbl(
                    text=columnnames[i] + "  /  " + columnunits[i-1], bold=True)
                self.ids.tp_grid.add_widget(tplbl)

        for i in self.exp_dict["TP"]["PROGRAM"]:
            for j in i:
                tplbl = SWILbl(text=str(i[j]), pad=60)
                self.ids.tp_grid.add_widget(tplbl)

        self.expdet = self.exp_dict["TP"]["EXPERIMENTAL DETAILS"]

        # Analytics
        anamet_str = ""
        ana_dict = self.exp_dict["ANALYTICS"]
        for n in ana_dict["METHODS"]:
            if ana_dict["METHODS"][n]:
                if anamet_str:
                    anamet_str = anamet_str + ",   " + n
                else:
                    anamet_str = n

        self.aplmet = anamet_str
        self.anadet = ana_dict["ANALYTICAL DETAILS"]

        # appearance
        self.ap = ana_dict["APPEARANCE"]

        # product
        self.ids.product_grid.clear_widgets()
        for i in self.exp_dict["RESULT"]["PRODUCTS"]:
            prods = ""
            if i["PRODUCT"]:
                splt = i["PRODUCT"].split("+")
                for s in splt:
                    trgt = chemify(s, 15)

                    if s is not splt[-1]:
                        prods += trgt + " + "
                    else:
                        prods += trgt

                self.ids.product_grid.add_widget(
                    SWILbl(text=i["IDENTIFIER"] + ":", bold=True))
                self.ids.product_grid.add_widget(
                    Factory.WrappedLabel(text=prods))

        # conclusion
        self.concl = self.exp_dict["RESULT"]["CONCLUSION"]


class SearchViewClass(ButtonBehavior, HoverBehavior, BoxLayout, ThemableBehavior):
    op = StringProperty()
    sid = StringProperty()
    tag = StringProperty()
    trgt = StringProperty()
    search_elements = ListProperty()
    method_abbrev = StringProperty()
    method_color = ListProperty([1, 1, 1, 1])
    method_color_text = ListProperty([0, 0, 0, 1])
    editor = ObjectProperty()
    search = ObjectProperty()
    searchpop = ObjectProperty()
    bg = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(SearchViewClass, self).__init__(**kwargs)

    def on_release(self):
        self.search.setattrs(self.searchpop,
                             sid=self.sid,
                             op=self.op,
                             tag=self.tag,
                             trgt=self.trgt,
                             search_elements=self.search_elements,
                             metabb=self.method_abbrev,
                             metcol=self.method_color,
                             mettxtcol=self.method_color_text,
                             editor=self.editor
                             )

        self.searchpop.open()
        self.searchpop.update_popup()

    def on_enter(self):
        if self.searchpop.is_open:
            return
        self.bg = [.95, .95, .95, 1]

    def on_leave(self):
        self.bg = [1, 1, 1, 1]


class SelectButton(FocusBehavior, Button, HoverBehavior):
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
        # try:
        #     self.txt = self.parent.parent.parent
        # except:
        #     pass

    def on_key_down(self, instance, key, scancode, codepoint, modifiers):
        if not self.parent:
            return

        selection = self.parent.children
        if key == 273 and self.selected:
            if self != selection[-1]:
                print(selection.index(self))
                previous_item_index = selection.index(self) + 1
                self.selected = False
                selection[previous_item_index].selected = True

        if key == 274 and self.selected and self != selection[0]:
            next_item_index = selection.index(self) - 1
            self.selected = False
            selection[next_item_index].selected = True

    def on_enter(self, *args):
        # for i in self.parent.children:
        #     i.selected = False

        setattr(self, "selected", True)

    def on_leave(self, *args):
        # for i in self.parent.children:
        #     i.selected = False

        setattr(self, "selected", False)


class SpinBox(BoxLayout):
    _font_size = NumericProperty(16)
    values = ListProperty()
    _lbl = StringProperty()
    _hint_text = StringProperty()
    method = StringProperty()
    txt = StringProperty("")
    _btmlbl = StringProperty()
    _halign = StringProperty("center")
    spnfld = ObjectProperty()
    lbl = ObjectProperty()
    btmlbl = ObjectProperty()


class SWIGrid(
    GridLayout,
    HoverBehavior
):
    btnbox = ObjectProperty()
    mass = ObjectProperty()
    swi = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_btnbox()

    def build_btnbox(self):
        # self.updnbox = Factory.AdaptBoxHeight()
        # self.upbtn = UpButton(box=self)
        # self.dnbtn = DownButton(box=self)
        self.delbox = BoxLayout(
            size_hint=(None, None),
            size=(40, 40),
            padding=(7.5, 7.5),
        )

        self.delbtn = IcnBtn(
            icon="close",
            size=(25, 25),
            bg_color=[181/255, 0/255, 16/255, 1],
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.swi.delete_selected_row(self)
        )

        self.delbox.add_widget(self.delbtn)

    def on_enter(self, *args):
        self.lbl = self.children[0]
        self.remove_widget(self.lbl)
        self.add_widget(self.delbox)

    def on_leave(self, *args):
        self.remove_widget(self.delbox)
        self.add_widget(self.lbl)
    pass


class SWILbl(Label):
    pad = NumericProperty(40)


class TextBox(BoxLayout):
    _font_size = NumericProperty(16)
    _lbl = StringProperty()
    _hint_text = StringProperty()
    _btmlbl = StringProperty()
    _halign = StringProperty("center")
    _height_multi = NumericProperty(10)
    _multiline = BooleanProperty(False)
    _writetab = BooleanProperty(False)
    text = StringProperty()
    txt = StringProperty("")
    txtfld = ObjectProperty()
    lbl = ObjectProperty()
    btmlbl = ObjectProperty()
    _scroll_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.txtfld.bind(focus=self.on_focus))

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.txtfld.select_all())


class TxtOpt(PlainTxtFld):
    values = ListProperty()
    dp = ObjectProperty()
    swi = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window.bind(on_key_down=self.on_key_down)
        self.bind(values=lambda instance, values: self.create_dp(values))
        # self.bind(on_text_validate=self.on_enter)
        self.values.append("AlN")

    def on_text_validate(self, *args):
        self.get_focus_next().focus = True

        for i in self.dp.children[0].children:
            if i.selected:
                setattr(self, "text", i.text)
        if self.dp.parent is not None:
            self.dp.dismiss()

    def create_dp(self, values):
        self.dp = DropDown(
            container=Factory.DDContainer(),
            # auto_width=False
        )
        self.dp.bind(on_select=self.on_select)

        for i in values:
            btn = SelectButton(text=i)
            btn.bind(on_release=lambda item: self.dp.select(item.text))
            self.dp.add_widget(btn)

    def on_select(self, instance, text_item):
        setattr(self, "text", text_item)
        self.dp.dismiss()

    def on_text(self, instance, text_textinput):
        self.values = self.swi.reactants

        if self.dp.parent is not None:
            self.dp.dismiss()

        values = []
        for i in self.values:
            if i.startswith(text_textinput):
                values.append(i)

        self.create_dp(values)

        if self.dp.parent is None and values:
            # print(instance, " has no parent")
            self.dp.open(instance)
            self.dp.children[0].children[-1].selected = True

        self.swi.fill_M(self, text_textinput)

    def on_focus(self, instance, value):
        # print("i was called")
        if value and self.text != "" and self.dp.parent is None:
            self.dp.open(instance)
            Clock.schedule_once(lambda dt: self.select_all())
            # Clock.schedule_once(lambda dt: self.dp.open(self))
        else:
            # print("dismiss")
            self.dp.dismiss()
            pass

    def on_touch_up(self, touch):
        if touch.grab_current == self and self.dp.parent is None:
            self.on_text(self, self.text)

        return True


class TitleSpin(FloatLayout):
    font_size = NumericProperty(14)
    text = StringProperty()
    values = ListProperty()


class UpButton(MDIconButton):
    box = ObjectProperty()


class UserBtn(RectangularRippleBehavior, ButtonBehavior, BoxLayout):
    user = StringProperty()


class WrappedPopLabel(BoxLayout, ThemableBehavior):
    title = StringProperty()
    value = StringProperty()
