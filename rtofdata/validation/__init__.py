from rtofdata.util.error_handler import ErrorEvent, print_error_handler as default_error_handler
from rtofdata.validation.validators import get_validator, ValidationException


class Validator:

    def __init__(self, spec, datasource, error_handler=None):
        self.spec = spec
        self.datasource = datasource
        if error_handler:
            self.error_handler = error_handler
        else:
            self.error_handler = lambda x: print(x)

        validator = self

        class ValidationContext:
            def __init__(
                    self,
                    record_id,
                    field_id,
                    record_pk,
            ):
                self.record_id = record_id
                self.field_id = field_id
                self.record_pk = record_pk
                self.validator = validator

            @property
            def spec(self):
                return self.validator.spec

            @property
            def datasource(self):
                return self.validator.datasource

        self.ValidationContext = ValidationContext

    def validate(self, validator_conf, record_id, field_id, record_pk):
        record = self.datasource.get_single_record(record_id, *record_pk)

        validator_id = validator_conf['id']
        field_value = getattr(record, field_id)

        context = self.ValidationContext(record_id, field_id, record_pk)

        validation_func = get_validator(validator_id)
        validation_func(context, field_value, validator_conf['args'])

    def validate_all(self, error_handler=None):
        if error_handler is None:
            error_handler = default_error_handler

        for record_spec in self.spec.records:
            for record_pk in self.datasource.get_records_by_type(record_spec.id):
                for field_spec in record_spec.fields:
                    for validator_conf in field_spec.validation:
                        try:
                            self.validate(validator_conf, record_spec.id, field_spec.id, record_pk)
                        except ValidationException as e:
                            error_handler(ErrorEvent(
                                message=str(e),
                                record_id=record_spec.id,
                                record_pk=record_pk,
                                field_id=field_spec.id,
                                validator=validator_conf['id'],
                            ))

