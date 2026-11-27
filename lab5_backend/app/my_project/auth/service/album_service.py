from ..dao import AlbumDAO, TrackDAO
from .general_service import GeneralService


class AlbumService(GeneralService):
    dao = AlbumDAO()
    children = {"tracks": (TrackDAO(), "album_id")}
