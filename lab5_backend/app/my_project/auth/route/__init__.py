from ..controller import (label_bp, genre_bp, artist_bp, album_bp, track_bp, user_bp, playlist_bp,
                          device_bp, playback_bp, review_bp, log_bp, procedure_bp)

ALL_BLUEPRINTS = [label_bp, genre_bp, artist_bp, album_bp, track_bp, user_bp, playlist_bp,
                  device_bp, playback_bp, review_bp, log_bp, procedure_bp]


def register_routes(app):
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)
