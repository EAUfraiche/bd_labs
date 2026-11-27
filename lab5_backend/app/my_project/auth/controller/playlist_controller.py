from flask import jsonify
from ..service import PlaylistService, PlaylistTrackService
from .crud import make_crud_blueprint, json_body, not_found

service = PlaylistService()
links = PlaylistTrackService()
playlist_bp = make_crud_blueprint("playlist", "/playlists", service)


# M:N: для кожного плейлиста - усі його треки
@playlist_bp.get("/tracks")
def all_with_tracks():
    return jsonify(links.all_playlists_with_tracks())


@playlist_bp.get("/<int:playlist_id>/tracks")
def tracks_of_playlist(playlist_id):
    r = links.tracks_of_playlist(playlist_id)
    return jsonify(r) if r else not_found("Playlist")


@playlist_bp.post("/<int:playlist_id>/tracks")
def add_track(playlist_id):
    r = links.add(playlist_id, json_body())
    return (jsonify(r), 201) if r else not_found("Playlist or track")


@playlist_bp.delete("/<int:playlist_id>/tracks/<int:track_id>")
def remove_track(playlist_id, track_id):
    return ("", 204) if links.remove(playlist_id, track_id) else not_found("Link")
