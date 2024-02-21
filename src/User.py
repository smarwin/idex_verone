import os


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
