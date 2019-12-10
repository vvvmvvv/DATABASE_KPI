import npyscreen


class ClubsList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(ClubsList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record
        })

    def display_value(self, vl):
        return "%s" % vl.name

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm('EDITCLUB').value = act_on_this.id
        self.parent.parentApp.switchForm('EDITCLUB')

    def when_add_record(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITCLUB').value = None
        self.parent.parentApp.switchForm('EDITCLUB')

    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.database.delete_club(self.values[self.cursor_line].id)
        self.parent.update_list()


class ClubsListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = ClubsList

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
            "^Q": self.when_exit
        })

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.database.get_clubs()
        self.wMain.display()

    def when_exit(self, *args, **keywords):
        self.parentApp.switchFormPrevious()
