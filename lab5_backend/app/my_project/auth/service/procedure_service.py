from ..dao import ProcedureDAO

STATS = ("MAX", "MIN", "SUM", "AVG")
ROLES = ("Primary", "Featured", "Producer")


def _obj(data):
    if not isinstance(data, dict):
        raise ValueError("JSON object expected")
    return data


def _text(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{key}' is required")
    return value


class ProcedureService:
    """Виклик збережених процедур з валідацією вхідних параметрів."""
    dao = ProcedureDAO()

    # 2.a
    def insert_artist(self, data):
        data = _obj(data)
        name = _text(data, "name")
        listeners = data.get("monthly_listeners", 0)
        if not isinstance(listeners, int) or listeners < 0:
            raise ValueError("Field 'monthly_listeners' must be a non-negative integer")
        rows = self.dao.call("sp_insert_artist", (name, data.get("country"), data.get("bio"), listeners))
        return rows[0] if rows else None

    # 2.b
    def add_track_artist(self, data):
        data = _obj(data)
        title, artist = _text(data, "track_title"), _text(data, "artist_name")
        role = data.get("role", "Primary")
        if role not in ROLES:
            raise ValueError("Field 'role' must be one of: " + ", ".join(ROLES))
        rows = self.dao.call("sp_add_track_artist", (title, artist, role))
        return rows[0] if rows else None

    # 2.c
    def insert_noname_batch(self):
        return self.dao.call("sp_insert_noname_batch")

    # 2.d
    def duration_stat(self, stat):
        stat = (stat or "").upper()
        if stat not in STATS:
            raise ValueError("Parameter 'stat' must be one of: " + ", ".join(STATS))
        rows = self.dao.call("sp_duration_stat", (stat,))
        return rows[0] if rows else None

    # 2.e (i)
    def split_artists_randomly(self):
        rows = self.dao.call("sp_split_artists_random")
        return rows[0] if rows else None
