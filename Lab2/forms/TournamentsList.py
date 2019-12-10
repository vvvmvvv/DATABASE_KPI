import npyscreen


class TournamentsList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(TournamentsList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record
        })

    def display_value(self, vl):
        return "%s" % vl.name

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm('EDITTOURNAMENT').value = act_on_this.id
        self.parent.parentApp.switchForm('EDITTOURNAMENT')

    def when_add_record(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITTOURNAMENT').value = None
        self.parent.parentApp.switchForm('EDITTOURNAMENT')

    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.database.delete_tournament(self.values[self.cursor_line].id)
        self.parent.update_list()


class TournamentsListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = TournamentsList

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
            "^Q": self.when_exit
        })

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.database.get_tournaments()
        self.wMain.display()

    def when_exit(self, *args, **keywords):
        self.parentApp.switchFormPrevious()
