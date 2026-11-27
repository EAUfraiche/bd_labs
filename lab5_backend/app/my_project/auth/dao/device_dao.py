from .general_dao import GeneralDAO
from ..domain import Device


class DeviceDAO(GeneralDAO):
    model = Device
