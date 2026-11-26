from flask import jsonify
from ..service import ArtistService, TrackArtistService
from .crud import make_crud_blueprint, not_found

service = ArtistService()
links = TrackArtistService()
artist_bp = make_crud_blueprint("artist", "/artists", service)


# M:N: для кожного виконавця - усі його треки
@artist_bp.get("/tracks")
def all_with_tracks():
    return jsonify(links.all_artists_with_tracks())


@artist_bp.get("/<int:artist_id>/tracks")
def tracks_of_artist(artist_id):
    r = links.tracks_of_artist(artist_id)
    return jsonify(r) if r else not_found("Artist")
