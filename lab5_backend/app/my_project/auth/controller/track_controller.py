from flask import jsonify
from ..service import TrackService, TrackArtistService
from .crud import make_crud_blueprint, add_children_routes, json_body, not_found

service = TrackService()
links = TrackArtistService()
track_bp = make_crud_blueprint("track", "/tracks", service)
add_children_routes(track_bp, service, "reviews")   # M:1: для кожного треку його відгуки


# M:N: для кожного треку - усі його виконавці
@track_bp.get("/artists")
def all_with_artists():
    return jsonify(links.all_tracks_with_artists())


@track_bp.get("/<int:track_id>/artists")
def artists_of_track(track_id):
    r = links.artists_of_track(track_id)
    return jsonify(r) if r else not_found("Track")


@track_bp.post("/<int:track_id>/artists")
def add_artist(track_id):
    r = links.add(track_id, json_body())
    return (jsonify(r), 201) if r else not_found("Track or artist")


@track_bp.delete("/<int:track_id>/artists/<int:artist_id>")
def remove_artist(track_id, artist_id):
    return ("", 204) if links.remove(track_id, artist_id) else not_found("Link")
