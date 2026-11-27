from ..service import DeviceService
from .crud import make_crud_blueprint

service = DeviceService()
device_bp = make_crud_blueprint("device", "/devices", service)
