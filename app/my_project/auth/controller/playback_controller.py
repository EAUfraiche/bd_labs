from ..service import PlaybackService
from .crud import make_crud_blueprint

service = PlaybackService()
playback_bp = make_crud_blueprint("playback", "/playback", service)
