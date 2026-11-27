from ..dao import ReviewDAO
from .general_service import GeneralService


class ReviewService(GeneralService):
    dao = ReviewDAO()
    children = {}
