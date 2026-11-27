from .general_dao import GeneralDAO
from ..domain import Review


class ReviewDAO(GeneralDAO):
    model = Review
