from .general_dao import GeneralDAO
from ..domain import CurrentPlayback


class PlaybackDAO(GeneralDAO):
    model = CurrentPlayback
