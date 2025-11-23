import os
import pickle

from information_module import Information
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior
from reaction_module import Reaction
from result_module import Result
from sample_weighin_module import SampleWeighin
from tempprog_module import TempProg

from analytics_module import Analytics
from tex import create_pdf, create_tex  # Assuming these are in tex.py
from Widgets import ConfirmPopup, InfoPopup, Panel  # Assuming these are in Widgets.py

# Assuming home and stdop are defined elsewhere or passed as arguments
# For now, let's define them here for the module to be self-contained
# You might need to adjust this based on your project structure
try:
    std_set = pickle.load(open("assets/std_settings.pkl", "rb"))
    home = std_set["HOME"]
    stdop = std_set["STDOP"]
except:
    home = "IDEXDATA"
    stdop = "Default User (XDEF)"


def chemify(text, size):
    # This is a placeholder for your actual chemify function
    # You'll need to import or define it properly
    return text


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
    method_dict = DictProperty(
        {
            "Tube Furnace": {
                "RGBA": [0 / 255, 121 / 255, 107 / 255, 1],
                "RGBATEXT": [1, 1, 1, 1],
                "ABBREV": "TF",
            },
            "RF Furnace": {
                "RGBA": [255 / 255, 171 / 255, 5 / 255, 1],
                "RGBATEXT": [0, 0, 0, 1],
                "ABBREV": "RF",
            },
            "DSC": {
                "RGBA": [105 / 255, 45 / 255, 9 / 255, 1],
                "RGBATEXT": [1, 1, 1, 1],
                "ABBREV": "DSC",
            },
            "Multianvil Press": {
                "RGBA": [0 / 255, 50 / 255, 140 / 255, 1],
                "RGBATEXT": [1, 1, 1, 1],
                "ABBREV": "MAP",
            },
            "HIP": {
                "RGBA": [181 / 255, 0 / 255, 16 / 255, 1],
                "RGBATEXT": [1, 1, 1, 1],
                "ABBREV": "HIP",
            },
            "Ammonothermal": {
                "RGBA": [162 / 255, 0 / 255, 188 / 255, 1],
                "RGBATEXT": [1, 1, 1, 1],
                "ABBREV": "ATS",
            },
        }
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.ops_list = os.listdir(home)
        except:
            self.ops_list = ["No OPs found"]

        try:
            self.expdict = pickle.load(
                open(home + "/" + stdop + "/" + stdop + "_experiments.idx", "rb")
            )
        except:
            self.expdict = {}

        self.info = Information(editor=self)
        self.reaction = Reaction(editor=self)
        self.swi = SampleWeighin(editor=self)
        self.tp = TempProg(editor=self)
        self.ana = Analytics(editor=self)
        self.res = Result(editor=self)

        self.infopop = InfoPopup()
        self.savedialog = ConfirmPopup(
            self.save_entry,
            id="save",
            obj=self,
            title="Save Entry?",
            text="This entry already exists. Are you sure to overwrite it?",
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

        Clock.schedule_once(lambda dt: setattr(self.ids.exp_op, "_starttext", stdop))
        Clock.schedule_once(lambda dt: self.create_modules())
        Clock.schedule_once(lambda dt: self.sample_btns())
        Clock.schedule_once(lambda dt: self.info_panel.open())

    def change_operator(self, op):
        self.op = op
        op_path = os.path.join(home, self.op)
        if not os.path.exists(op_path):
            os.makedirs(op_path)
        if not os.path.exists(os.path.join(op_path, "pdf")):
            os.makedirs(os.path.join(op_path, "pdf"))
        if not os.path.exists(os.path.join(op_path, "tex")):
            os.makedirs(os.path.join(op_path, "tex"))

        exp_file_path = os.path.join(op_path, f"{self.op}_experiments.idx")
        try:
            with open(exp_file_path, "rb") as f:
                self.expdict = pickle.load(f)
        except FileNotFoundError:
            self.expdict = {}
            with open(exp_file_path, "wb") as f:
                pickle.dump(self.expdict, f)  # Create an empty file if it doesn't exist
        except Exception as e:
            print(f"Error loading experiment file: {e}")
            self.expdict = {}

        self.ops_list = os.listdir(home)
        try:
            self.ops_list.remove("DATA")
        except ValueError:
            pass

    def change_title(self):
        sid = self.info.ids.sid.txtfld.text
        tag = self.info.ids.tag.txtfld.text
        trgt = chemify(self.info.ids.trgt.txtfld.text, 30)

        self.title = f"{sid if sid else '-'}   |   {tag if tag else '-'}   |   {trgt if trgt else '-'}"

    def check_for_file(self, *args):
        self.sid = self.info.ids.sid.txtfld.text
        if not self.sid:
            self.infopop.title = "Please enter a sample ID first"
            self.infopop.text = "You need at least a sample ID for this function."
            self.infopop.open()
            return

        if "save" in args:
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
            pdf_path = os.path.join(home, self.op, "pdf", f"{self.sid}.pdf")
            if os.path.exists(pdf_path):
                self.pdfdialog.open()
            elif self.sid in self.expdict:
                self.make_pdf()
            else:
                self.infopop.title = "Save this entry first!"
                self.infopop.text = (
                    "You need to save your entry before you can create the PDF file."
                )
                self.infopop.open()

    def close_all_panels(self):
        for module in self.modules:
            module.close()

    def create_modules(self):
        self.info_panel = Panel(
            content=self.info, icon="information-outline", title="Information"
        )
        self.reaction_panel = Panel(
            content=self.reaction, icon="react", title="Reaction"
        )
        self.swi_panel = Panel(
            content=self.swi, icon="scale-balance", title="Sample Weigh-in"
        )
        self.tp_panel = Panel(
            content=self.tp, icon="stove", title="Method and Temperature Program"
        )
        self.ana_panel = Panel(content=self.ana, icon="chart-bar", title="Analytics")
        self.res_panel = Panel(
            content=self.res, icon="clipboard-check-outline", title="Results"
        )

        self.modules = [
            self.info_panel,
            self.reaction_panel,
            self.swi_panel,
            self.tp_panel,
            self.ana_panel,
            self.res_panel,
        ]
        for module in self.modules:
            self.ids.modules.add_widget(module)

    def make_pdf(self):
        create_tex(self.sid, self.op)
        create_pdf(self.sid, self.op)

    def delete_entry(self):
        if self.sid in self.expdict:
            self.expdict.pop(self.sid)
            exp_file_path = os.path.join(home, self.op, f"{self.op}_experiments.idx")
            with open(exp_file_path, "wb") as f:
                pickle.dump(self.expdict, f)

            pdf_path = os.path.join(home, self.op, "pdf", f"{self.sid}.pdf")
            try:
                os.remove(pdf_path)
                print("PDF was removed")
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Error removing PDF: {e}")

            self.sample_btns()
            self.new_entry()

    def fill_modules(self, sample, *modules, **kwargs):
        self.exp_op = kwargs.get("op", self.ids.exp_op.text)
        exp_file_path = os.path.join(
            home, self.exp_op, f"{self.exp_op}_experiments.idx"
        )
        try:
            with open(exp_file_path, "rb") as f:
                self.sidebar_expdict = pickle.load(f)
        except Exception as e:
            print(f"Error loading sidebar experiment file: {e}")
            self.sidebar_expdict = {}
            return

        if sample not in self.sidebar_expdict:
            print(f"Sample {sample} not found in {self.exp_op}'s experiments.")
            return

        sample_data = self.sidebar_expdict[sample]

        if "complete" in modules:
            self.ids.complete.status = sample_data.get("COMPLETE", False)

        if "info" in modules and "INFORMATION" in sample_data:
            info_dict = sample_data["INFORMATION"]
            self.info.ids.sid.txtfld.text = info_dict.get("SAMPLE ID", "")
            self.info.ids.tag.txtfld.text = info_dict.get("TAG", "")
            self.info.ids.lj.txtfld.text = info_dict.get("LABJOURNAL", "")
            self.info.ids.date.txtfld.text = info_dict.get("DATE", "")
            self.info.ids.trgt.txtfld.text = info_dict.get("TARGET", "")

        if "idea" in modules and "INFORMATION" in sample_data:
            self.info.ids.idea.txtfld.text = sample_data["INFORMATION"].get("IDEA", "")

        if "reaction" in modules and "REACTION" in sample_data:
            reac_dict = sample_data["REACTION"]
            self.reaction.error = ""
            self.reaction.ids.reactants.txtfld.text = reac_dict.get("REACTANTS", "")
            self.reaction.ids.products.txtfld.text = reac_dict.get("PRODUCTS", "")
            self.reaction.ids.output_reactants.text = reac_dict.get("REACTANTSBAL", "")
            self.reaction.ids.output_products.text = reac_dict.get("PRODUCTSBAL", "")

        if "swi" in modules and "SWI" in sample_data:
            swi_dict = sample_data["SWI"]
            self.swi.ids.netweight.txtfld.text = swi_dict.get("NET WEIGHT", "")
            self.swi.swi_grid.clear_widgets()
            self.swi.swi_rows = []
            reactants_data = swi_dict.get("REACTANTS", [])
            for _ in reactants_data:
                self.swi.add_swi_row()
            for n, x in enumerate(self.swi.swi_rows):
                if n < len(reactants_data):
                    reactant_info = reactants_data[n]
                    x.children[5].unbind(text=x.children[5].on_text)
                    x.children[5].text = reactant_info.get("REACTANT", "")
                    x.children[5].bind(text=x.children[5].on_text)
                    x.children[4].text = reactant_info.get("EQUIVALENT", "")
                    x.children[3].text = reactant_info.get("MOLAR MASS", "")
                    x.children[2].text = reactant_info.get("MOL", "")
                    x.children[1].text = reactant_info.get("MASS", "")

        if "additives" in modules and "SWI" in sample_data:
            self.swi.ids.additives.txtfld.text = sample_data["SWI"].get("ADDITIVES", "")

        if "method" in modules and "TP" in sample_data:
            tp_method_dict = sample_data["TP"].get("METHOD", {})
            self.tp.ids.method.spnfld.text = tp_method_dict.get("Method", "")
            for i, j in enumerate(tp_method_dict.values()):
                if j != "Method" and i - 1 < len(self.tp.method_parameters):
                    self.tp.method_parameters[i - 1].txtfld.text = j

        if "expdet" in modules and "TP" in sample_data:
            self.tp.ids.expdet.txtfld.text = sample_data["TP"].get(
                "EXPERIMENTAL DETAILS", ""
            )

        if "tp" in modules and "TP" in sample_data:
            tp_data = sample_data["TP"]
            units = tp_data.get("UNITS", {})
            self.tp.ids.tstart_unit.unit.text = units.get("TSTART", "")
            self.tp.ids.ramp_unit.unit.text = units.get("RAMP", "")
            self.tp.ids.tend_unit.unit.text = units.get("TEND", "")
            self.tp.ids.dwell_unit.unit.text = units.get("DWELL", "")

            for i in self.tp.tp_rows:
                for j_widget in i:
                    self.tp.ids.tp_grid.remove_widget(j_widget)
            self.tp.tp_rows = []

            program_data = tp_data.get("PROGRAM", [])
            for _ in range(len(program_data) - 1):
                self.tp.add_tp_row()

            for i, segment_data in enumerate(program_data):
                if i == 0:
                    self.tp.ids.tstart.text = segment_data.get("TSTART", "")
                    self.tp.ids.ramp.text = segment_data.get("RAMP", "")
                    self.tp.ids.tend.text = segment_data.get("TEND", "")
                    self.tp.ids.dwell.text = segment_data.get("DWELL", "")
                elif i - 1 < len(self.tp.tp_rows):
                    row_widgets = self.tp.tp_rows[i - 1]
                    row_widgets[0].text = segment_data.get("SEGMENT", "")
                    row_widgets[1].text = segment_data.get("TSTART", "")
                    row_widgets[2].text = segment_data.get("RAMP", "")
                    row_widgets[3].text = segment_data.get("TEND", "")
                    row_widgets[4].text = segment_data.get("DWELL", "")

        if "ap" in modules and "ANALYTICS" in sample_data:
            self.ana.ids.ap.txtfld.text = sample_data["ANALYTICS"].get("APPEARANCE", "")

        if "ana" in modules and "ANALYTICS" in sample_data:
            ana_methods = sample_data["ANALYTICS"].get("METHODS", {})
            for item in self.ana.method_list:
                item.status = ana_methods.get(item.label, False)

        if "anadet" in modules and "ANALYTICS" in sample_data:
            self.ana.ids.anadet.txtfld.text = sample_data["ANALYTICS"].get(
                "ANALYTICAL DETAILS", ""
            )

        if "prod" in modules and "RESULT" in sample_data:
            res_dict = sample_data["RESULT"]
            for i in self.res.product_rows:
                for j_widget in i:
                    self.res.ids.product_grid.remove_widget(j_widget)
            self.res.product_rows = []

            products_data = res_dict.get("PRODUCTS", [])
            for _ in range(len(products_data) - 1):
                self.res.add_product_row()

            for i, product_info in enumerate(products_data):
                if i == 0:
                    self.res.ids.identifier.txtfld.text = product_info.get(
                        "IDENTIFIER", ""
                    )
                    self.res.ids.product.txtfld.text = product_info.get("PRODUCT", "")
                elif i - 1 < len(self.res.product_rows):
                    row_widgets = self.res.product_rows[i - 1]
                    row_widgets[0].text = product_info.get("IDENTIFIER", "")
                    row_widgets[1].text = product_info.get("PRODUCT", "")

        if "res" in modules and "RESULT" in sample_data:
            self.res.ids.conclusion.txtfld.text = sample_data["RESULT"].get(
                "CONCLUSION", ""
            )

    def key_action(self, *args):
        # This method is quite long and contains UI interaction logic.
        # Consider breaking it down further if needed, or moving parts to specific UI components.
        # For now, it's kept as is for structural similarity to the original.
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
                lambda dt: self.ids.editor_sv.scroll_to(self.info_panel)
            )
            self.info.ids.sid.txtfld.focus = True

        # Open Reaction and Focus
        if args[3] == "2" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.reaction_panel.is_open:
                self.reaction_panel.open()
            Clock.schedule_once(
                lambda dt: self.ids.editor_sv.scroll_to(self.reaction_panel)
            )
            self.reaction.ids.reactants.txtfld.focus = True

        # Open SWI and Focus
        if args[3] == "3" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.swi_panel.is_open:
                self.swi_panel.open()
            Clock.schedule_once(lambda dt: self.ids.editor_sv.scroll_to(self.swi_panel))
            self.swi.ids.netweight.txtfld.focus = True

        # Open TP and Focus
        if args[3] == "4" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.tp_panel.is_open:
                self.tp_panel.open()
            Clock.schedule_once(lambda dt: self.ids.editor_sv.scroll_to(self.tp_panel))
            if self.tp.ids.method_grid.children:
                self.tp.ids.method_grid.children[-2].txtfld.focus = True

        # Open Analytics and Focus
        if args[3] == "5" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.ana_panel.is_open:
                self.ana_panel.open()

            Clock.schedule_once(lambda dt: self.ids.editor_sv.scroll_to(self.ana_panel))
            self.ana.ids.ap.txtfld.focus = True

        # Open Results and Focus
        if args[3] == "6" and "ctrl" in args[4] and "shift" not in args[4]:
            if not self.res_panel.is_open:
                self.res_panel.open()

            Clock.schedule_once(lambda dt: self.ids.editor_sv.scroll_to(self.res_panel))
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
        self.info.ids.sid.txtfld.focus = True
        # The rest of the new_entry method that was commented out is removed as it's covered by reset methods.

    def on_enter(self, *args):
        # Make sure Window is imported: from kivy.core.window import Window
        from kivy.core.window import Window

        if self.info_panel:
            self.info_panel.open()
        if (
            hasattr(self.info, "ids")
            and self.info.ids
            and hasattr(self.info.ids.sid, "txtfld")
        ):
            self.info.ids.sid.txtfld.focus = True
        Window.bind(on_key_down=self.key_action)

    def on_leave(self, *args):
        from kivy.core.window import Window

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
        # Assuming ImportPopup is defined in Widgets.py or imported elsewhere
        from Widgets import ImportPopup  # Add this if not already imported

        self.importpopup = ImportPopup(
            editor=self,
            ops_list=self.ops_list,
            op=self.container.ids.op.text,
            module=module,
            home=home,
        )
        self.importpopup.open()

    def sample_btns(self):
        self.ops_list = os.listdir(home)
        try:
            self.ops_list.remove("DATA")
        except ValueError:
            pass

        self.samplelist = []
        self.exp_op = self.ids.exp_op.text
        exp_file_path = os.path.join(
            home, self.exp_op, f"{self.exp_op}_experiments.idx"
        )
        try:
            with open(exp_file_path, "rb") as f:
                self.sidebar_expdict = pickle.load(f)
        except Exception:
            return

        self.sample_files = []
        for i in self.sidebar_expdict:
            sid = i
            tag = self.sidebar_expdict[i]["INFORMATION"].get("TAG", "")
            met = self.sidebar_expdict[i]["TP"]["METHOD"].get("Method", "")
            met_abbrev = self.method_dict.get(met, {}).get("ABBREV", "")
            sidtagmet = f"{sid}#{tag}#{met_abbrev}"
            self.sample_files.append(sidtagmet)

        self.sample_files.sort(key=lambda v: v.upper(), reverse=True)

        btn_search = self.ids.filter.text.strip()
        search_elements = [s for s in btn_search.split(" ") if s] or [""]

        current_search_results = list(
            self.sample_files
        )  # Make a copy to iterate and modify
        for term in search_elements:
            if term == "":  # if search is empty, show all
                break
            filtered_results = []
            for item_string in current_search_results:
                if term in item_string:
                    filtered_results.append(item_string)
            current_search_results = filtered_results
        self.search_result = current_search_results

        final_results_sids = [res.split("#")[0] for res in self.search_result]

        self.samplelist = []  # Clear previous list
        for sid_key in final_results_sids:
            if sid_key in self.sidebar_expdict:
                exp_data = self.sidebar_expdict[sid_key]
                tag = exp_data["INFORMATION"].get("TAG", "")
                met = exp_data["TP"]["METHOD"].get("Method", "")

                met_info = self.method_dict.get(met, {})
                met_color = met_info.get("RGBA", [1, 1, 1, 1])  # Default to white
                met_text_color = met_info.get(
                    "RGBATEXT", [0, 0, 0, 1]
                )  # Default to black
                met_text = met_info.get("ABBREV", "")

                compl = exp_data.get("COMPLETE", False)
                text_color = (
                    self.theme_cls.primary_color
                    if compl
                    else [181 / 255, 0 / 255, 16 / 255, 1]
                )

                sidtag = f"{sid_key}   |   {tag}" if tag else sid_key

                btndict = {
                    "sidtag": sidtag,
                    "sample": sid_key,
                    "editor": self,
                    "met_color": met_color,
                    "met_text_color": met_text_color,
                    "met_text": met_text,
                    "text_color": text_color,
                }
                self.samplelist.append(btndict)

    def save_entry(self):
        info_dict = {
            "SAMPLE ID": self.info.ids.sid.text,
            "TAG": self.info.ids.tag.text,
            "LABJOURNAL": self.info.ids.lj.text,
            "TARGET": self.info.ids.trgt.text,
            "DATE": self.info.ids.date.text,
            "IDEA": self.info.ids.idea.text,
        }
        reaction_dict = {
            "REACTANTS": self.reaction.ids.reactants.text,
            "PRODUCTS": self.reaction.ids.products.text,
            "REACTANTSBAL": self.reaction.ids.output_reactants.text,
            "PRODUCTSBAL": self.reaction.ids.output_products.text,
        }
        reactants_list = []
        for i in self.swi.swi_rows:
            reactant_data = {
                "REACTANT": i.children[5].text,
                "EQUIVALENT": i.children[4].text,
                "MOLAR MASS": i.children[3].text,
                "MOL": i.children[2].text,
                "MASS": i.children[1].text,
            }
            reactants_list.append(reactant_data)
        swi_dict = {
            "NET WEIGHT": self.swi.ids.netweight.txtfld.text,
            "ADDITIVES": self.swi.ids.additives.txtfld.text,
            "REACTANTS": reactants_list,
        }
        method_grid_children = reversed(self.tp.ids.method_grid.children)
        method_dict_tp = {
            child.lbl.text: child.text
            for child in method_grid_children
            if hasattr(child, "lbl")
        }

        program_list = [
            {
                "SEGMENT": "1",
                "TSTART": self.tp.ids.tstart.text,
                "RAMP": self.tp.ids.ramp.text,
                "TEND": self.tp.ids.tend.text,
                "DWELL": self.tp.ids.dwell.text,
            }
        ]
        for i in self.tp.tp_rows:
            program_data = {
                "SEGMENT": i[0].text,
                "TSTART": i[1].text,
                "RAMP": i[2].text,
                "TEND": i[3].text,
                "DWELL": i[4].text,
            }
            program_list.append(program_data)
        units_dict = {
            "TSTART": self.tp.ids.tstart_unit.unit.text,
            "RAMP": self.tp.ids.ramp_unit.unit.text,
            "TEND": self.tp.ids.tend_unit.unit.text,
            "DWELL": self.tp.ids.dwell_unit.unit.text,
        }
        tp_dict = {
            "METHOD": method_dict_tp,
            "EXPERIMENTAL DETAILS": self.tp.ids.expdet.text,
            "UNITS": units_dict,
            "PROGRAM": program_list,
        }
        ana_method_dict = {item.label: item.status for item in self.ana.method_list}
        ana_dict = {
            "APPEARANCE": self.ana.ids.ap.text,
            "METHODS": ana_method_dict,
            "ANALYTICAL DETAILS": self.ana.ids.anadet.text,
        }
        product_list = [
            {
                "IDENTIFIER": self.res.ids.identifier.text,
                "PRODUCT": self.res.ids.product.text,
            }
        ]
        for i in self.res.product_rows:
            product_data = {"IDENTIFIER": i[0].text, "PRODUCT": i[1].text}
            product_list.append(product_data)
        res_dict = {
            "PRODUCTS": product_list,
            "CONCLUSION": self.res.ids.conclusion.text,
        }

        entry_dict = {
            "OPERATOR": self.container.ids.op.spnfld.text,
            "COMPLETE": self.ids.complete.status,
            "INFORMATION": info_dict,
            "REACTION": reaction_dict,
            "SWI": swi_dict,
            "TP": tp_dict,
            "ANALYTICS": ana_dict,
            "RESULT": res_dict,
        }
        self.expdict[self.info.ids.sid.text] = entry_dict
        exp_file_path = os.path.join(home, self.op, f"{self.op}_experiments.idx")
        with open(exp_file_path, "wb") as f:
            pickle.dump(self.expdict, f)

        self.sample_btns()
        setattr(self.ids.exp_op, "text", self.container.ids.op.text)
        setattr(self.ids.exp_op.ids.spnfld, "text", self.container.ids.op.text)

    def update_reacspin(self):
        pass  # Placeholder for now

    def view_pdf(self):
        # Make sure subprocess is imported: import subprocess
        import subprocess

        self.sampleid = self.info.ids.sid.txtfld.text
        pdf_path = os.path.join(home, self.op, "pdf", f"{self.sampleid}.pdf")
        if os.path.exists(pdf_path):
            try:
                if os.name == "nt":  # For Windows
                    os.startfile(pdf_path)
                elif os.uname().sysname == "Darwin":  # For macOS
                    subprocess.Popen(["open", pdf_path])
                else:  # For Linux and other Unix-like OS
                    subprocess.Popen(["xdg-open", pdf_path])
            except Exception as e:
                print(f"Error opening PDF: {e}")
                self.infopop.title = "Error"
                self.infopop.text = "Could not open the PDF file."
                self.infopop.open()
        else:
            self.infopop.title = "No PDF found"
            self.infopop.text = "Create a PDF first."
            self.infopop.open()
