from .general_dao import GeneralDAO
from ..domain import PlaylistDeleteLog


class PlaylistDeleteLogDAO(GeneralDAO):
    model = PlaylistDeleteLog
