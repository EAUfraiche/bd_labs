from ..dao import AlbumDAO, LabelDAO
from .general_service import GeneralService


class LabelService(GeneralService):
    dao = LabelDAO()
    children = {"albums": (AlbumDAO(), "label_id")}
