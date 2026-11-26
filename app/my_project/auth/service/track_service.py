from ..dao import TrackDAO
from .general_service import GeneralService


class TrackService(GeneralService):
    dao = TrackDAO()
    children = {}
