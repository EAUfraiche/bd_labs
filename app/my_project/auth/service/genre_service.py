from ..dao import GenreDAO, TrackDAO
from .general_service import GeneralService


class GenreService(GeneralService):
    dao = GenreDAO()
    children = {"tracks": (TrackDAO(), "genre_id")}
