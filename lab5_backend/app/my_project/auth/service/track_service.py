from ..dao import ReviewDAO, TrackDAO
from .general_service import GeneralService


class TrackService(GeneralService):
    dao = TrackDAO()
    children = {"reviews": (ReviewDAO(), "track_id")}   # 1:M tracks -> reviews
