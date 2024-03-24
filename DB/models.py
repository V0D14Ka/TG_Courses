from tortoise.models import Model
from tortoise import fields
from tortoise.validators import MaxLengthValidator


class Users(Model):
    id = fields.BigIntField(pk=True)
    full_name = fields.CharField(60, null=True)
    study_group = fields.CharField(100, null=True)
    phone_number = fields.CharField(11, null=True)
    date_of_birth = fields.DateField(null=True)
    # Паспортные данные
    passport_series = fields.IntField(max_length=4, null=True)
    passport_number = fields.IntField(max_length=6, null=True)
    passport_date = fields.DateField(null=True)
    passport_issued = fields.CharField(100, null=True)
    reg_place = fields.CharField(200, null=True)
    department_code = fields.IntField(max_length=7, null=True)

    courses = fields.ManyToManyField("models.Courses", related_name='events')

    def __str__(self):
        return self.full_name

    def __getitem__(self, item):
        match item:
            case 0:
                return self.id
            case 1:
                return self.full_name
            case 2:
                return self.study_group
            case 3:
                return self.phone_number
            case 4:
                return self.date_of_birth
            case 5:
                return self.passport_series
            case 6:
                return self.passport_number
            case 7:
                return self.passport_date
            case 8:
                return self.passport_issued
            case 9:
                return self.reg_place
            case 10:
                return self.department_code

    def __setitem__(self, item, new_value):
        match item:
            case 0:
                self.id = new_value
            case 1:
                self.full_name = new_value
            case 2:
                self.study_group = new_value
            case 3:
                self.phone_number = new_value
            case 4:
                self.date_of_birth = new_value
            case 5:
                self.passport_series = new_value
            case 6:
                self.passport_number = new_value
            case 7:
                self.passport_date = new_value
            case 8:
                self.passport_issued = new_value
            case 9:
                self.reg_place = new_value
            case 10:
                self.department_code = new_value


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

