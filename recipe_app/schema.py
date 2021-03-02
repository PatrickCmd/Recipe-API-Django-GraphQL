import graphene
import graphql_jwt

import auth_user.schema
import api.schema


class Query(
    auth_user.schema.Query,
    api.schema.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    auth_user.schema.Mutation,
    api.schema.Mutation,
    graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
