import datetime

from models.DbEntity import DbEntity


class Player(DbEntity):
    def __init__(self,
                 first_name: str=None,
                 last_name: str=None,
                 date_of_birth: datetime=None,
                 position_id: int=None,
                 height: int=None,
                 is_injured: bool=None,
                 club_id: int=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_id = position_id
        self.height = height
        self.is_injured = is_injured
        self.club_id = club_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
