from django.contrib.auth import get_user_model

import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "gender",
        )
        convert_choices_to_enum = False

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        print(user)
        if user.is_anonymous:
            raise GraphQLError("Not logged in")
        return user


class CreateUser(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        gender = graphene.String()

    # The class attributes define the response of the mutation
    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password, **kwargs):
        user = get_user_model()(
            username=username,
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save()

        # Notice we return an instance of this mutation
        return CreateUser(user=user)


class Mutation:
    create_user = CreateUser.Field()
