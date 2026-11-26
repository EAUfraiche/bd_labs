from ... import db
from .general_dao import GeneralDAO
from ..domain import TrackArtist, Artist, Track


class TrackArtistDAO(GeneralDAO):
    model = TrackArtist

    def find_link(self, track_id, artist_id):
        return db.session.get(TrackArtist, (track_id, artist_id))

    def artists_of_track(self, track_id):
        return (db.session.query(Artist, TrackArtist.role)
                .join(TrackArtist, TrackArtist.artist_id == Artist.artist_id)
                .filter(TrackArtist.track_id == track_id)
                .order_by(Artist.artist_id).all())

    def tracks_of_artist(self, artist_id):
        return (db.session.query(Track, TrackArtist.role)
                .join(TrackArtist, TrackArtist.track_id == Track.track_id)
                .filter(TrackArtist.artist_id == artist_id)
                .order_by(Track.track_id).all())
