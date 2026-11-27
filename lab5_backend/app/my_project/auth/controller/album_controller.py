from ..service import AlbumService
from .crud import make_crud_blueprint, add_children_routes

service = AlbumService()
album_bp = make_crud_blueprint("album", "/albums", service)
add_children_routes(album_bp, service, "tracks")
