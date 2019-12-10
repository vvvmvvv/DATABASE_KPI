import npyscreen

from models.Tournament import Tournament


class EditTournament(npyscreen.ActionFormV2):
    def create(self):

        self.value = None
        self.wgName = self.add(npyscreen.TitleText, name="Name:")
        self.wgDescription = self.add(npyscreen.TitleText, name="Description:")
        self.wgClubs = self.add(npyscreen.TitleFixedText, name="Participants:")
        self.wgAvaliableClubs = self.add(npyscreen.TitleMultiSelect,
                                      name="Avaliable clubs:",
                                      max_height=-7,
                                      scroll_exit=True)

    def beforeEditing(self):
        if self.value:
            tournament = self.parentApp.database.get_tournament(self.value)
            clubs_participants = tournament.clubs
            available_clubs = [club for club in self.parentApp.database.get_clubs() if club.id not in [c.id for c in clubs_participants]]
            self.name = "Tournament id : %s" % tournament.id
            self.tournament_id = tournament.id
            self.wgName.value = tournament.name
            self.wgDescription.value = tournament.description
            string_participants = ''
            for c in clubs_participants:
                string_participants += '{0} | '.format(c.name)
            self.wgClubs.value = string_participants
            self.wgAvaliableClubs.values = [(c.name, c.id) for c in available_clubs]
            if self.wgClubs.value:
                self.wgAvaliableClubs.value = ''
        else:
            all_clubs = self.parentApp.database.get_clubs()
            self.name = "New Tournament"
            self.tournament_id = ''
            self.wgName.value = ''
            self.wgDescription.value = ''
            self.wgClubs.value = ''
            self.wgAvaliableClubs.values = [(c.name, c.id) for c in all_clubs]
            self.wgAvaliableClubs.value = ''

    def on_ok(self):
        tournament = Tournament(name=self.wgName.value, description=self.wgDescription.value)
        clubs_indexes = filter(lambda el: isinstance(el, int), self.wgAvaliableClubs.value)
        clubs_ids = []
        if clubs_indexes:
            clubs_ids = [self.wgAvaliableClubs.values[i][1] for i in clubs_indexes]
        self.parentApp.database.upsert_tournament(self.tournament_id, tournament, clubs_ids)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

