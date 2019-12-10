import npyscreen


class FindPlayer(npyscreen.ActionFormV2):
    def create(self):
        self.value = None
        self.wgMinHeight = self.add(npyscreen.TitleText, name="Min player height:")
        self.wgMaxHeight = self.add(npyscreen.TitleText, name="Max player height:")
        self.wgMinClubTrophies = self.add(npyscreen.TitleText, name="Min club number trophies:")
        self.wgMaxClubTrophies = self.add(npyscreen.TitleText, name="Max club number trophies:")
        all_positions = self.parentApp.database.get_positions()
        self.wgPosition = self.add(npyscreen.TitleSelectOne,
                                   max_height=4,
                                   value=[0, ],
                                   name="Player position:",
                                   values=[(p.name, p.id) for p in all_positions],
                                   scroll_exit=True,
                                   default=0)
        self.gdPlayers = self.add(npyscreen.GridColTitles, name="Results:", columns=6)

    def beforeEditing(self):
        self.name = "Advanced player search"
        self.wgPosition.value = 0
        self.wgMinHeight.value = ''
        self.wgMaxHeight.value = ''
        self.wgMinClubTrophies.value = ''
        self.wgMaxClubTrophies.value = ''


    def on_ok(self):
        search_results = self.parentApp.database.advanced_player_search(
            self.wgMinHeight.value,
            self.wgMaxHeight.value,
            self.wgMinClubTrophies.value,
            self.wgMaxClubTrophies.value,
            self.wgPosition.values[self.wgPosition.value[0]][1]
            )
        self.gdPlayers.values = []
        self.gdPlayers.values.append(['first name', 'last name', 'height', 'club', 'trophies', 'position'])
        for x in range(len(search_results)):
            player = search_results[x][0]
            club = search_results[x][1]
            position = search_results[x][2]
            row = []
            row.extend([player.first_name, player.last_name, player.height])
            row.extend([club.name, club.number_of_trophies])
            row.extend([position.name])
            self.gdPlayers.values.append(row)

    def on_cancel(self):
        self.parentApp.switchFormPrevious()
