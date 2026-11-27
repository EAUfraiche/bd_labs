from ..service import GenreService
from .crud import make_crud_blueprint, add_children_routes

service = GenreService()
genre_bp = make_crud_blueprint("genre", "/genres", service)
add_children_routes(genre_bp, service, "tracks")
