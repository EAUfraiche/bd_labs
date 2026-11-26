from datetime import date, datetime
from ... import db


class BaseModel(db.Model):
    __abstract__ = True

    def to_dto(self):
        dto = {}
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if isinstance(v, (date, datetime)):
                v = v.isoformat()
            dto[c.name] = v
        return dto


class RecordLabel(BaseModel):
    __tablename__ = "record_labels"
    label_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    country = db.Column(db.String(100))
    established_year = db.Column(db.Integer)


class Genre(BaseModel):
    __tablename__ = "genres"
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text)


class Artist(BaseModel):
    __tablename__ = "artists"
    artist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(100))
    bio = db.Column(db.Text)
    monthly_listeners = db.Column(db.BigInteger, default=0)


class Album(BaseModel):
    __tablename__ = "albums"
    album_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    album_type = db.Column(db.Enum("Album", "Single", "EP"), nullable=False, default="Album")
    label_id = db.Column(db.Integer, db.ForeignKey("record_labels.label_id", ondelete="SET NULL"))


class Track(BaseModel):
    __tablename__ = "tracks"
    track_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    isrc_code = db.Column(db.String(15), nullable=False, unique=True)
    album_id = db.Column(db.Integer, db.ForeignKey("albums.album_id", ondelete="CASCADE"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.genre_id", ondelete="SET NULL"))
    play_count = db.Column(db.BigInteger, default=0)


class TrackArtist(BaseModel):  # M:N tracks <-> artists
    __tablename__ = "track_artists"
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.track_id", ondelete="CASCADE"), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.artist_id", ondelete="CASCADE"), primary_key=True)
    role = db.Column(db.Enum("Primary", "Featured", "Producer"), default="Primary")


class User(BaseModel):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    subscription_plan = db.Column(db.Enum("Free", "Premium", "Family", "Student"), default="Free")
    country = db.Column(db.String(100), default="Ukraine")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Playlist(BaseModel):
    __tablename__ = "playlists"
    playlist_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)


class PlaylistTrack(BaseModel):  # M:N playlists <-> tracks
    __tablename__ = "playlist_tracks"
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.playlist_id", ondelete="CASCADE"), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.track_id", ondelete="CASCADE"), primary_key=True)
    added_at = db.Column(db.DateTime, server_default=db.func.now())
    position = db.Column(db.Integer, nullable=False)


class Device(BaseModel):
    __tablename__ = "devices"
    device_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.Enum("Smartphone", "Desktop", "Tablet", "SmartSpeaker", "TV"), nullable=False)
    is_active = db.Column(db.Boolean, default=False)


class CurrentPlayback(BaseModel):  # 1:1 з users
    __tablename__ = "current_playback"
    playback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.track_id", ondelete="CASCADE"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.device_id", ondelete="SET NULL"))
    progress_seconds = db.Column(db.Integer, default=0)
    is_playing = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
