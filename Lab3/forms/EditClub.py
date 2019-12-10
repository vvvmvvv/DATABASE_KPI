import npyscreen

from models.Club import Club


class EditClub(npyscreen.ActionFormV2):
    def create(self):
        self.value = None
        self.wgName = self.add(npyscreen.TitleText, name="Name:")
        self.wgNumberOfTrophies = self.add(npyscreen.TitleText, name="Number of trophies:")
        self.wgCreationDate = self.add(npyscreen.TitleDateCombo, name="Creation date:")
        self.wgTournaments = self.add(npyscreen.TitleFixedText, name="Tournaments:")
        self.wgFreePlayers = self.add(npyscreen.TitleMultiSelect,
                                      name="Free players:",
                                      max_height=-7,
                                      scroll_exit=True
                                      )
        self.wgPlayers = self.add(npyscreen.TitleMultiLine, name="Players:")


    def beforeEditing(self):
        free_players = self.parentApp.database.get_players_free()
        self.wgFreePlayers.values = [(p.first_name, p.last_name, p.id) for p in free_players]
        self.wgFreePlayers.value = [p.id for p in free_players]
        if self.value:
            club = self.parentApp.database.get_club(self.value)
            club_players = club.players#self.parentApp.database.get_players_by_club(club.id)
            club_tournaments = club.tournaments#self.parentApp.database.get_tournaments_by_club(club.id)
            self.name = "Club id : %s" % club.id
            self.club_id = club.id
            self.wgName.value = club.name
            self.wgCreationDate.value = club.creation_date
            self.wgNumberOfTrophies.value = str(club.number_of_trophies)
            self.wgPlayers.values = [str(p) for p in club_players]
            tournaments_string = ''
            for t in club_tournaments:
                tournaments_string += '{0} | '.format(t.name)
            self.wgTournaments.value = tournaments_string
            self.wgFreePlayers.values = [(p.first_name, p.last_name, p.id) for p in free_players]
            if self.wgPlayers.values:
                self.wgFreePlayers.value = ''
        else:
            self.name = "New Club"
            self.club_id = ''
            self.wgName.value = ''
            self.wgCreationDate.value = ''
            self.wgNumberOfTrophies.value = ''
            self.wgFreePlayers.value = 0
            self.wgPlayers.values = ''

    def on_ok(self):
        club = Club(name=self.wgName.value, creation_date=self.wgCreationDate.value,
                    number_of_trophies=self.wgNumberOfTrophies.value)
        free_player_indexes = filter(lambda el: isinstance(el, int), self.wgFreePlayers.value)
        free_player_ids = []
        if free_player_indexes:
            free_player_ids = [self.wgFreePlayers.values[i][2] for i in free_player_indexes]
        self.parentApp.database.upsert_club(self.club_id, club, free_player_ids)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()
