from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields


class Users(Model):
    id = fields.IntField(pk=True)
    full_name = fields.CharField(100, null=True)
    study_group = fields.CharField(100, null=True)
    phone_number = fields.CharField(100, null=True)
    date_of_birth = fields.DatetimeField(null=True)
    passport_data = fields.IntField(null=True)
    passport_date = fields.DatetimeField(null=True)
    passport_issued = fields.CharField(100, null=True)
    department_code = fields.IntField(null=True)
    place_of_registration = fields.CharField(100, null=True)
    courses = fields.CharField(100, null=True)

    def __str__(self):
        return self.full_name


class Administrators(Model):
    id = fields.IntField(pk=True)
    full_name = fields.CharField(100, null=True)
    password = fields.CharField(100, null=True)
    is_active = fields.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    def to_dict(self):
        return Administrators(id=self.id, fullname=self.full_name, password=self.password, is_active=True)


class Courses(Model):
    id = fields.IntField(pk=True, autoincrement=True)
    title = fields.TextField(null=True)
    schedule = fields.TextField(null=True)
    price = fields.IntField(null=True)
    audience = fields.IntField(null=True)
    teacher = fields.TextField(null=True)
    comment = fields.TextField(null=True)
    status = fields.BooleanField(default=False)

    def __str__(self):
        return self.title

    def __getitem__(self, item):
        match item:
            case 0:
                return self.id
            case 1:
                return self.title
            case 2:
                return self.schedule
            case 3:
                return self.price
            case 4:
                return self.audience
            case 5:
                return self.teacher
            case 6:
                return self.comment
            case 7:
                return self.status

    def __setitem__(self, item, new_value):
        match item:
            case 0:
                self.id = new_value
            case 1:
                self.title = new_value
            case 2:
                self.schedule = new_value
            case 3:
                self.price = new_value
            case 4:
                self.audience = new_value
            case 5:
                self.teacher = new_value
            case 6:
                self.comment = new_value
            case 7:
                self.status = new_value


admin_pydantic = pydantic_model_creator(Administrators, name="admin")
