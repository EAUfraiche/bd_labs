from datetime import date, datetime
from sqlalchemy import Date, DateTime, Enum


class GeneralService:
    """Базова бізнес-логіка: валідація, CRUD, вибірки зі сторони зв'язку 1:N (M:1)."""
    dao = None
    children = {}  # назва -> (DAO дочірньої таблиці, ім'я зовнішнього ключа)
    readonly = {"created_at", "last_updated"}

    # ---------- валідація ----------
    def _writable(self):
        return {c.name: c for c in self.dao.model.__table__.columns
                if not c.primary_key and c.name not in self.readonly}

    def _clean(self, data, partial):
        if not isinstance(data, dict):
            raise ValueError("JSON object expected")
        cols = self._writable()
        unknown = sorted(set(data) - set(cols))
        if unknown:
            raise ValueError("Unknown fields: " + ", ".join(unknown))
        if not partial:
            missing = [n for n, c in cols.items()
                       if not c.nullable and c.default is None and c.server_default is None and n not in data]
            if missing:
                raise ValueError("Required fields: " + ", ".join(missing))
        clean = {}
        for key, value in data.items():
            col = cols[key]
            if value is None:
                if not col.nullable:
                    raise ValueError(f"Field '{key}' cannot be null")
            elif isinstance(col.type, Enum) and value not in col.type.enums:
                raise ValueError(f"Field '{key}' must be one of: {', '.join(col.type.enums)}")
            elif isinstance(col.type, (Date, DateTime)):
                try:
                    parse = date.fromisoformat if isinstance(col.type, Date) else datetime.fromisoformat
                    value = parse(value)
                except (TypeError, ValueError):
                    raise ValueError(f"Field '{key}' must be an ISO date string")
            clean[key] = value
        return clean

    # ---------- CRUD ----------
    def get_all(self):
        return [o.to_dto() for o in self.dao.find_all()]

    def get_one(self, obj_id):
        obj = self.dao.find_by_id(obj_id)
        return obj.to_dto() if obj else None

    def create(self, data):
        return self.dao.create(**self._clean(data, partial=False)).to_dto()

    def update(self, obj_id, data):
        obj = self.dao.find_by_id(obj_id)
        if not obj:
            return None
        return self.dao.update(obj, **self._clean(data, partial=True)).to_dto()

    def delete(self, obj_id):
        obj = self.dao.find_by_id(obj_id)
        if not obj:
            return False
        self.dao.delete(obj)
        return True

    # ---------- M:1 (для батьківського запису - всі дочірні) ----------
    def get_with(self, obj_id, key):
        parent = self.dao.find_by_id(obj_id)
        if not parent:
            return None
        child_dao, fk = self.children[key]
        dto = parent.to_dto()
        dto[key] = [c.to_dto() for c in child_dao.find_by(**{fk: obj_id})]
        return dto

    def get_all_with(self, key):
        pk = list(self.dao.model.__table__.primary_key.columns)[0].name
        return [self.get_with(getattr(p, pk), key) for p in self.dao.find_all()]
