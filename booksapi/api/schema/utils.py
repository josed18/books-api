import graphene


class ObjectError:
    code = graphene.String(description="code of the error")
    message = graphene.String(description="message with error")
