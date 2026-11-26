from .general_dao import GeneralDAO
from ..domain import Track


class TrackDAO(GeneralDAO):
    model = Track
