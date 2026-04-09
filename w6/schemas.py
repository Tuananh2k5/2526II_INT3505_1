from marshmallow import Schema, fields, validate

class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    owner_id = fields.Int(dump_only=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)
    scopes = fields.Method("get_scopes_list", dump_only=True)

    def get_scopes_list(self, obj):
        return obj.get_scopes()
