import npyscreen

from models.Player import Player


class EditPlayer(npyscreen.ActionFormV2):
    def create(self):
        self.value = None
        all_clubs = self.parentApp.database.get_clubs()
        all_positions = self.parentApp.database.get_positions()
        self.wgFirstName = self.add(npyscreen.TitleText, name="First Name:")
        self.wgLastName = self.add(npyscreen.TitleText, name="Last Name:")
        self.wgHeight = self.add(npyscreen.TitleText, name="Height:")
        self.wgDateOfBirth = self.add(npyscreen.TitleDateCombo, name="Date of birth:")
        self.wgIsInjured = self.add(npyscreen.TitleSelectOne,
                                      max_height=2,
                                      value=[0, ],
                                      name='IsInjured:',
                                      values=['False', 'True'],
                                      scroll_exit=True)
        self.wgPosition = self.add(npyscreen.TitleSelectOne,
                                   max_height=4,
                                   value=[0, ],
                                   name="Position:",
                                   values=[(p.name, p.id) for p in all_positions],
                                   scroll_exit=True,
                                   default=0)

        self.wgClub = self.add(npyscreen.TitleSelectOne,
                               name="Club:",
                               max_height=-2,
                               value=[c.id for c in all_clubs],
                               values=[(c.name, c.id) for c in all_clubs],
                               scroll_exit=True)

    def beforeEditing(self):
        if self.value:
            player = self.parentApp.database.get_player(self.value)
            if player.club_id:
                self.wgClub.value = [x[1] for x in self.wgClub.values].index(player.club_id)
            else:
                self.wgClub.value = ''
            if player.position_id:
                self.wgPosition.value = [x[1] for x in self.wgPosition.values].index(player.position_id)
            else:
                self.wgPosition.value = 0
            self.name = "Player id : %s" % player.id
            self.player_id = player.id
            self.wgFirstName.value = player.first_name
            self.wgLastName.value = player.last_name
            self.wgHeight.value = str(player.height)
            self.wgDateOfBirth.value = player.date_of_birth
            self.wgIsInjured.value = player.is_injured
        else:
            self.name = "New Player"
            self.player_id = ''
            self.wgFirstName.value = ''
            self.wgLastName.value = ''
            self.wgHeight.value = ''
            self.wgDateOfBirth.value = ''
            self.wgIsInjured.value = 0
            self.wgPosition.value = 0
            self.wgClub.value = ''

    def on_ok(self):
        player = Player(height=self.wgHeight.value,
                        is_injured=bool(self.wgIsInjured.value[0]),
                        first_name=self.wgFirstName.value,
                        last_name=self.wgLastName.value,
                        date_of_birth=self.wgDateOfBirth.value)
        if isinstance(self.wgClub.value[0], int):
            player.club_id = self.wgClub.values[self.wgClub.value[0]][1]
        if isinstance(self.wgPosition.value[0], int):
            player.position_id = self.wgPosition.values[self.wgPosition.value[0]][1]
        self.parentApp.database.upsert_player(self.player_id, player)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()
