from ..dao import PlaybackDAO
from .general_service import GeneralService


class PlaybackService(GeneralService):
    dao = PlaybackDAO()
    children = {}
