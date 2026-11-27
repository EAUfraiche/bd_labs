from ..dao import ArtistDAO
from .general_service import GeneralService


class ArtistService(GeneralService):
    dao = ArtistDAO()
    children = {}
