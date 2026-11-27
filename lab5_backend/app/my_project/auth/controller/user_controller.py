from ..service import UserService
from .crud import make_crud_blueprint, add_children_routes

service = UserService()
user_bp = make_crud_blueprint("user", "/users", service)
add_children_routes(user_bp, service, "playlists")
add_children_routes(user_bp, service, "devices")
