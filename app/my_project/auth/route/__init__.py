from ..controller import (label_bp, genre_bp, artist_bp, album_bp, track_bp, user_bp, playlist_bp, device_bp, playback_bp)

ALL_BLUEPRINTS = [label_bp, genre_bp, artist_bp, album_bp, track_bp, user_bp, playlist_bp, device_bp, playback_bp]


def register_routes(app):
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)
