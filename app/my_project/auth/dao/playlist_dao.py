from .general_dao import GeneralDAO
from ..domain import Playlist


class PlaylistDAO(GeneralDAO):
    model = Playlist
