from models.DbEntity import DbEntity


class Position(DbEntity):
    def __init__(self, name: str=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
