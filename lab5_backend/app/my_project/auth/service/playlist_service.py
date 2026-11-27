from ..dao import PlaylistDAO
from .general_service import GeneralService


class PlaylistService(GeneralService):
    dao = PlaylistDAO()
    children = {}
