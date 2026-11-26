from ... import db


class GeneralDAO:
    model = None

    def find_all(self):
        return db.session.query(self.model).all()

    def find_by_id(self, obj_id):
        return db.session.get(self.model, obj_id)

    def find_by(self, **filters):
        return db.session.query(self.model).filter_by(**filters).all()

    def create(self, **data):
        obj = self.model(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, obj, **data):
        for key, value in data.items():
            setattr(obj, key, value)
        db.session.commit()
        return obj

    def delete(self, obj):
        db.session.delete(obj)
        db.session.commit()
