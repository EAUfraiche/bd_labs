from ..service import ReviewService
from .crud import make_crud_blueprint

service = ReviewService()
review_bp = make_crud_blueprint("review", "/reviews", service)
