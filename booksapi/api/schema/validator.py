import graphene
import cerberus


class InvalidFieldValue(graphene.ObjectType):
    field = graphene.String(description="field with error")
    message = graphene.String(description="message with error")


class InvalidValuesInput(graphene.ObjectType):
    errors = graphene.List(InvalidFieldValue)


class Validate:

    error_node = None

    def __init__(self, data, schema):
        validator = cerberus.Validator()
        validator.validate(data, schema)
        if len(validator.errors) > 0:
            errors_list = []
            for field, errors in validator.errors.items():
                for error in errors:
                    errors_list.append(InvalidFieldValue(field=field, message=error))

            self.error_node = InvalidValuesInput(errors=errors_list)

    @property
    def is_valid(self):
        return self.error_node is None

    @property
    def is_invalid(self):
        return not self.is_valid