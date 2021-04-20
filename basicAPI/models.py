from tortoise.models import Model
from tortoise import fields

class Todo(Model):
    id = fields.IntField(pk = True)
    name  = fields.CharField(100, unique = True)
    description = fields.CharField(400, unique = True)
    # https://tortoise-orm.readthedocs.io/en/latest/fields.html#module-tortoise.fields.data
    date_created = fields.DatetimeField(auto_now_add = True)
    last_update =  fields.DatetimeField(auto_now = True)

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.name