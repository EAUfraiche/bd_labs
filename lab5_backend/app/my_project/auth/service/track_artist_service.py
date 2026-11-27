from ..dao import TrackArtistDAO, TrackDAO, ArtistDAO

ROLES = ("Primary", "Featured", "Producer")


class TrackArtistService:
    """M:N: треки <-> виконавці (стикувальна таблиця track_artists)."""
    dao = TrackArtistDAO()
    track_dao = TrackDAO()
    artist_dao = ArtistDAO()

    def artists_of_track(self, track_id):
        track = self.track_dao.find_by_id(track_id)
        if not track:
            return None
        dto = track.to_dto()
        dto["artists"] = [{**a.to_dto(), "role": role} for a, role in self.dao.artists_of_track(track_id)]
        return dto

    def tracks_of_artist(self, artist_id):
        artist = self.artist_dao.find_by_id(artist_id)
        if not artist:
            return None
        dto = artist.to_dto()
        dto["tracks"] = [{**t.to_dto(), "role": role} for t, role in self.dao.tracks_of_artist(artist_id)]
        return dto

    def all_tracks_with_artists(self):
        return [self.artists_of_track(t.track_id) for t in self.track_dao.find_all()]

    def all_artists_with_tracks(self):
        return [self.tracks_of_artist(a.artist_id) for a in self.artist_dao.find_all()]

    def add(self, track_id, data):
        if not isinstance(data, dict) or "artist_id" not in data:
            raise ValueError("Field 'artist_id' is required")
        role = data.get("role", "Primary")
        if role not in ROLES:
            raise ValueError("Field 'role' must be one of: " + ", ".join(ROLES))
        artist_id = data["artist_id"]
        if not self.track_dao.find_by_id(track_id) or not self.artist_dao.find_by_id(artist_id):
            return None
        link = self.dao.find_link(track_id, artist_id)
        if link:
            self.dao.update(link, role=role)
        else:
            self.dao.create(track_id=track_id, artist_id=artist_id, role=role)
        return self.artists_of_track(track_id)

    def remove(self, track_id, artist_id):
        link = self.dao.find_link(track_id, artist_id)
        if not link:
            return False
        self.dao.delete(link)
        return True
