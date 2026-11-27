from .general_dao import GeneralDAO
from ..domain import Genre


class GenreDAO(GeneralDAO):
    model = Genre
