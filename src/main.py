# Standard Library Imports
import os
import pickle

# Kivy and KivyMD Imports
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (BooleanProperty, DictProperty, ListProperty,
                             NumericProperty, ObjectProperty, StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior

# External Libraries
from chempy import Substance, balance_stoichiometry

from Widgets import *
from tex import *

MAX_CLOCK_ITERATIONS = 200
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 400

Builder.load_file('Layout.kv')
Builder.load_file('Widgets.kv')

Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Window.maximize()
Window.minimum_width = 1200
Window.minimum_height = 400


# from kivymd.uix.picker import MDDatePicker
# from importpopup import ImportPopup


Clock.max_iteration = MAX_CLOCK_ITERATIONS

# Standard variables

try:
    std_set = pickle.load(open("../IDEXDATA/DATA/std_settings.pkl", "rb"))

except:
    std_set = {
        "HOME": "../IDEXDATA",
        "STDOP": "Marwin Dialer (MD)",
        "OPERATOR": {}
    }

home = std_set["HOME"]
stdop = std_set["STDOP"]
ops_dict = std_set["OPERATOR"]

# general functions for use


class Analytics(BoxLayout, ThemableBehavior):
    anas = ["PXRD", "SCXRD", "HT-PXRD", "IR", "UV/VIS",
            "FLUORESCENCE", "NMR", "CHNS", "ICP", "STEM", "EDX", "RAMAN"]
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


class Container(Screen, ThemableBehavior):
    editor = ObjectProperty()
    ops_list = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_dict = pickle.load(
            open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        self.ops_dict = self.settings_dict["OPERATOR"]
        self.ops_list = []
        for i in self.ops_dict:
            self.ops_list.append(
                self.ops_dict[i]["givenname"] + " " + self.ops_dict[i]["lastname"] + " (" + i + ")")

        self.ops_list.sort()

        self.ids.op.spnfld.text = stdop


class Editor(Screen, ThemableBehavior):
    container = ObjectProperty()
    mainwindow = ObjectProperty()
    ops_list = ListProperty()
    ops_dict = DictProperty()
    save_value = BooleanProperty(False)
    title = StringProperty("   -   |   -   |   -   ")
    samplelist = ListProperty()
    importpopup = None
    info_panel = ObjectProperty()
    method_dict = DictProperty({
        "Tube Furnace": {
            "RGBA": [0/255, 121/255, 107/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "TF"
        },
        "RF Furnace": {
            "RGBA": [255/255, 171/255, 5/255, 1],
            "RGBATEXT": [0, 0, 0, 1],
            "ABBREV": "RF"
        },
        "DSC": {
            "RGBA": [105/255, 45/255, 9/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "DSC"
        },
        "Multianvil Press": {
            "RGBA": [0/255, 50/255, 140/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "MAP"
        },
        "HIP": {
            "RGBA": [181/255, 0/255, 16/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "HIP"
        },
        "Ammonothermal": {
            "RGBA": [162/255, 0/255, 188/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "ATS"
        }
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Clock.schedule_once(lambda dt: self.creatibus())
        try:
            self.ops_list = os.listdir(home)
        except:
            self.ops_list = ["No OPs found"]

        try:
            self.expdict = pickle.load(
                open(home + "/" + stdop + "/" + stdop + "_experiments.idx", "rb"))
        except:
            self.expdict = {}

        # self.ids.exp_op._starttext = stdop

        self.info = Information(editor=self)
        self.reaction = Reaction(editor=self)
        self.swi = SampleWeighin(editor=self)
        self.tp = TempProg(editor=self)
        self.ana = Analytics(editor=self)
        self.res = Result(editor=self)

        # create dialogs
        self.infopop = InfoPopup()

        self.savedialog = ConfirmPopup(
            self.save_entry,
            id="save",
            obj=self,
            title="Save Entry?",
            text="This entry already exists. Are you sure to overwrite it?"
        )

        self.deletedialog = ConfirmPopup(
            self.delete_entry,
            id="delete",
            obj=self,
            title="Delete Entry?",
            text="Are you sure to delete this entry?",
        )

        self.pdfdialog = ConfirmPopup(
            self.make_pdf,
            id="make_pdf",
            obj=self,
            title="Overwrite PDF?",
            text="For this entry a PDF file already exists. Are you sure to overwrite it?",
        )

        Clock.schedule_once(lambda dt: setattr(
            self.ids.exp_op, "_starttext", stdop))
        Clock.schedule_once(lambda dt: self.create_modules())
        Clock.schedule_once(lambda dt: self.sample_btns())
        Clock.schedule_once(lambda dt: self.info_panel.open())

        # Clock.schedule_once(lambda dt: self.open_all_panels(self.ids.modules),2)
        # Clock.schedule_once(lambda dt: self.info_panel.open_panel(self.info_panel),5)
        # Clock.schedule_once(lambda dt: self.info_panel.set_chevron_down(),2)

    def change_operator(self, op):

        self.op = op

        if not os.path.exists(home + "/" + self.op):
            os.makedirs(home + "/" + self.op)
        if not os.path.exists(home + "/" + self.op + "/pdf"):
            os.makedirs(home + "/" + self.op + "/pdf")
        if not os.path.exists(home + "/" + self.op + "/tex"):
            os.makedirs(home + "/" + self.op + "/tex")

        try:
            self.expdict = pickle.load(
                open(home + "/" + self.op + "/" + self.op + "_experiments.idx", "rb"))
        except:
            self.expdict = {}
            f = open(home + "/" + self.op + "/" +
                     self.op + "_experiments.idx", "w")

        self.ops_list = os.listdir(home)

        # all system relevant data lies in IDEXDATA/DATA, yet I don't want it in the OP-SPIN of the sidebar
        try:
            self.ops_list.remove("DATA")
        except:
            pass

    def change_title(self):
        sid = self.info.ids.sid.txtfld.text
        tag = self.info.ids.tag.txtfld.text
        trgt = chemify(self.info.ids.trgt.txtfld.text, 30)

        if sid != "":
            self.title = sid + "   "
        else:
            # self.title = "   SAMPLE ID   "
            self.title = "-   "

        if tag != "":
            self.title += "|   " + tag + "   "
        else:
            # self.title += "|   TAG   "
            self.title += "|   -   "

        if trgt != "":
            self.title += "|   " + trgt + "   "
        else:
            # self.title += "|   TARGET   "
            self.title += "|   -   "

    def check_for_file(self, *args):
        if self.op == "Default User (XDEF)":
            self.infopop.title = "Warning"
            self.infopop.text = "The Default User is just for show. Please create your own user to save or delete experiments."
            self.infopop.open()
        else:
            self.sid = self.info.ids.sid.txtfld.text

            if self.sid == "":
                self.infopop.title = "Please enter a sample ID first"
                self.infopop.text = "You need at least a sample ID for this function."
                self.infopop.open()

            elif "save" in args:
                if self.sid in self.expdict:
                    self.savedialog.open()
                else:
                    self.save_entry()

            elif "delete" in args:
                if self.sid not in self.expdict:
                    self.infopop.title = "No entry found with this sample ID"
                    self.infopop.text = "Can't delete what isn't there. Mind you, you can only delete your current operator's entries."
                    self.infopop.open()

                else:
                    self.deletedialog.open()

            elif "createpdf" in args:

                if os.path.exists(home + "/" + self.op + "/pdf/" + self.sid + ".pdf"):
                    self.pdfdialog.open()
                elif self.sid in self.expdict:
                    self.make_pdf()

                else:
                    self.infopop.title = "Save this entry first!"
                    self.infopop.text = "You need to save your entry before you can create the PDF file."
                    self.infopop.open()

    def close_all_panels(self):
        for module in self.modules:
            module.close()

    def create_modules(self):
        self.info_panel = Panel(
            content=self.info,
            icon="information-outline",
            title="Information"
        )
        self.reaction_panel = Panel(
            content=self.reaction,
            icon="react",
            title="Reaction"
        )
        self.swi_panel = Panel(
            content=self.swi,
            icon="scale-balance",
            title="Sample Weigh-in"
        )
        self.tp_panel = Panel(
            content=self.tp,
            icon="stove",
            title="Method and Temperature Program"
        )
        self.ana_panel = Panel(
            content=self.ana,
            icon="chart-bar",
            title="Analytics"
        )
        self.res_panel = Panel(
            content=self.res,
            icon="clipboard-check-outline",
            title="Results"
        )

        self.modules = [
            self.info_panel,
            self.reaction_panel,
            self.swi_panel,
            self.tp_panel,
            self.ana_panel,
            self.res_panel
        ]

        for module in self.modules:
            self.ids.modules.add_widget(module)

    def make_pdf(self):
        create_tex(self.sid, self.op)
        create_pdf(self.sid, self.op)

    # creates pdfs for all experiments
    # def make_pdf(self):
    #     for i in self.expdict:
    #         if i == "MD0125":
    #             continue
    #         if int(i[-3:]) < 61:
    #             continue
    #
    #         create_tex(self.expdict[i]["INFORMATION"]["SAMPLE ID"], 'Marwin Dialer (MD)')
    #         create_pdf(self.expdict[i]["INFORMATION"]["SAMPLE ID"], 'Marwin Dialer (MD)')

    def delete_entry(self):
        self.expdict.pop(self.sid)
        pickle.dump(self.expdict, open(home + "/" + self.op +
                    "/" + self.op + "_experiments.idx", "wb"))

        try:
            os.remove(home + "/" + self.op + "/pdf/" + self.sid + ".pdf")
            print("PDF was removed")
        except:
            pass

        self.sample_btns()
        # self.open_and_delay("new_entry")
        self.new_entry()

    def fill_modules(self, sample, *modules, **kwargs):

        if "op" in kwargs:
            self.exp_op = kwargs["op"]
        else:
            self.exp_op = self.ids.exp_op.text

        self.sidebar_expdict = pickle.load(
            open(home + "/" + self.exp_op + "/" + self.exp_op + "_experiments.idx", "rb"))

        if "complete" in modules:
            try:
                if self.sidebar_expdict[sample]["COMPLETE"]:
                    self.ids.complete.status = True
                else:
                    self.ids.complete.status = False
            except:
                self.ids.complete.status = False

        if "info" in modules:
            info_dict = self.sidebar_expdict[sample]["INFORMATION"]

            self.info.ids.sid.txtfld.text = info_dict["SAMPLE ID"]
            self.info.ids.tag.txtfld.text = info_dict["TAG"]
            try:
                self.info.ids.lj.txtfld.text = info_dict["LABJOURNAL"]
            except:
                self.info.ids.lj.txtfld.text = ""

            self.info.ids.date.txtfld.text = info_dict["DATE"]
            self.info.ids.trgt.txtfld.text = info_dict["TARGET"]

        if "idea" in modules:
            info_dict = self.sidebar_expdict[sample]["INFORMATION"]
            self.info.ids.idea.txtfld.text = info_dict["IDEA"]

        if "reaction" in modules:
            reac_dict = self.sidebar_expdict[sample]["REACTION"]

            self.reaction.error = ""
            self.reaction.ids.reactants.txtfld.text = reac_dict["REACTANTS"]
            self.reaction.ids.products.txtfld.text = reac_dict["PRODUCTS"]

            try:
                self.reaction.ids.output_reactants.text = reac_dict["REACTANTSBAL"]
                self.reaction.ids.output_products.text = reac_dict["PRODUCTSBAL"]
            except:
                self.reaction.ids.output_reactants.text = ""
                self.reaction.ids.output_products.text = ""
            #     self.reaction.balance_reaction()

        if "swi" in modules:
            try:
                swi_dict = self.sidebar_expdict[sample]["SWI"]
                # self.swi.error = ""

                self.swi.ids.netweight.txtfld.text = swi_dict["NET WEIGHT"]

                self.swi.swi_grid.clear_widgets()
                self.swi.swi_rows = []
                num_reac = len(swi_dict["REACTANTS"])
                for i in range(num_reac):
                    self.swi.add_swi_row()

                for n, x in enumerate(self.swi.swi_rows):
                    x.children[5].unbind(text=x.children[5].on_text)
                    x.children[5].text = swi_dict["REACTANTS"][n]["REACTANT"]
                    x.children[5].bind(text=x.children[5].on_text)
                    x.children[4].text = swi_dict["REACTANTS"][n]["EQUIVALENT"]
                    x.children[3].text = swi_dict["REACTANTS"][n]["MOLAR MASS"]
                    x.children[2].text = swi_dict["REACTANTS"][n]["MOL"]
                    x.children[1].text = swi_dict["REACTANTS"][n]["MASS"]
            except:
                pass

        if "additives" in modules:
            try:
                self.swi.ids.additives.txtfld.text = self.sidebar_expdict[sample]["SWI"]["ADDITIVES"]
            except:
                print("That did not work")
                self.swi.ids.additives.txtfld.text = ""

        if "method" in modules:
            tp_dict = self.sidebar_expdict[sample]["TP"]

            self.tp.ids.method.spnfld.text = tp_dict["METHOD"]["Method"]
            # para = reversed(self.tp.method_parameters)
            for i, j in enumerate(tp_dict["METHOD"].values()):
                if j != "Method":
                    self.tp.method_parameters[i-1].txtfld.text = j

        if "expdet" in modules:
            tp_dict = self.sidebar_expdict[sample]["TP"]
            self.tp.ids.expdet.txtfld.text = tp_dict["EXPERIMENTAL DETAILS"]

        if "tp" in modules:
            tp_dict = self.sidebar_expdict[sample]["TP"]
            self.tp.ids.tstart_unit.unit.text = tp_dict["UNITS"]["TSTART"]
            self.tp.ids.ramp_unit.unit.text = tp_dict["UNITS"]["RAMP"]
            self.tp.ids.tend_unit.unit.text = tp_dict["UNITS"]["TEND"]
            self.tp.ids.dwell_unit.unit.text = tp_dict["UNITS"]["DWELL"]

            # Need to clear all Reactant Rows before inserting new ones
            for i in self.tp.tp_rows:
                for j in i:
                    self.tp.ids.tp_grid.remove_widget(j)

            self.tp.tp_rows = []

            no_seg = len(tp_dict["PROGRAM"])
            for i in range(no_seg-1):
                self.tp.add_tp_row()

            # Fill rows
            x = self.tp.tp_rows

            for i in range(no_seg):
                if i == 0:
                    self.tp.ids.tstart.text = tp_dict["PROGRAM"][i]["TSTART"]
                    self.tp.ids.ramp.text = tp_dict["PROGRAM"][i]["RAMP"]
                    self.tp.ids.tend.text = tp_dict["PROGRAM"][i]["TEND"]
                    self.tp.ids.dwell.text = tp_dict["PROGRAM"][i]["DWELL"]

                else:
                    x[i-1][0].text = tp_dict["PROGRAM"][i]["SEGMENT"]
                    x[i-1][1].text = tp_dict["PROGRAM"][i]["TSTART"]
                    x[i-1][2].text = tp_dict["PROGRAM"][i]["RAMP"]
                    x[i-1][3].text = tp_dict["PROGRAM"][i]["TEND"]
                    x[i-1][4].text = tp_dict["PROGRAM"][i]["DWELL"]

        if "ap" in modules:
            ana_dict = self.sidebar_expdict[sample]["ANALYTICS"]

            self.ana.ids.ap.txtfld.text = ana_dict["APPEARANCE"]

        if "ana" in modules:
            ana_dict = self.sidebar_expdict[sample]["ANALYTICS"]
            try:
                for i in self.ana.method_list:
                    i.status = ana_dict["METHODS"][i.label]
            except:
                for i in self.ana.method_list:
                    i.status = False

                print("Still old ANA KEYS")
                pass

        if "anadet" in modules:
            ana_dict = self.sidebar_expdict[sample]["ANALYTICS"]
            self.ana.ids.anadet.txtfld.text = ana_dict["ANALYTICAL DETAILS"]

        if "prod" in modules:
            # Need to clear all Reactant Rows before inserting new ones
            res_dict = self.sidebar_expdict[sample]["RESULT"]
            for i in self.res.product_rows:
                for j in i:
                    self.res.ids.product_grid.remove_widget(j)

            self.res.product_rows = []

            no_prod = len(res_dict["PRODUCTS"])
            for i in range(no_prod-1):
                self.res.add_product_row()

            # Fill rows
            x = self.res.product_rows

            for i in range(no_prod):
                if i == 0:
                    self.res.ids.identifier.txtfld.text = res_dict["PRODUCTS"][i]["IDENTIFIER"]
                    self.res.ids.product.txtfld.text = res_dict["PRODUCTS"][i]["PRODUCT"]

                else:
                    x[i-1][0].text = res_dict["PRODUCTS"][i]["IDENTIFIER"]
                    x[i-1][1].text = res_dict["PRODUCTS"][i]["PRODUCT"]

        if "res" in modules:
            res_dict = self.sidebar_expdict[sample]["RESULT"]
            self.res.ids.conclusion.txtfld.text = res_dict["CONCLUSION"]

    def key_action(self, *args):
        # print(args)
        # Open all Panels
        if args[3] == "o" and "ctrl" in args[4] and "shift" not in args[4]:
            self.open_all_panels()
            self.ids.editor_sv.scroll_y = 1

        # Close all Panels
        if args[3] == "o" and "ctrl" in args[4] and "shift" in args[4]:
            self.close_all_panels()
            self.ids.editor_sv.scroll_y = 1

        # Open Info and Focus
        if args[3] == "1" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.info_panel.is_open:
                self.info_panel.open()
            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.info_panel))
            self.info.ids.sid.txtfld.focus = True

        # Open Reaction and Focus
        if args[3] == "2" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.reaction_panel.is_open:
                self.reaction_panel.open()
            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.reaction_panel))
            self.reaction.ids.reactants.txtfld.focus = True

        # Open SWI and Focus
        if args[3] == "3" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.swi_panel.is_open:
                self.swi_panel.open()
            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.swi_panel))
            self.swi.ids.netweight.txtfld.focus = True

        # Open TP and Focus
        if args[3] == "4" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.tp_panel.is_open:
                self.tp_panel.open()
            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.tp_panel))
            self.tp.ids.method_grid.children[-2].txtfld.focus = True

        # Open Analytics and Focus
        if args[3] == "5" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.ana_panel.is_open:
                self.ana_panel.open()

            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.ana_panel))
            self.ana.ids.ap.txtfld.focus = True

        # Open Results and Focus
        if args[3] == "6" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.res_panel.is_open:
                self.res_panel.open()

            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.res_panel))
            self.res.ids.identifier.txtfld.focus = True

        # Save Entry
        if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
            self.check_for_file("save")

        # Delete Entry Strg + Entf
        if args[1] == 127 and "ctrl" in args[4] and "shift" not in args[4]:
            self.check_for_file("delete")

        # Focus Sidebar Filter
        if args[3] == "f" and "ctrl" in args[4] and "shift" in args[4]:
            self.ids.filter.txtfld.focus = True

        # Calculate SWI
        if args[3] == "c" and "ctrl" in args[4] and "shift" in args[4]:
            self.swi.calc_swi()

        # Balance Reaction
        if args[3] == "b" and "ctrl" in args[4] and "shift" in args[4]:
            self.reaction.balance_reaction()

        # New Entry
        if args[3] == "n" and "ctrl" in args[4] and "shift" not in args[4]:
            self.new_entry()

        # Create PDF
        if args[3] == "p" and "ctrl" in args[4] and "shift" not in args[4]:
            self.check_for_file("createpdf")

        # Add Reactants and TP Rows - 270,87 is numpad plus
        if args[1] == 270 and args[2] == 87 and "ctrl" in args[4]:
            if "shift" not in args[4]:
                self.swi.add_swi_row()
            elif "shift" in args[4]:
                self.tp.add_tp_row()

        # Subtract Reactants and TP Rows - 269,86 is numpad minus
        if args[1] == 269 and args[2] == 86 and "ctrl" in args[4]:
            if "shift" not in args[4]:
                if not self.swi.swi_rows:
                    return
                self.swi.del_swi_row()
            elif "shift" in args[4]:
                if not self.tp.tp_rows:
                    return
                self.tp.del_tp_row()

        # Scroll DOWN - 274,81 is DOWN
        sci = 0.05  # scroll interval
        if args[1] == 274 and args[2] == 81 and "ctrl" in args[4]:
            scr = self.ids.editor_sv.scroll_y
            scr -= sci
            if scr < 0:
                scr = 0

            self.ids.editor_sv.scroll_y = scr

        # Scroll UP - 273,82 is up
        if args[1] == 273 and args[2] == 82 and "ctrl" in args[4]:
            scr = self.ids.editor_sv.scroll_y
            scr += sci
            if scr > 1:
                scr = 1

            self.ids.editor_sv.scroll_y = scr

    def new_entry(self):
        self.info.reset("info", "idea")
        self.reaction.reset()
        self.swi.reset("weighin", "additives")
        self.tp.reset("method", "expdet", "program")
        self.ana.reset("ap", "methods", "ana")
        self.res.reset("product", "conclusion")
        return

        self.info.ids.sid.txtfld.focus = True
        self.info.ids.sid.txtfld.text = ""
        self.info.ids.tag.txtfld.text = ""
        self.info.ids.lj.txtfld.text = ""
        self.info.ids.trgt.txtfld.text = ""
        self.info.ids.date.txtfld.text = ""
        self.info.ids.idea.txtfld.text = ""

        self.reaction.error = ""
        self.reaction.ids.reactants.txtfld.text = ""
        self.reaction.ids.products.txtfld.text = ""
        self.reaction.ids.output_reactants.text = ""
        self.reaction.ids.output_products.text = ""

        self.swi.ids.netweight.txtfld.text = ""
        self.swi.error = ""
        for i in self.swi.swi_rows:
            for j in i:
                self.swi.ids.swi_grid.remove_widget(j)
        self.swi.swi_rows = []

        self.swi.ids.reac.txtfld.unbind(text=self.swi.ids.reac.txtfld.on_text)
        self.swi.ids.reac.txtfld.text = ""
        self.swi.ids.reac.txtfld.bind(text=self.swi.ids.reac.txtfld.on_text)
        self.swi.ids.eq.txtfld.text = ""
        self.swi.ids.molarmass.txtfld.text = ""
        self.swi.ids.mol.lblfld.text = ""
        self.swi.ids.mass.lblfld.text = ""

        self.tp.ids.method.spnfld.text = "DSC"
        self.tp.ids.method.spnfld.text = "Tube Furnace"
        self.tp.ids.expdet.txtfld.text = ""
        # self.tp.ids.tstart_unit.unit.text = "°C"
        # self.tp.ids.ramp_unit.unit.text = tp_dict["UNITS"]["RAMP"]
        # self.tp.ids.tend_unit.unit.text = tp_dict["UNITS"]["TEND"]
        # self.tp.ids.dwell_unit.unit.text = tp_dict["UNITS"]["DWELL"]
        for i in self.tp.tp_rows:
            for j in i:
                self.tp.ids.tp_grid.remove_widget(j)
        self.tp.tp_rows = []
        self.tp.ids.tstart.text = ""
        self.tp.ids.ramp.text = ""
        self.tp.ids.tend.text = ""
        self.tp.ids.dwell.text = ""

        self.ana.ids.ap.txtfld.text = ""
        for i in self.ana.method_list:
            i.status = False
        self.ana.ids.anadet.txtfld.text = ""

        for i in self.res.product_rows:
            for j in i:
                self.res.ids.product_grid.remove_widget(j)
        self.res.product_rows = []
        self.res.ids.identifier.txtfld.text = ""
        self.res.ids.product.txtfld.text = ""

        self.res.ids.conclusion.txtfld.text = ""

    def on_enter(self, *args):
        if self.info_panel:
            self.info_panel.open()

        self.info.ids.sid.txtfld.focus = True
        Window.bind(on_key_down=self.key_action)

    def on_leave(self, *args):
        Window.unbind(on_key_down=self.key_action)

    def open_all_panels(self):
        for module in self.modules:
            module.open()

    def open_help(self):
        self.dialog = InfoPopup(
            title="This does not work yet!",
            text="This function will be available in a future release. Stay tuned!",
        )

        self.dialog.open()

    def open_import(self, module):
        # if module == "INFO":
        #     self.content = Info_cnt(
        #         editor = self,
        #         ops_list = self.container.ops_list,
        #         op = self.container.ids.op.text,
        #         module = module,
        #         home = home
        #         )

        self.importpopup = ImportPopup(
            # content_cls = self.content,
            editor=self,
            ops_list=self.ops_list,
            op=self.container.ids.op.text,
            module=module,
            home=home
        )

        self.importpopup.open()

    def sample_btns(self):
        self.ops_list = os.listdir(home)
        # all system relevant data lies in IDEXDATA/DATA, yet I don't want it in the OP-SPIN of the sidebar
        try:
            self.ops_list.remove("DATA")
        except:
            pass

        self.samplelist = []
        self.exp_op = self.ids.exp_op.text
        # self.exp_op= self.ops_dict[self.ids.exp_op.text]

        # self.sb.samples.clear_widgets()

        # Get the List of pkl files and strip the .pkl
        try:
            self.sidebar_expdict = pickle.load(
                open(home + "/" + self.exp_op + "/" + self.exp_op + "_experiments.idx", "rb"))
        except:
            return

        self.sample_files = []
        for i in self.sidebar_expdict:
            sid = i
            tag = self.sidebar_expdict[i]["INFORMATION"]["TAG"]
            met = self.sidebar_expdict[i]["TP"]["METHOD"]["Method"]
            met = self.method_dict[met]["ABBREV"]
            sidtagmet = sid + "#" + tag + "#" + met
            self.sample_files.append(sidtagmet)

        # self.sample_names = []
        # for i in self.sample_files:
        #     split = os.path.splitext(i)[0]
        #     self.sample_names.append(split)

        self.sample_files.sort(key=lambda v: v.upper(), reverse=True)

        # Get Search Input and split it into search elements (if sampleid and Tag is given)
        btn_search = self.ids.filter.text

        if btn_search == "" or btn_search.startswith(" "):
            search_elements = [""]
        else:
            search_elements_with_empty_strings = btn_search.split(" ")
            search_elements = []
            for i in search_elements_with_empty_strings:
                if i != "":
                    search_elements.append(i)

        self.search_result = self.sample_files

        for i in search_elements:
            self.sample_files = self.search_result
            self.search_result = []
            for j in self.sample_files:
                if i in j and j not in self.search_result:
                    self.search_result.append(j)

        final_results = []
        for i in self.search_result:
            final_results.append(i.split("#")[0])

        for i in final_results:
            sid = i
            tag = self.sidebar_expdict[i]["INFORMATION"]["TAG"]
            met = self.sidebar_expdict[i]["TP"]["METHOD"]["Method"]

            met_color = self.method_dict[met]["RGBA"]
            met_text_color = self.method_dict[met]["RGBATEXT"]
            met_text = self.method_dict[met]["ABBREV"]

            try:
                compl = self.sidebar_expdict[i]["COMPLETE"]
            except:
                compl = False

            if compl:
                text_color = self.theme_cls.primary_color
            else:
                text_color = [181/255, 0/255, 16/255, 1]

            if tag != "":
                sidtag = sid + "   |   " + tag
            else:
                sidtag = sid

            btndict = {}
            btndict["sidtag"] = sidtag
            btndict["sample"] = i
            btndict["editor"] = self
            btndict["met_color"] = met_color
            btndict["met_text_color"] = met_text_color
            btndict["met_text"] = met_text
            btndict["text_color"] = text_color

            self.samplelist.append(btndict)

    def save_entry(self):
        # INFO
        info_dict = {
            "SAMPLE ID": self.info.ids.sid.text,
            "TAG": self.info.ids.tag.text,
            "LABJOURNAL": self.info.ids.lj.text,
            "TARGET": self.info.ids.trgt.text,
            "DATE": self.info.ids.date.text,
            "IDEA": self.info.ids.idea.text
        }

        # REACTION
        reaction_dict = {
            "REACTANTS": self.reaction.ids.reactants.text,
            "PRODUCTS": self.reaction.ids.products.text,
            "REACTANTSBAL": self.reaction.ids.output_reactants.text,
            "PRODUCTSBAL": self.reaction.ids.output_products.text
        }

        # SWI
        reactants_list = []

        for i in self.swi.swi_rows:
            reactant_dict = {
                "REACTANT": i.children[5].text,
                "EQUIVALENT": i.children[4].text,
                "MOLAR MASS": i.children[3].text,
                "MOL": i.children[2].text,
                "MASS": i.children[1].text
            }
            reactants_list.append(reactant_dict)

        swi_dict = {
            "NET WEIGHT": self.swi.ids.netweight.txtfld.text,
            "ADDITIVES": self.swi.ids.additives.txtfld.text,
            "REACTANTS": reactants_list,
        }

        # TP
        method_dict = {}
        for i in reversed(self.tp.ids.method_grid.children):
            method_dict[i.lbl.text] = i.text

        program_list = [{
            "SEGMENT": "1",
            "TSTART": self.tp.ids.tstart.text,
            "RAMP": self.tp.ids.ramp.text,
            "TEND": self.tp.ids.tend.text,
            "DWELL": self.tp.ids.dwell.text,
        }]

        for i in self.tp.tp_rows:
            program_dict = {
                "SEGMENT": i[0].text,
                "TSTART": i[1].text,
                "RAMP": i[2].text,
                "TEND": i[3].text,
                "DWELL": i[4].text
            }
            program_list.append(program_dict)

        units_dict = {
            "TSTART": self.tp.ids.tstart_unit.unit.text,
            "RAMP": self.tp.ids.ramp_unit.unit.text,
            "TEND": self.tp.ids.tend_unit.unit.text,
            "DWELL": self.tp.ids.dwell_unit.unit.text,
        }

        tp_dict = {
            "METHOD": method_dict,
            "EXPERIMENTAL DETAILS": self.tp.ids.expdet.text,
            "UNITS": units_dict,
            "PROGRAM": program_list
        }

        # ANA
        ana_method_dict = {}
        for i in self.ana.method_list:
            ana_method_dict[i.label] = i.status

        ana_dict = {
            "APPEARANCE": self.ana.ids.ap.text,
            "METHODS": ana_method_dict,
            "ANALYTICAL DETAILS": self.ana.ids.anadet.text
        }

        # RES
        product_list = [{
            "IDENTIFIER": self.res.ids.identifier.text,
            "PRODUCT": self.res.ids.product.text
        }]
        for i in self.res.product_rows:
            product_dict = {}
            product_dict["IDENTIFIER"] = i[0].text
            product_dict["PRODUCT"] = i[1].text
            product_list.append(product_dict)

        res_dict = {
            "PRODUCTS": product_list,
            "CONCLUSION": self.res.ids.conclusion.text
        }

        # MERGE everything

        entry_dict = {
            "OPERATOR": self.container.ids.op.spnfld.text,
            "COMPLETE": self.ids.complete.status,
            "INFORMATION": info_dict,
            "REACTION": reaction_dict,
            "SWI": swi_dict,
            "TP": tp_dict,
            "ANALYTICS": ana_dict,
            "RESULT": res_dict
        }

        self.expdict[self.info.ids.sid.text] = entry_dict

        pickle.dump(self.expdict, open(home + "/" + self.op +
                    "/" + self.op + "_experiments.idx", "wb"))

        self.sample_btns()
        setattr(self.ids.exp_op, "text", self.container.ids.op.text)
        setattr(self.ids.exp_op.ids.spnfld, "text", self.container.ids.op.text)

    def update_reacspin(self):
        pass

    def view_pdf(self):
        self.sampleid = self.info.ids.sid.txtfld.text
        if os.path.exists(home + "/" + self.op + "/pdf/" + self.sampleid + ".pdf"):
            subprocess.Popen(self.sampleid + ".pdf", cwd=home +
                             "/" + self.op + "/pdf", shell=True)
        else:
            self.infopop.title = "No PDF found"
            self.infopop.text = "Create a PDF first."
            self.infopop.open()


class IDEXSettings(Screen, ThemableBehavior):
    ops_list = ListProperty()
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_dict = pickle.load(
            open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        self.ops_dict = self.settings_dict["OPERATOR"]
        # self.ops_dict = {}
        self.ops_list = []
        for i in self.ops_dict:
            self.ops_list.append(
                self.ops_dict[i]["givenname"] + " " + self.ops_dict[i]["lastname"] + " (" + i + ")")

        self.ops_list.sort()
        self.stdop = stdop
        self.home = home

        self.savedialog = ConfirmPopup(
            self.save_settings,
            id="save_settings",
            obj=self,
            title="Save settings?",
            text="Are you sure you want to overwrite your settings? For a new home directory to take action you have to restart your program!",
        )

        self.infopop = InfoPopup()

    def key_action(self, *args):
        # print(args)

        # Save Entry
        if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
            self.check()

    def help(self, who):
        if who == "home":
            self.infopop.title = "Info"
            self.infopop.text = "This is where all experiments, tex files and PDF files are saved. I don't advice you to change this, however, you can."
            self.infopop.open()

        if who == "stdop":
            self.infopop.title = "Info"
            self.infopop.text = "You can choose your standard user here. Usually, that would be you."
            self.infopop.open()

    def on_enter(self):
        self.ids.stdop.spnfld.text = self.stdop
        self.ids.home.text = self.home
        self.ids.home.focus = True

        Window.bind(on_key_down=self.key_action)

    def on_leave(self, *args):
        Window.unbind(on_key_down=self.key_action)

    def check(self):
        self.savedialog.open()

    def save_settings(self):

        std_set["HOME"] = self.ids.home.text
        std_set["STDOP"] = self.ids.stdop.text
        pickle.dump(std_set, open("../IDEXDATA/DATA/std_settings.pkl", "wb"))

        self.stdop = self.ids.stdop.text
        self.home = self.ids.home.text


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


class LabJournal(Screen, ThemableBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Reactants(Screen, ThemableBehavior):
    rv_reaclist = ListProperty()
    # reactant_dict = DictProperty()
    filter = ObjectProperty()
    container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.reactant_dict = pickle.load(
                open("../IDEXDATA/DATA/reactants.pkl", "rb"))
        except:
            self.reactant_dict = {}

        # create dialogs
        self.infopop = InfoPopup()

        self.savedialog = ConfirmPopup(
            self.save_reactant,
            id="save_reactant",
            obj=self,
            title="Save Reactant?",
            text="This reactant already exists. Are you sure to overwrite it?",
        )

        self.deletedialog = ConfirmPopup(
            self.delete_reactant,
            id="delete_reactant",
            obj=self,
            title="Delete reactant?",
            text="Are you sure to delete this reactant?",
        )

        Clock.schedule_once(lambda dt: self.update_list())
        Clock.schedule_once(lambda dt: self.ids.reac.ids.txtfld.bind(
            text=lambda instance, text: self.fill_M(text)))

    def check(self, *args):
        if "save" in args:
            if not self.ids.reac.txtfld.text or not self.ids.molarmass.txtfld.text:
                self.infopop.title = "Minimum requirements not met"
                self.infopop.text = "You need at least a formula and its molar mass for this action."
                self.infopop.open()
            elif self.ids.reac.txtfld.text in self.reactant_dict:
                self.savedialog.open()
            else:
                self.save_reactant()

        elif "delete" in args:
            if self.ids.reac.txtfld.text not in self.reactant_dict:
                self.infopop.title = "Not found"
                self.infopop.text = "There is no reactant listed with this formula"
                self.infopop.open()

            else:
                self.deletedialog.open()

    def delete_reactant(self):
        self.reactant_dict.pop(self.ids.reac.txtfld.text)
        pickle.dump(self.reactant_dict, open(
            "../IDEXDATA/DATA/reactants.pkl", "wb"))
        self.update_list()
        self.reset()
        self.editor.swi.update_reactants()

    def fill_M(self, formula):
        self.ids.molarmass.txtfld.text = ""
        try:
            c = Substance.from_formula(formula)
            self.ids.molarmass.txtfld.text = "%.4f" % c.mass
        except:
            pass

    def fill_reactant(self, formula):
        dic = self.reactant_dict[formula]

        self.ids.reac.txtfld.text = formula
        self.ids.reac.txtfld.focus = True
        self.ids.molarmass.txtfld.text = dic["Molar Mass"]
        self.ids.tag.txtfld.text = dic["Tag"]
        self.ids.tmelt.txtfld.text = dic["Tmelt"]
        self.ids.tboil.txtfld.text = dic["Tboil"]
        self.ids.tdecomp.txtfld.text = dic["Tdecomp"]

    def key_action(self, *args):
        # print(args)

        # Save Entry
        if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
            self.check("save")

        # Delete Entry Strg + Entf
        if args[1] == 127 and "ctrl" in args[4] and "shift" not in args[4]:
            self.check("delete")

        # Focus Filter
        if args[3] == "f" and "ctrl" in args[4] and "shift" not in args[4]:
            self.ids.filter.focus = True

        # Focus Formula
        if args[3] == "f" and "ctrl" in args[4] and "shift" in args[4]:
            self.ids.reac.txtfld.focus = True

        # New Reactant
        if args[3] == "n" and "ctrl" in args[4] and "shift" not in args[4]:
            self.reset()

        # Scroll DOWN - 274,81 is DOWN
        sci = 0.05  # scroll interval
        if args[1] == 274 and args[2] == 81 and "ctrl" in args[4]:
            scr = self.ids.rv_btns.scroll_y
            scr -= sci
            if scr < 0:
                scr = 0

            self.ids.rv_btns.scroll_y = scr

        # Scroll UP - 273,82 is up
        if args[1] == 273 and args[2] == 82 and "ctrl" in args[4]:
            scr = self.ids.rv_btns.scroll_y
            scr += sci
            if scr > 1:
                scr = 1

            self.ids.rv_btns.scroll_y = scr

    def on_enter(self):
        Window.bind(on_key_down=self.key_action)
        self.ids.reac.txtfld.focus = True

    def on_leave(self, *args):
        Window.unbind(on_key_down=self.key_action)

    def reset(self):
        self.ids.reac.txtfld.text = ""
        self.ids.reac.txtfld.focus = True
        self.ids.molarmass.txtfld.text = ""
        self.ids.tag.txtfld.text = ""
        self.ids.tmelt.txtfld.text = ""
        self.ids.tboil.txtfld.text = ""
        self.ids.tdecomp.txtfld.text = ""

    def save_reactant(self):
        self.reactant_dict[self.ids.reac.txtfld.text] = {
            "Molar Mass": self.ids.molarmass.txtfld.text,
            "Tag": self.ids.tag.txtfld.text,
            "Tmelt": self.ids.tmelt.txtfld.text,
            "Tboil": self.ids.tboil.txtfld.text,
            "Tdecomp": self.ids.tdecomp.txtfld.text
        }

        pickle.dump(self.reactant_dict, open(
            "../IDEXDATA/DATA/reactants.pkl", "wb"))
        self.update_list()
        self.reset()
        self.editor.swi.update_reactants()

    def update_list(self):
        self.rv_reaclist = []

        # Get Search Elements entered by User and split them
        rc_search = self.filter.text

        if rc_search == "":
            search_elements = [""]
        else:
            search_elements_with_empty_strings = rc_search.split(" ")
            search_elements = []
            for i in search_elements_with_empty_strings:
                if i != "":
                    search_elements.append(i)

        # Get all Reactants
        # if os.path.exists("../IDEXDATA/DATA/reactants.pkl"):
        #     self.reactant_dict = pickle.load(open("../IDEXDATA/DATA/reactants.pkl","rb"))
        # else:
        #     self.reactant_dict = {}

        self.reactant_list = self.reactant_dict.keys()
        self.search_result = self.reactant_list

        # Find Hits
        for i in search_elements:
            self.reactant_list = self.search_result
            self.search_result = []
            for j in self.reactant_list:
                if i in j:
                    self.search_result.append(j)
                if i in self.reactant_dict[j]["Tag"]:
                    if j not in self.search_result:
                        self.search_result.append(j)

        self.search_result.sort()

        # Create RecycleView Dicts
        for i in self.search_result:
            # Formatting of the Reactants
            try:
                chemical = chemify(i, 15)
            except:
                chemical = i

            btndict = {}
            btndict["reactants"] = self
            btndict["container"] = self.container
            btndict["reactant"] = chemical
            btndict["entry"] = i
            btndict["tag"] = self.reactant_dict[i]["Tag"]
            btndict["molarmass"] = self.reactant_dict[i]["Molar Mass"]
            btndict["tmelt"] = self.reactant_dict[i]["Tmelt"]
            btndict["tboil"] = self.reactant_dict[i]["Tboil"]
            btndict["tdecomp"] = self.reactant_dict[i]["Tdecomp"]

            self.rv_reaclist.append(btndict)


class Reaction(BoxLayout, ThemableBehavior):
    r = StringProperty()
    p = StringProperty()
    # error = StringProperty()
    editor = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.infopop = InfoPopup(
            title="That did not work!",
            text="Did you catch all the elements on both sides? You can enter the solution also manually."
        )

    def balance_reaction(self):
        self.r = ""
        self.p = ""
        # self.error = ""

        try:
            self.reac = self.ids.reactants.text.split("+")

            self.prod = self.ids.products.text.split("+")

            self.reac, self.prod = balance_stoichiometry(
                self.reac, self.prod, underdetermined=None)
            print(self.reac)
            print(self.prod)
            for i in self.reac:
                if self.reac[i] != 1:
                    n = str(self.reac[i]) + " "
                else:
                    n = ""

                u = chemify(i, self.ids.reactants.txtfld.font_size)
                if i == list(self.reac.keys())[-1]:
                    self.r = self.r + n + u
                else:
                    self.r = self.r + n + u + "   +   "

            for i in self.prod:
                if self.prod[i] != 1:
                    n = str(self.prod[i]) + " "
                else:
                    n = ""

                u = chemify(i, self.ids.reactants.txtfld.font_size)

                if i == list(self.prod.keys())[-1]:
                    self.p = self.p + n + u
                else:
                    self.p = self.p + n + u + "   +   "

        except:
            # self.error = "Could not be calculated. Did you catch all the elements on both sides? You can enter the solution manually."
            self.infopop.open()

            try:
                spltr = self.ids.reactants.text.split(" + ")
                spltp = self.ids.products.text.split(" + ")

                for i in spltr:
                    sr = i.split(" ")
                    if len(sr) == 1:
                        chem = sr[0]
                        n = ""
                    else:
                        chem = sr[1]
                        n = str(sr[0]) + " "

                    u = chemify(chem, self.ids.reactants.txtfld.font_size)
                    if i == spltr[-1]:
                        self.r = self.r + n + u
                    else:
                        self.r = self.r + n + u + "   +   "

                for i in spltp:
                    sp = i.split(" ")
                    if len(sp) == 1:
                        chem = sp[0]
                        n = ""
                    else:
                        chem = sp[1]
                        n = sp[0] + " "

                    u = chemify(chem, self.ids.reactants.font_size)
                    if i == spltp[-1]:
                        self.p = self.p + n + u
                    else:
                        self.p = self.p + n + u + "   +   "

            except:
                self.r = self.ids.reactants.text
                self.p = self.ids.products.text

        print(self.r)
        print(self.p)

    def reset(self):
        self.ids.reactants.txtfld.text = ""
        self.ids.output_reactants.text = ""
        self.ids.products.txtfld.text = ""
        self.ids.output_products.text = ""
        # self.error = ""


class Result(BoxLayout, ThemableBehavior):
    product_grid = ObjectProperty()
    product_rows = ListProperty()
    prev = NumericProperty()
    editor = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_height(self, *args):
        if not self.prev:
            self.prev = 0
        diff = args[1] - self.prev
        self.prev = args[1]
        try:
            self.parent.height += diff
        except:
            pass

    def add_product_row(self):
        identifier = PlainTxtFld(
            _hint_text="e.g. washed with H2O or MD001a",
            size_hint=(0.4, None)
        )
        product = PlainTxtFld(
            _hint_text="e.g. AlN + AlN + AlN",
        )

        self.product_rows.append([identifier, product])

        for i in self.product_rows[-1]:
            self.product_grid.add_widget(i)

    def del_product_row(self):
        if self.product_rows != []:
            for i in self.product_rows[-1]:
                self.product_grid.remove_widget(i)

            self.product_rows.pop(-1)

    def reset(self, *args):
        if "product" in args:
            for i in self.product_rows:
                for j in i:
                    self.ids.product_grid.remove_widget(j)

            self.product_rows = []
            self.ids.identifier.txtfld.text = ""
            self.ids.product.txtfld.text = ""

        if "conclusion" in args:
            self.ids.conclusion.txtfld.text = ""


class SampleWeighin(BoxLayout, ThemableBehavior):
    swi_grid = ObjectProperty()
    swi_rows = ListProperty()
    # error = StringProperty()
    prev = NumericProperty()
    reactants = ListProperty()
    editor = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.infopop = InfoPopup(
            title="That did not work!",
            text="Did you enter 'Net weight'? Please choose your reactant and only use numbers separated by points. (Computers prefer points...)"
        )

        self.update_reactants()
        Clock.schedule_once(lambda dt: self.add_swi_row())

    def delete_selected_row(self, box):
        length = len(self.swi_rows)
        self.swi_grid.remove_widget(box)
        self.swi_rows.remove(box)
        if length < 2:
            self.add_swi_row()

    def move_row_down(self, box):
        i = self.swi_rows
        if box is not self.swi_rows[-1]:
            a, b = i.index(box), i.index(box) + 1
            i[b], i[a] = i[a], i[b]

            self.swi_rows = i

            self.swi_grid.clear_widgets()
            for element in self.swi_rows:
                self.swi_grid.add_widget(element)

    def move_row_up(self, box):
        i = self.swi_rows
        if box is not self.swi_rows[0]:
            a, b = i.index(box), i.index(box) - 1
            i[b], i[a] = i[a], i[b]

            self.swi_rows = i

            self.swi_grid.clear_widgets()
            for element in self.swi_rows:
                self.swi_grid.add_widget(element)

    def on_height(self, *args):
        if not self.prev:
            self.prev = 0
        diff = args[1] - self.prev
        self.prev = args[1]
        try:
            self.parent.height += diff
        except:
            pass

    def update_reactants(self):
        try:
            self.reactant_dict = pickle.load(
                open("../IDEXDATA/DATA/reactants.pkl", "rb"))
        except:
            self.reactant_dict = {}

        self.reactants = []

        for i in self.reactant_dict:
            self.reactants.append(i)

    def fill_M(self, instance, formula):
        instance_row = None
        for n, i in enumerate(self.swi_rows):
            if instance == i.children[5]:
                instance_row = n

        if instance_row != None:
            if formula in self.reactant_dict:
                self.swi_rows[instance_row].children[3].text = self.reactant_dict[formula]["Molar Mass"]
            else:
                self.swi_rows[instance_row].children[3].text = ""

    def add_swi_row(self):
        # instantiate new row_grid
        row_grid = SWIGrid(swi=self)

        # create updnbox
        updnbox = BoxLayout(
            size_hint=(None, None),
            size=(45, 40),
            padding=(2.5, 2.5),
            orientation="vertical"
        )

        upbtn = IcnBtn(
            icon="chevron-up",
            radius=[4, 4, 0, 0],
            on_release=lambda x: self.move_row_up(row_grid)
        )
        dnbtn = IcnBtn(
            icon="chevron-down",
            radius=[0, 0, 4, 4],
            on_release=lambda x: self.move_row_down(row_grid)
        )
        updnbox.add_widget(upbtn)
        updnbox.add_widget(dnbtn)

        # create all txt/lblflds
        reac = TxtOpt(
            _hint_text="e.g. Sr2N",
            swi=self
        )
        eq = PlainTxtFld(
            _hint_text="e.g. 1.0"
        )
        molarmass = PlainTxtFld(
            _hint_text="e.g. 189.25"
        )
        mol = Factory.PlainLabel()
        mass = Factory.PlainLabel()

        # delbtn = DeleteButton(box=row_grid)
        lbl = Label(
            size_hint=(None, None),
            size=(40, 40)
        )

        # append new row_grid to find later
        self.swi_rows.append(row_grid)

        # add all flds to grid
        widget_list = [updnbox, reac, eq, molarmass, mol, mass, lbl]
        for i in widget_list:
            row_grid.add_widget(i)

        # add row_grid to screen
        self.swi_grid.add_widget(row_grid)

    def del_swi_row(self):
        length = len(self.swi_rows)
        self.swi_grid.remove_widget(self.swi_rows[-1])
        self.swi_rows.pop(-1)
        if length < 2:
            self.add_swi_row()

    def calc_swi(self):
        # self.error = ""

        try:

            M_list = []
            eq_list = []
            list_mass = []
            list_mol = []

            # Write all Eq and M of the Ansatz in lists
            for i in self.swi_rows:
                M_list.append(float(i.children[3].text))
                eq_list.append(float(i.children[4].text))

            # Calculate the sumproduct which is the denominator
            Meq_product = [i*j for i, j in zip(M_list, eq_list)]
            Meq_sumproduct = sum(Meq_product)

            # Calculate the results for mass and mol
            for i, j in enumerate(Meq_product):
                result_mass = j / Meq_sumproduct * \
                    float(self.ids.netweight.txtfld.text)
                result_mol = result_mass / M_list[i]
                list_mass.append(result_mass)
                list_mol.append(result_mol)

            # Print the Results to Screen!
            # self.ids.mol.lblfld.text = str("%.2f" % list_mol[0])
            # self.ids.mass.lblfld.text = str("%.2f" % list_mass[0])

            for i, j in enumerate(self.swi_rows):
                j.children[2].text = str("%.2f" % list_mol[i])
                j.children[1].text = str("%.2f" % list_mass[i])

        except ValueError:
            # Error if Reactants not chosen or something else than numbers inserted
            # self.error = "Choose a Reactant and insert only numbers separated by '.'."
            self.infopop.open()

        except ZeroDivisionError:
            print("Ohoh ZeroDivisionError")

    def reset(self, *args):
        if "weighin" in args:
            self.swi_rows = []
            self.swi_grid.clear_widgets()
            self.add_swi_row()

        if "additives" in args:
            self.ids.additives.txtfld.text = ""


class Search(Screen, ThemableBehavior):
    search_txt = ObjectProperty(None)
    results_lyt = ObjectProperty(None)
    home = StringProperty()
    numres = StringProperty("0")
    themedict = {
        "green": [
            55/255, 200/255, 171/255, 1
        ],
        "red": [
            255/255, 85/255, 85/255, 1
        ],
        "blue": [
            42/255, 212/255, 255/255, 1
        ],
        "violet": [
            229/255, 128/255, 255/255, 1
        ],
        "orange": [
            255/255, 153/255, 85/255, 1
        ],
        "yellow": [
            255/255, 221/255, 85/255, 1
        ],
        "grey": [
            222/255, 222/255, 222/255, 1
        ], "cc1_lightblue": [85/255, 221/255, 255/255, 1], "cc1_blue": [42/255, 127/255, 255/255, 1], "cc1_beige": [255/255, 246/255, 213/255, 1], "cc1_green": [43/255, 160/255, 43/255, 1], "cc1_brown": [85/255, 34/255, 0/255, 1], "cc1_turquoise": [0/255, 102/255, 128/255, 1], "cc1_yellow": [255/255, 230/255, 128/255, 1]}
    # colordict = {
    #     "DSC": {"Button": "data/images/cc1_brown.png", "Color": themedict["cc1_brown"], "TextColor": [1,1,1,1]}, "TF": {"Button": "data/images/cc1_turquoise.png", "Color": themedict["cc1_turquoise"], "TextColor": [1,1,1,1]}, "RF": {"Button": "data/images/cc1_yellow.png", "Color": themedict["cc1_yellow"], "TextColor": [0,0,0,1]}, "MP": {"Button": "data/images/cc1_green.png", "Color": themedict["cc1_green"], "TextColor": [1,1,1,1]}, "HIP": {"Button": "data/images/cc1_blue.png", "Color": themedict["cc1_blue"], "TextColor": [1,1,1,1]}, "AS": {"Button": "data/images/cc1_lightblue.png", "Color": themedict["cc1_lightblue"], "TextColor": [0,0,0,1]}}
    abbrev_dict = {
        "Tube Furnace": "TF",
        "RF Furnace": "RF",
        "DSC": "DSC",
        "Multianvil Press": "MP",
        "HIP": "HIP",
        "Ammonothermal": "AS"
    }
    method_dict = DictProperty({
        "Tube Furnace": {
            "RGBA": [0/255, 121/255, 107/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "TF"
        },
        "RF Furnace": {
            "RGBA": [255/255, 171/255, 5/255, 1],
            "RGBATEXT": [0, 0, 0, 1],
            "ABBREV": "RF",
            "HEX": "ffab05"
        },
        "DSC": {
            "RGBA": [105/255, 45/255, 9/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "DSC"
        },
        "Multianvil Press": {
            "RGBA": [0/255, 50/255, 140/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "MAP"
        },
        "HIP": {
            "RGBA": [181/255, 0/255, 16/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "HIP",
            "HEX": "b50010"
        },
        "Ammonothermal": {
            "RGBA": [162/255, 0/255, 188/255, 1],
            "RGBATEXT": [1, 1, 1, 1],
            "ABBREV": "ATS"
        }
    })

    rv_sc = ListProperty()
    results = {}
    container = ObjectProperty()
    editor = ObjectProperty()
    hit_color = StringProperty("b50010")

    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        std_set = pickle.load(open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        # try:
        #     self.home = std_set["Home Directory"]
        # except:
        #     self.home = std_set["HOME"]

        # self.home = home
        # self.ops_list = self.container.ops_list

        self.searchpop = SearchPopup()

    def create_content(self, page, num_of_entries):
        self.ids.gl_search.clear_widgets()

        if len(self.rv_sc) == 0:
            text = "Couldn't find anything..."
            sl_notfound = Label(
                text=text,
                font_size=30,
                size_hint_y=None,
                color=[0.7, 0.7, 0.7, 1],
                height=200
            )

            self.ids.gl_search.add_widget(sl_notfound)
            return

        if page*num_of_entries > len(self.rv_sc):
            rng = range((page-1)*num_of_entries, len(self.rv_sc))
        else:
            rng = range((page-1)*num_of_entries, page*num_of_entries)

        for i in rng:
            svc = SearchViewClass(
                op=self.rv_sc[i]["op"],
                sid=self.rv_sc[i]["sid"],
                tag=self.rv_sc[i]["tag"],
                trgt=self.rv_sc[i]["trgt"],
                search_elements=self.search_elements,
                method_abbrev=self.rv_sc[i]["method_abbrev"],
                method_color=self.rv_sc[i]["method_color"],
                method_color_text=self.rv_sc[i]["method_color_text"],
                search=self,
                searchpop=self.searchpop,
                editor=self.editor
            )

            for j, k in enumerate(self.rv_sc[i]["strlist"]):
                if j < 4:
                    sl_title = Factory.SearchLabel1(text=k[0], bold=True)
                    sl_cont = Factory.SearchLabel2(text=k[1])
                    svc.ids.gl_res.add_widget(sl_title)
                    svc.ids.gl_res.add_widget(sl_cont)

                elif j == 4:
                    sl_title = Factory.SearchLabel1()
                    sl_cont = Factory.SearchLabel2(text="[...]")
                    svc.ids.gl_res.add_widget(sl_title)
                    svc.ids.gl_res.add_widget(sl_cont)

            self.ids.gl_search.add_widget(svc)

    def create_results(self):
        self.rv_sc = []
        for i in self.results:
            try:
                exp_dict = pickle.load(
                    open(home + "/" + i + "/" + i + "_experiments.idx", "rb"))
            except:
                exp_dict = {}

            for j in self.results[i]:  # j is the Sample-ID
                str_list = []
                info_dict = exp_dict[j]["INFORMATION"]
                reac_dict = exp_dict[j]["REACTION"]
                swi_dict = exp_dict[j]["SWI"]["REACTANTS"]
                tp_dict = exp_dict[j]["TP"]
                expdet_txt = exp_dict[j]["TP"]["EXPERIMENTAL DETAILS"]
                ana_dict = exp_dict[j]["ANALYTICS"]
                res_dict = exp_dict[j]["RESULT"]
                ap_txt = exp_dict[j]["ANALYTICS"]["APPEARANCE"]
                prod_list = exp_dict[j]["RESULT"]["PRODUCTS"]
                concl_txt = exp_dict[j]["RESULT"]["CONCLUSION"]

                met = tp_dict["METHOD"]["Method"]
                method_abbrev = self.method_dict[met]["ABBREV"]

                hits = self.results[i][j]

                trgt = chemify(info_dict["TARGET"], 20)

                rv_dict = {
                    "op": i,
                    "sid": j,
                    "tag": info_dict["TAG"],
                    "trgt": trgt,
                    "method_abbrev": self.method_dict[met]["ABBREV"],
                    "method_color": self.method_dict[met]["RGBA"],
                    "method_color_text": self.method_dict[met]["RGBATEXT"],
                }

                if "info" in hits:
                    idea = info_dict["IDEA"]
                    notaddedyet = True
                    for f in self.search_elements:
                        if f in idea and notaddedyet:
                            splt = idea.split(f, 1)
                            if len(splt[0]) > 60:
                                idea = "[...]" + splt[0][-60:]
                            else:
                                idea = splt[0]

                            if len(splt[1]) > 60:
                                idea += f + splt[1][:60] + "[...]"
                            else:
                                idea += f + splt[1]

                            notaddedyet = False

                            idea = idea.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        else:
                            idea = idea.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Idea:", idea])

                if "reaction" in hits:
                    try:
                        reacstr = reac_dict["REACTANTSBAL"] + \
                            "    -->    " + reac_dict["PRODUCTSBAL"]
                    except:
                        reacstr = reac_dict["REACTANTS"] + \
                            "    -->    " + reac_dict["PRODUCTS"]

                    for f in self.search_elements:
                        trgt = chemify(f, 16)

                        if trgt in reacstr:
                            reacstr = reacstr.replace(
                                trgt, f"[color={self.hit_color}]" + trgt + "[/color]")

                    # reacstr = reacstr.replace("12sp","10sp")
                    str_list.append(["Reaction:", reacstr])

                rceq_list = ""
                if "swi" in hits:
                    for m in swi_dict:
                        if m["REACTANT"] != "":
                            trgt = chemify(m["REACTANT"], 15)

                            if m == swi_dict[-1]:
                                rceq_list = rceq_list + trgt + \
                                    " (" + m["EQUIVALENT"] + ")"
                            else:
                                rceq_list = rceq_list + trgt + \
                                    " (" + m["EQUIVALENT"] + "),   "

                    for f in self.search_elements:
                        trgt = chemify(f, 15)

                        if trgt in rceq_list:
                            rceq_list = rceq_list.replace(
                                trgt, f"[color={self.hit_color}]" + trgt + "[/color]")

                    str_list.append(["Reactants:", rceq_list])

                meth_str = ""
                if "method" in hits:
                    x = tp_dict["METHOD"]
                    chem_list = ["Atmo", "Atmosphere", "Crucible", "Liner"]
                    for n in x:
                        if n in chem_list:
                            val = chemify(x[n], 15)
                        else:
                            val = x[n]

                        if n == list(x.keys())[0] or not meth_str and val:
                            meth_str = val
                        elif val and meth_str:
                            meth_str = meth_str + ",   " + val
                        # elif val:
                        #     meth_str = val

                    for f in self.search_elements:
                        fchem = chemify(f, 15)
                        if f in meth_str:
                            meth_str = meth_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        elif fchem in meth_str:
                            meth_str = meth_str.replace(
                                fchem, f"[color={self.hit_color}]" + fchem + "[/color]")

                    str_list.append(["Method:", meth_str])

                tp_str = ""
                if "program" in hits:
                    for m in tp_dict["PROGRAM"]:
                        for n in m.values():
                            if n == "":
                                if n is not list(m.values())[-1]:
                                    tp_str = tp_str + " - | "
                                else:
                                    tp_str = tp_str + " - "

                            elif n is not list(m.values())[-1]:
                                tp_str = tp_str + n + " | "
                            else:
                                tp_str = tp_str + n

                        for f in self.search_elements:
                            if f in tp_str:
                                tp_str = tp_str.replace(
                                    f, f"[color={self.hit_color}]" + f + "[/color]")

                        if m is not tp_dict["PROGRAM"][-1]:
                            tp_str = tp_str + "     -->     "

                    str_list.append(["Program:", tp_str])

                expdet_str = ""
                if "expdet" in hits:
                    expdet_str = expdet_txt
                    notaddedyet = True
                    for f in self.search_elements:
                        if f in expdet_str and notaddedyet:
                            splt = expdet_str.split(f, 1)
                            if len(splt[0]) > 60:
                                expdet_str = "[...]" + splt[0][-60:]
                            else:
                                expdet_str = splt[0]

                            if len(splt[1]) > 60:
                                expdet_str += f + splt[1][:60] + "[...]"
                            else:
                                expdet_str += f + splt[1]

                            notaddedyet = False

                            expdet_str = expdet_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        else:
                            expdet_str = expdet_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Exp. Det.:", expdet_str])

                if "ap" in hits:
                    ap_str = ap_txt
                    notaddedyet = True
                    for f in self.search_elements:
                        if f in ap_str and notaddedyet:
                            splt = ap_str.split(f, 1)
                            if len(splt[0]) > 60:
                                ap_str = "[...]" + splt[0][-60:]
                            else:
                                ap_str = splt[0]

                            if len(splt[1]) > 60:
                                ap_str += f + splt[1][:60] + "[...]"
                            else:
                                ap_str += f + splt[1]

                            notaddedyet = False

                            ap_str = ap_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        else:
                            ap_str = ap_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Appearance:", ap_str])

                anamet_str = ""
                if "anamet" in hits:
                    for n in ana_dict["METHODS"]:
                        if ana_dict["METHODS"][n]:
                            if anamet_str:
                                anamet_str = anamet_str + ",   " + n
                            else:
                                anamet_str = n

                    for f in self.search_elements:
                        if f in anamet_str:
                            anamet_str = anamet_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Analytics:", anamet_str])

                if "anadet" in hits:
                    anadet_str = ana_dict["ANALYTICAL DETAILS"]
                    notaddedyet = True
                    for f in self.search_elements:
                        if f in anadet_str and notaddedyet:
                            splt = anadet_str.split(f, 1)
                            if len(splt[0]) > 60:
                                anadet_str = "[...]" + splt[0][-60:]
                            else:
                                anadet_str = splt[0]

                            if len(splt[1]) > 60:
                                anadet_str += f + splt[1][:60] + "[...]"
                            else:
                                anadet_str += f + splt[1]

                            notaddedyet = False

                            anadet_str = anadet_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        else:
                            anadet_str = anadet_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Ana. Det.:", anadet_str])

                prod_str = ""
                if "prod" in hits:
                    for n in prod_list:
                        if n["PRODUCT"]:
                            prods = ""
                            splt = n["PRODUCT"].split("+")
                            for s in splt:
                                trgt = chemify(s, 15)
                                if s is not splt[-1]:
                                    prods += trgt + " + "
                                else:
                                    prods += trgt

                            idf = n["IDENTIFIER"]
                            if idf and n == prod_list[-1]:
                                prod_str = prod_str + idf + ":   " + prods
                            elif idf:
                                prod_str = prod_str + idf + ":   " + prods + ",   "
                            elif n == prod_list[-1]:
                                prod_str = prod_str + prods
                            else:
                                prod_str = prod_str + prods + ",   "

                    if prod_str:
                        for f in self.search_elements:
                            trgt = chemify(f, 15)
                            if f in prod_str:
                                prod_str = prod_str.replace(
                                    f, f"[color={self.hit_color}]" + f + "[/color]")

                            elif trgt in prod_str:
                                prod_str = prod_str.replace(
                                    trgt, f"[color={self.hit_color}]" + trgt + "[/color]")

                        str_list.append(["Products:", prod_str])

                if "concl" in hits:
                    concl_str = concl_txt
                    notaddedyet = True
                    for f in self.search_elements:
                        if f in concl_str and notaddedyet:
                            splt = concl_str.split(f, 1)
                            if len(splt[0]) > 60:
                                concl_str = "[...]" + splt[0][-60:]
                            else:
                                concl_str = splt[0]

                            if len(splt[1]) > 60:
                                concl_str += f + splt[1][:60] + "[...]"
                            else:
                                concl_str += f + splt[1]

                            notaddedyet = False

                            concl_str = concl_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                        else:
                            concl_str = concl_str.replace(
                                f, f"[color={self.hit_color}]" + f + "[/color]")

                    str_list.append(["Conclusion:", concl_str])

                rv_dict["strlist"] = str_list

                self.rv_sc.append(rv_dict)
        # print(self.rv_sc)
        # return
        print(len(self.rv_sc))
        if len(self.rv_sc) < 100:
            self.numres = str(len(self.rv_sc))
        else:
            self.numres = "99+"

        btn_list = []

        if len(self.rv_sc) % 10 == 0:
            rng = int(len(self.rv_sc)/10)
        else:
            rng = int(len(self.rv_sc)/10)+1

        if rng:
            for i in range(rng):
                if i < 10:
                    btn = PageToggler(
                        text=str(i+1),
                    )
                    btn.bind(on_release=lambda instance: self.create_content(
                        int(instance.text), 10))
                    btn_list.append(btn)
                    self.ids.pagebtns.add_widget(btn)

        else:
            btn = PageToggler(
                text=str(1),
            )
            btn.bind(on_release=lambda instance: self.create_content(
                int(instance.text), 10))
            btn_list.append(btn)
            self.ids.pagebtns.add_widget(btn)

        btn_list[0].state = "down"
        self.create_content(1, 10)

    def key_action(self, *args):
        # print(args)

        # Focus Filter
        if args[3] == "f" and "ctrl" in args[4] and "shift" not in args[4]:
            self.ids.filter.focus = True

        # New Reactant
        if args[3] == "n" and "ctrl" in args[4] and "shift" not in args[4]:
            self.reset()

        # Scroll DOWN - 274,81 is DOWN
        sci = 0.05  # scroll interval
        if args[1] == 274 and args[2] == 81 and "ctrl" in args[4]:
            scr = self.ids.sv_search.scroll_y
            scr -= sci
            if scr < 0:
                scr = 0

            self.ids.sv_search.scroll_y = scr

        # Scroll UP - 273,82 is up
        if args[1] == 273 and args[2] == 82 and "ctrl" in args[4]:
            scr = self.ids.sv_search.scroll_y
            scr += sci
            if scr > 1:
                scr = 1

            self.ids.sv_search.scroll_y = scr

    def on_enter(self, *args):
        self.ids.filter.focus = True
        Window.bind(on_key_down=self.key_action)

    def on_leave(self, *args):
        Window.unbind(on_key_down=self.key_action)

    def reset(self):
        self.ids.filter.text = ""
        self.ids.filter.focus = True

    def search_module(self, input):
        self.ids.pagebtns.clear_widgets()

        self.search_elements = []
        if input != "":
            search_elements_with_empty_strings = input.split(" ")
            for i in search_elements_with_empty_strings:
                if i != "":
                    self.search_elements.append(i)

        op_list = self.editor.ops_list

        # print(op_list)
        # return
        # self.results = []

        for i in op_list:
            try:
                exp_dict = pickle.load(
                    open(home + "/" + i + "/" + i + "_experiments.idx", "rb"))
            except:
                exp_dict = {}

            search_results = list(exp_dict.keys())
            search_results.sort(reverse=True)

            # info_searchables = ["Target","Sample-ID","Tag","Operator","Date","Idea"]
            reac_searchables = ["REACTANTS", "PRODUCTS"]

            results_dict = {}

            for f in self.search_elements:
                search_ids = search_results
                search_results = []
                for j in search_ids:
                    if j not in results_dict:
                        results_dict[j] = []

                    # where_match = []
                    info_dict = exp_dict[j]["INFORMATION"]
                    reac_dict = exp_dict[j]["REACTION"]
                    swi_dict = exp_dict[j]["SWI"]["REACTANTS"]
                    tp_dict = exp_dict[j]["TP"]
                    expdet_txt = exp_dict[j]["TP"]["EXPERIMENTAL DETAILS"]
                    ana_dict = exp_dict[j]["ANALYTICS"]
                    res_dict = exp_dict[j]["RESULT"]
                    ap_txt = exp_dict[j]["ANALYTICS"]["APPEARANCE"]
                    prod_list = exp_dict[j]["RESULT"]["PRODUCTS"]
                    concl_txt = exp_dict[j]["RESULT"]["CONCLUSION"]

                    for l in info_dict:
                        if f in info_dict[l] or f in i:
                            results_dict[j].append("info")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    for l in reac_searchables:
                        if f in reac_dict[l]:
                            results_dict[j].append("reaction")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    for l in swi_dict:
                        if f in l["REACTANT"]:
                            results_dict[j].append("swi")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    for l in tp_dict["METHOD"]:
                        if f in tp_dict["METHOD"][l]:
                            results_dict[j].append("method")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    for l in tp_dict["PROGRAM"]:
                        if f in l["TEND"]:
                            results_dict[j].append("program")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    if f in expdet_txt:
                        results_dict[j].append("expdet")
                        if j not in search_results:
                            search_results.append(j)

                    for l in ana_dict["METHODS"]:
                        if f in l and ana_dict["METHODS"][l]:
                            results_dict[j].append("anamet")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    if f in ana_dict["ANALYTICAL DETAILS"]:
                        results_dict[j].append("anadet")
                        if j not in search_results:
                            search_results.append(j)

                    if f in ap_txt:
                        results_dict[j].append("ap")
                        if j not in search_results:
                            search_results.append(j)

                    for l in prod_list:
                        if f in l["PRODUCT"] or f in l["IDENTIFIER"] and l["PRODUCT"]:
                            results_dict[j].append("prod")
                            if j not in search_results:
                                search_results.append(j)
                            break

                    if f in concl_txt:
                        results_dict[j].append("concl")
                        if j not in search_results:
                            search_results.append(j)

            # this removes all empty entries in the results_dict
            for k in list(results_dict):
                if not results_dict[k] or k not in search_results:
                    del results_dict[k]

            self.results[i] = results_dict

        # print(self.results)
        self.create_results()

    def setattrs(self, _self, **kwargs):
        for k, v in kwargs.items():
            setattr(_self, k, v)

        setattr(_self, "container", self.container)


class TempProg(BoxLayout, ThemableBehavior):
    method_grid = ObjectProperty()
    method_parameters = ListProperty()
    method_items = ListProperty()
    tp_grid = ObjectProperty()
    tp_rows = ListProperty()
    prev = NumericProperty()
    editor = ObjectProperty()
    methods = DictProperty({
        "Tube Furnace": {
            "Method ID": {
                "_hint_text": "e.g. C4",
                "_btmlbl": "e.g. C4"
            },
            "Crucible": {
                "_hint_text": "e.g. Ta, W, Al2O3",
                "_btmlbl": "e.g. Ta, W, Al2O3"
            },
            "Atmosphere": {
                "_hint_text": "e.g. Vacuum, N2, Ar",
                "_btmlbl": "e.g. Vacuum, N2, Ar"
            }
        },
        "RF Furnace": {
            "Method ID": {
                "_hint_text": "e.g. Bonnie, Clyde",
                "_btmlbl": "e.g. Bonnie, Clyde"
            },
            "Crucible": {
                "_hint_text": "e.g. Ta, W",
                "_btmlbl": "e.g. Ta, W"
            },
            "Atmosphere": {
                "_hint_text": "e.g. Vacuum, N2, Ar",
                "_btmlbl": "e.g. Vacuum, N2, Ar"
            }
        },
        "DSC": {
            "Modus": {
                "_hint_text": "e.g. TG, DSC, TG/DSC",
                "_btmlbl": "e.g. TG, DSC, TG/DSC"
            },
            "Crucible": {
                "_hint_text": "e.g. Ta, Al2O3, Cu",
                "_btmlbl": "e.g. Ta, Al2O3, Cu"
            },
            "Atmosphere": {
                "_hint_text": "e.g. Ar",
                "_btmlbl": "e.g. Ar"
            },
            "Gas Flow": {
                "_hint_text": "e.g. 5 ml/min",
                "_btmlbl": "e.g. 5 ml/min"
            }
        },
        "HIP": {
            "Method ID": {
                "_hint_text": "e.g. hippo",
                "_btmlbl": "e.g. hippo"
            },
            "Crucible": {
                "_hint_text": "e.g. W",
                "_btmlbl": "e.g. W"
            },
            "Atmosphere": {
                "_hint_text": "e.g. Ar, N2",
                "_btmlbl": "e.g. Ar, N2"
            },
            "Pressure": {
                "_hint_text": "e.g. 150 MPa",
                "_btmlbl": "e.g. 150 MPa"
            },
            "Ansatz No.": {
                "_hint_text": "e.g. 520",
                "_btmlbl": "e.g. 520"
            },
        },
        "Multianvil Press": {
            "Method ID": {
                "_hint_text": "e.g. old, new",
                "_btmlbl": "e.g. old, new"
            },
            "Crucible": {
                "_hint_text": "e.g. BN, Ta-Inlay",
                "_btmlbl": "e.g. BN, Ta-Inlay"
            },
            "Size": {
                "_hint_text": "e.g. 14/8, 18/11",
                "_btmlbl": "e.g. 14/8, 18/11"
            },
            "Pressure": {
                "_hint_text": "e.g. 5 GPa",
                "_btmlbl": "e.g. 5 GPa"
            },
            "Oil Pressure": {
                "_hint_text": "e.g. 230 bar",
                "_btmlbl": "e.g. 230 bar"
            },
            "Heating Capacity": {
                "_hint_text": "e.g. 24 %",
                "_btmlbl": "e.g. 24 %"
            }
        },
        "Ammonothermal": {
            "Autoclave": {
                "_hint_text": "e.g. 2010-002",
                "_btmlbl": "e.g. 2010-002"
            },
            "V(Autoclave)": {
                "_hint_text": "e.g. 93 ml",
                "_btmlbl": "e.g. 93 ml"
            },
            "Liner": {
                "_hint_text": "e.g. Si3N4",
                "_btmlbl": "e.g. Si3N4"
            },
            "V(NH[sub][size=10.5sp]3[/size][/sub])": {
                "_hint_text": "e.g. 9000 l",
                "_btmlbl": "e.g. 9000 l"
            },
            "Pressure": {
                "_hint_text": "e.g. 50 bar",
                "_btmlbl": "e.g. 50 bar"
            }
        }
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in self.methods:
            self.method_items.append(i)

    def on_height(self, *args):
        if not self.prev:
            self.prev = 0
        diff = args[1] - self.prev
        self.prev = args[1]
        try:
            self.parent.height += diff
        except:
            pass

    def change_method(self, method):
        if method not in self.methods:
            return

        if self.method_parameters != []:
            for i in self.method_parameters:
                self.method_grid.remove_widget(i)

            self.method_parameters = []

        method_dict = self.methods[method]
        for i in method_dict:
            parameter = TextBox(
                _lbl=i,
                _hint_text=method_dict[i]["_hint_text"],
                _btmlbl=method_dict[i]["_btmlbl"]
            )

            self.method_parameters.append(parameter)
            self.method_grid.add_widget(parameter)

    def add_tp_row(self):
        segno = len(self.tp_rows) + 2
        seg = Label(
            text=str(segno),
            size_hint_x=None,
            width=10
        )
        tstart = PlainTxtFld()
        ramp = PlainTxtFld()
        tend = PlainTxtFld()
        dwell = PlainTxtFld()

        self.tp_rows.append([seg, tstart, ramp, tend, dwell])

        for i in self.tp_rows[-1]:
            self.tp_grid.add_widget(i)

    def del_tp_row(self):
        if self.tp_rows != []:
            for i in self.tp_rows[-1]:
                self.tp_grid.remove_widget(i)

            self.tp_rows.pop(-1)

    def reset(self, *args):
        if "method" in args:
            self.ids.method.spnfld.text = "DSC"
            self.ids.method.spnfld.text = "Tube Furnace"

        if "expdet" in args:
            self.ids.expdet.txtfld.text = ""

        if "program" in args:
            for i in self.tp_rows:
                for j in i:
                    self.ids.tp_grid.remove_widget(j)
            self.tp_rows = []
            self.ids.tstart.text = ""
            self.ids.ramp.text = ""
            self.ids.tend.text = ""
            self.ids.dwell.text = ""


class TestNavigationDrawer(MDApp):
    color = StringProperty("Teal")

    def build(self):
        self.title = "IDEX - Inorganic Database for Experiments"
        # self.icon="data/images/icon_yellow_randlos.png"

        self.theme_cls.primary_palette = self.color
        # self.theme_cls.accent_palette = color
        self.theme_cls.primary_hue = "700"
        Window.bind(on_key_down=self.key_action)
        self.cntr = Container()
        return self.cntr

    def key_action(self, *args):

        # Ctrl + Bild ab --> Switch between Tabs
        if args[1] == 281 and args[2] == 78 and "ctrl" in args[4]:
            self.cntr.sm.current = self.cntr.sm.next()

        # Ctrl + Bild ab --> Switch between Tabs
        if args[1] == 280 and args[2] == 75 and "ctrl" in args[4]:
            self.cntr.sm.current = self.cntr.sm.previous()

        # Focus to find Reactants or Search
        if args[3] == "f" and "ctrl" in args[4] and "shift" not in args[4]:
            if self.cntr.sm.current == "reactants":
                self.cntr.ids.reactants.ids.filter.focus = True

        if self.cntr.sm.current == "settings":
            # Save Entry
            if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
                self.cntr.ids.settings.check()
        #
        # if self.cntr.sm.current == "reactants":
        #     if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
        #         self.cntr.ids.reactants.check("save")


class User(Screen, ThemableBehavior):
    # ops_list = ListProperty()
    ops_dict = {}
    userlist = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.infopop = InfoPopup()

        self.savedialog = ConfirmPopup(
            self.save_user,
            id="save_user",
            obj=self,
            title="Save operator?",
            text="This operator already exists. Are you sure to overwrite them?",
        )

        self.deletedialog = ConfirmPopup(
            self.delete_user,
            id="delete_user",
            obj=self,
            title="Delete operator?",
            text="Are you sure to delete this operator and all his files?",
        )
        self.settings_dict = pickle.load(
            open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        self.ops_dict = self.settings_dict["OPERATOR"]

        Clock.schedule_once(lambda dt: self.user_btns())

    def check(self, *args):
        if self.ids.abbrev.txtfld.text == "XDEF":
            self.infopop.title = "Warning"
            self.infopop.text = "You can't change or delete the default user. Please create your own user."
            self.infopop.open()

        elif self.ids.abbrev.txtfld.text == "XXXX":
            self.infopop.title = "Warning"
            self.infopop.text = "You can't change or delete IDEAS. Please create a new 'IDEAS' user if that is necessary, e.g. 'IDEAS Marwin (IMD)'"
            self.infopop.open()

        else:

            if "save" in args:
                if not self.ids.givenname.txtfld.text or not self.ids.abbrev.txtfld.text or not self.ids.lastname.txtfld.text:
                    self.infopop.title = "Minimum requirements not met"
                    self.infopop.text = "Please fill all fields."
                    self.infopop.open()
                elif self.ids.abbrev.txtfld.text in self.ops_dict:
                    self.savedialog.open()
                else:
                    self.save_user()

            elif "delete" in args:
                if self.ids.abbrev.txtfld.text not in self.ops_dict:
                    self.infopop.title = "Not found"
                    self.infopop.text = "There is no operator listed with this name."
                    self.infopop.open()

                else:
                    self.deletedialog.open()

    def user_btns(self):
        self.userlist = []
        self.user = []

        for i in self.ops_dict:
            operator = self.ops_dict[i]["givenname"] + " " + \
                self.ops_dict[i]["lastname"] + " (" + i + ")"
            self.user.append(operator)

        self.user.sort()

        # Get Search Input and split it into search elements (if sampleid and Tag is given)
        btn_search = self.ids.filter.text

        if btn_search == "":
            search_elements = [""]
        else:
            search_elements_with_empty_strings = btn_search.split(" ")
            search_elements = []
            for i in search_elements_with_empty_strings:
                if i != "":
                    search_elements.append(i)

        self.search_result = self.user

        for i in search_elements:
            self.user = self.search_result
            self.search_result = []
            for j in self.user:
                if i in j:
                    self.search_result.append(j)

        for i in self.search_result:
            btndict = {
                "user": i
            }
            self.userlist.append(btndict)

    def new_user(self):
        self.ids.givenname.txtfld.text = ""
        self.ids.givenname.txtfld.focus = True
        self.ids.lastname.txtfld.text = ""
        self.ids.abbrev.txtfld.text = ""
        # self.ids.haircolor.txtfld.text = ""
        # self.ids.favmovie.txtfld.text = ""

    def fill_user(self, user):
        name = user.split(" (")[0]
        abbrev = user.split("(")[1].split(")")[0]

        usr = self.ops_dict[abbrev]

        self.ids.givenname.txtfld.text = usr["givenname"]
        self.ids.lastname.txtfld.text = usr["lastname"]
        self.ids.abbrev.txtfld.text = usr["abbrev"]
        # self.ids.haircolor.txtfld.text = usr["haircolor"]
        # self.ids.favmovie.txtfld.text = usr["favmovie"]

        self.ids.givenname.txtfld.focus = True

    def save_user(self):
        user_dict = {
            "givenname": self.ids.givenname.txtfld.text,
            "lastname": self.ids.lastname.txtfld.text,
            "abbrev": self.ids.abbrev.txtfld.text,
        }

        self.ops_dict[self.ids.abbrev.txtfld.text] = user_dict
        self.settings_dict["OPERATOR"] = self.ops_dict
        print(self.ops_dict)
        pickle.dump(self.settings_dict, open(
            "../IDEXDATA/DATA/std_settings.pkl", "wb"))
        self.user_btns()
        self.new_user()
        self.update_ops()

        self.op = user_dict["givenname"] + " " + \
            user_dict["lastname"] + " " + "(" + user_dict["abbrev"] + ")"

        if not os.path.exists(home + "/" + self.op):
            os.makedirs(home + "/" + self.op)
        if not os.path.exists(home + "/" + self.op + "/pdf"):
            os.makedirs(home + "/" + self.op + "/pdf")
        if not os.path.exists(home + "/" + self.op + "/tex"):
            os.makedirs(home + "/" + self.op + "/tex")
        if not os.path.exists(home + "/" + self.op + "/" + self.op + "_experiments.idx"):
            f = open(home + "/" + self.op + "/" +
                     self.op + "_experiments.idx", "w")

    def delete_user(self):
        self.ops_dict.pop(self.ids.abbrev.txtfld.text)

        self.settings_dict["OPERATOR"] = self.ops_dict
        pickle.dump(self.settings_dict, open(
            "../IDEXDATA/DATA/std_settings.pkl", "wb"))

        self.new_user()
        self.user_btns()
        self.update_ops()

    def key_action(self, *args):
        # print(args)

        # Save Entry
        if args[3] == "s" and "ctrl" in args[4] and "shift" not in args[4]:
            self.check("save")

        # Delete Entry Strg + Entf
        if args[1] == 127 and "ctrl" in args[4] and "shift" not in args[4]:
            self.check("delete")

        # Focus Filter
        if args[3] == "f" and "ctrl" in args[4] and "shift" not in args[4]:
            self.ids.filter.focus = True

        # New Reactant
        if args[3] == "n" and "ctrl" in args[4] and "shift" not in args[4]:
            self.new_user()

    def on_enter(self):
        Window.bind(on_key_down=self.key_action)
        self.ids.givenname.txtfld.focus = True
        self.settings_dict = pickle.load(
            open("../IDEXDATA/DATA/std_settings.pkl", "rb"))
        self.ops_dict = self.settings_dict["OPERATOR"]

    def on_leave(self, *args):
        Window.unbind(on_key_down=self.key_action)

    def update_ops(self):
        ops_list = []
        for i in self.ops_dict:
            ops_list.append(
                self.ops_dict[i]["givenname"] + " " + self.ops_dict[i]["lastname"] + " (" + i + ")")

        ops_list.sort()
        self.container.ops_list = ops_list
        self.settings.ops_list = ops_list


TestNavigationDrawer().run()
