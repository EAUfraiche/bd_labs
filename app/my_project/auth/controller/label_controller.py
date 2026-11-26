from ..service import LabelService
from .crud import make_crud_blueprint, add_children_routes

service = LabelService()
label_bp = make_crud_blueprint("label", "/labels", service)
add_children_routes(label_bp, service, "albums")
