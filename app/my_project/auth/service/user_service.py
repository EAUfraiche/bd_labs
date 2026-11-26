from ..dao import DeviceDAO, PlaylistDAO, UserDAO
from .general_service import GeneralService


class UserService(GeneralService):
    dao = UserDAO()
    children = {"playlists": (PlaylistDAO(), "user_id"), "devices": (DeviceDAO(), "user_id")}
