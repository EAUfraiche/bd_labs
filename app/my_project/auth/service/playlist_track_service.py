from ..dao import PlaylistTrackDAO, PlaylistDAO, TrackDAO


class PlaylistTrackService:
    """M:N: плейлисти <-> треки (стикувальна таблиця playlist_tracks)."""
    dao = PlaylistTrackDAO()
    playlist_dao = PlaylistDAO()
    track_dao = TrackDAO()

    def tracks_of_playlist(self, playlist_id):
        playlist = self.playlist_dao.find_by_id(playlist_id)
        if not playlist:
            return None
        dto = playlist.to_dto()
        dto["tracks"] = [
            {**t.to_dto(), "position": pos, "added_at": added.isoformat() if added else None}
            for t, pos, added in self.dao.tracks_of_playlist(playlist_id)]
        return dto

    def all_playlists_with_tracks(self):
        return [self.tracks_of_playlist(p.playlist_id) for p in self.playlist_dao.find_all()]

    def add(self, playlist_id, data):
        if not isinstance(data, dict) or "track_id" not in data:
            raise ValueError("Field 'track_id' is required")
        track_id = data["track_id"]
        position = data.get("position")
        if position is not None and (not isinstance(position, int) or position < 1):
            raise ValueError("Field 'position' must be a positive integer")
        if not self.playlist_dao.find_by_id(playlist_id) or not self.track_dao.find_by_id(track_id):
            return None
        if position is None:
            position = self.dao.next_position(playlist_id)
        link = self.dao.find_link(playlist_id, track_id)
        if link:
            self.dao.update(link, position=position)
        else:
            self.dao.create(playlist_id=playlist_id, track_id=track_id, position=position)
        return self.tracks_of_playlist(playlist_id)

    def remove(self, playlist_id, track_id):
        link = self.dao.find_link(playlist_id, track_id)
        if not link:
            return False
        self.dao.delete(link)
        return True
