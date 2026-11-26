from .general_dao import GeneralDAO
from ..domain import RecordLabel


class LabelDAO(GeneralDAO):
    model = RecordLabel
