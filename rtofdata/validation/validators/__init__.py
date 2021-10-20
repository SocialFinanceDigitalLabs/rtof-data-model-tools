from datetime import datetime
from types import ModuleType


class ValidationException(Exception):
    pass


def get_validator(validator_id: str):
    validator = globals().get(validator_id)
    if validator is None:
        raise Exception(f"No validator found for: {validator_id}")
    if isinstance(validator, ModuleType):
        return getattr(validator, 'validate')
    else:
        return validator


def required(context, field_value, enabled):
    if enabled and (field_value is None or field_value == ""):
        raise ValidationException("Field is blank")


def unique(context, field_value, enabled):
    pass

def date_after(context, field_value, field_id):
    if not field_value:
        return

    spec = context.spec
    fields_by_id = {f.field.id: f for f in spec.fields}
    fieldrecord = fields_by_id.get(field_id)
    if not fieldrecord:
        print("VALIDATION MISCONFIGURED: FIELD DOES NOT EXIST", field_id)
        raise ValidationException("CONFIGURATION ERROR")

    other_record = context.datasource.get_single_record(fieldrecord.record.id, *context.record_pk)
    other_value = getattr(other_record, fieldrecord.field.id) if other_record else None
    if other_value is None:
        raise ValidationException(f"{other_value} is not set")

    if not isinstance(other_value, datetime):
        mon_year = datetime.strptime(str(other_value), '%Y-%m')
        if not isinstance (mon_year, datetime):

            raise ValidationException(f"{other_value} is not a date")

        datetime.strptime(other_value, '%Y-%m')

    if field_value <= other_value:
        raise ValidationException(f"{field_value} is not larger than {other_value}")


def character_limit(context, field_value, enabled):
        if enabled: 
            field_value = str(field_value)
            if len(field_value) > 255:
                print("255 character limit exceeded")
        else:
            pass 


def dimension(context, field_value, enabled):
    pass


def count_min(context, field_value, enabled):
    if enabled:
        len(field_value) < 3
        print("The number of occurances in this list is below the required number")
    else :
        pass


def national_insurance_number(context, field_value, enabled):
    pass


def conditional(context, field_value, enabled):
    pass
