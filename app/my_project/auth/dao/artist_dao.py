from .general_dao import GeneralDAO
from ..domain import Artist


class ArtistDAO(GeneralDAO):
    model = Artist
