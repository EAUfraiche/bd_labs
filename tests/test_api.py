import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from sqlalchemy import event
from my_project import create_app, db


@pytest.fixture
def client():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def _fk_on(dbapi_con, _):
            dbapi_con.execute("PRAGMA foreign_keys=ON")
        db.create_all()
        yield app.test_client()


def make(client, url, body, key):
    r = client.post(url, json=body)
    assert r.status_code == 201, r.get_json()
    return r.get_json()[key]


def seed(client):
    s = {}
    s["label"] = make(client, "/labels", {"name": "L1", "country": "UA"}, "label_id")
    s["genre"] = make(client, "/genres", {"name": "Pop"}, "genre_id")
    s["album"] = make(client, "/albums", {"title": "A1", "release_date": "2020-01-01", "label_id": s["label"]}, "album_id")
    s["t1"] = make(client, "/tracks", {"title": "T1", "duration_seconds": 200, "isrc_code": "X1", "album_id": s["album"], "genre_id": s["genre"]}, "track_id")
    s["t2"] = make(client, "/tracks", {"title": "T2", "duration_seconds": 300, "isrc_code": "X2", "album_id": s["album"]}, "track_id")
    s["a1"] = make(client, "/artists", {"name": "Art1"}, "artist_id")
    s["a2"] = make(client, "/artists", {"name": "Art2"}, "artist_id")
    s["user"] = make(client, "/users", {"username": "u1", "email": "u1@x.io"}, "user_id")
    s["pl"] = make(client, "/playlists", {"title": "P1", "user_id": s["user"]}, "playlist_id")
    return s


def test_crud(client):
    lid = make(client, "/labels", {"name": "L", "established_year": 2000}, "label_id")
    assert client.get("/labels").get_json()[0]["name"] == "L"
    assert client.get(f"/labels/{lid}").status_code == 200
    assert client.put(f"/labels/{lid}", json={"country": "PL"}).get_json()["country"] == "PL"
    assert client.delete(f"/labels/{lid}").status_code == 204
    assert client.get(f"/labels/{lid}").status_code == 404
    assert client.delete(f"/labels/{lid}").status_code == 404


def test_defaults_and_dates(client):
    s = seed(client)
    album = client.get(f"/albums/{s['album']}").get_json()
    assert album["album_type"] == "Album" and album["release_date"] == "2020-01-01"
    assert client.get(f"/users/{s['user']}").get_json()["subscription_plan"] == "Free"


def test_validation(client):
    assert client.post("/labels", json={}).status_code == 400
    assert client.post("/labels", json={"name": "x", "foo": 1}).status_code == 400
    assert client.post("/labels", data="not json").status_code == 400
    client.post("/labels", json={"name": "dup"})
    assert client.post("/labels", json={"name": "dup"}).status_code == 409
    assert client.post("/albums", json={"title": "a", "release_date": "bad"}).status_code == 400
    assert client.post("/albums", json={"title": "a", "release_date": "2020-01-01", "album_type": "LP"}).status_code == 400
    assert client.post("/albums", json={"title": "a", "release_date": "2020-01-01", "label_id": 999}).status_code == 409


def test_many_to_one(client):
    s = seed(client)
    r = client.get(f"/labels/{s['label']}/albums").get_json()
    assert [a["title"] for a in r["albums"]] == ["A1"]
    assert len(client.get(f"/albums/{s['album']}/tracks").get_json()["tracks"]) == 2
    assert client.get("/labels/albums").get_json()[0]["albums"][0]["album_id"] == s["album"]
    assert client.get(f"/users/{s['user']}/playlists").get_json()["playlists"][0]["title"] == "P1"
    assert client.get("/genres/tracks").get_json()[0]["tracks"][0]["title"] == "T1"
    assert client.get("/labels/999/albums").status_code == 404


def test_many_to_many_track_artist(client):
    s = seed(client)
    t = s["t1"]
    assert client.post(f"/tracks/{t}/artists", json={"artist_id": s["a1"]}).status_code == 201
    r = client.post(f"/tracks/{t}/artists", json={"artist_id": s["a2"], "role": "Featured"})
    assert [a["role"] for a in r.get_json()["artists"]] == ["Primary", "Featured"]
    assert client.get(f"/artists/{s['a2']}/tracks").get_json()["tracks"][0]["role"] == "Featured"
    assert len(client.get("/tracks/artists").get_json()) == 2
    assert len(client.get("/artists/tracks").get_json()) == 2
    assert client.post(f"/tracks/{t}/artists", json={"artist_id": s["a1"], "role": "Boss"}).status_code == 400
    assert client.post(f"/tracks/{t}/artists", json={"artist_id": 999}).status_code == 404
    assert client.delete(f"/tracks/{t}/artists/{s['a1']}").status_code == 204
    assert client.delete(f"/tracks/{t}/artists/{s['a1']}").status_code == 404


def test_many_to_many_playlist_tracks(client):
    s = seed(client)
    pl = s["pl"]
    client.post(f"/playlists/{pl}/tracks", json={"track_id": s["t2"]})
    r = client.post(f"/playlists/{pl}/tracks", json={"track_id": s["t1"]}).get_json()
    assert [(t["title"], t["position"]) for t in r["tracks"]] == [("T2", 1), ("T1", 2)]
    assert len(client.get("/playlists/tracks").get_json()[0]["tracks"]) == 2
    assert client.delete(f"/playlists/{pl}/tracks/{s['t2']}").status_code == 204


def test_cascade_and_set_null(client):
    s = seed(client)
    client.delete(f"/labels/{s['label']}")
    assert client.get(f"/albums/{s['album']}").get_json()["label_id"] is None
    client.delete(f"/albums/{s['album']}")
    assert client.get(f"/tracks/{s['t1']}").status_code == 404


def test_playback_one_to_one(client):
    s = seed(client)
    body = {"user_id": s["user"], "track_id": s["t1"]}
    assert client.post("/playback", json=body).status_code == 201
    assert client.post("/playback", json=body).status_code == 409
    d = client.post("/devices", json={"user_id": s["user"], "device_name": "Phone", "device_type": "Smartphone"})
    assert d.status_code == 201
