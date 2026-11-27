from ..dao import PlaylistDeleteLogDAO
from .general_service import GeneralService


class LogService(GeneralService):
    """Журнал видалених плейлистів (лише читання)."""
    dao = PlaylistDeleteLogDAO()
