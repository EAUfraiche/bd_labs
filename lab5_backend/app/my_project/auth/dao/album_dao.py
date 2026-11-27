from .general_dao import GeneralDAO
from ..domain import Album


class AlbumDAO(GeneralDAO):
    model = Album
