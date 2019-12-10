import datetime

from models.DbEntity import DbEntity


class Club(DbEntity):
    def __init__(self, creation_date: datetime=None, number_of_trophies: int=None, name: str=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creation_date = creation_date
        self.number_of_trophies = number_of_trophies
        self.name = name
