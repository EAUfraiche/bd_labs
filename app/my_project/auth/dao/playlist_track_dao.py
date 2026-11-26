from sqlalchemy import func
from ... import db
from .general_dao import GeneralDAO
from ..domain import PlaylistTrack, Track


class PlaylistTrackDAO(GeneralDAO):
    model = PlaylistTrack

    def find_link(self, playlist_id, track_id):
        return db.session.get(PlaylistTrack, (playlist_id, track_id))

    def tracks_of_playlist(self, playlist_id):
        return (db.session.query(Track, PlaylistTrack.position, PlaylistTrack.added_at)
                .join(PlaylistTrack, PlaylistTrack.track_id == Track.track_id)
                .filter(PlaylistTrack.playlist_id == playlist_id)
                .order_by(PlaylistTrack.position).all())

    def next_position(self, playlist_id):
        m = (db.session.query(func.max(PlaylistTrack.position))
             .filter(PlaylistTrack.playlist_id == playlist_id).scalar())
        return (m or 0) + 1
