from ..dao import DeviceDAO
from .general_service import GeneralService


class DeviceService(GeneralService):
    dao = DeviceDAO()
    children = {}
