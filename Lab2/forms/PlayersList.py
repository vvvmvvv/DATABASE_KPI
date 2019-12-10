import npyscreen


class PlayersList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(PlayersList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record
        })

    def display_value(self, vl):
        return "%s, %s" % (vl.first_name, vl.last_name)

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm('EDITPLAYER').value = act_on_this.id
        self.parent.parentApp.switchForm('EDITPLAYER')

    def when_add_record(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITPLAYER').value = None
        self.parent.parentApp.switchForm('EDITPLAYER')

    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.database.delete_player(self.values[self.cursor_line].id)
        self.parent.update_list()


class PlayersListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = PlayersList

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
            "^Q": self.when_exit
        })

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.database.get_players()
        self.wMain.display()

    def when_exit(self, *args, **keywords):
        self.parentApp.switchFormPrevious()
