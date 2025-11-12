import factory

from apps.users.models import BNBUser, UserToken


class UserFactory(factory.Factory):
    class Meta:
        model = BNBUser

    first_name = factory.Sequence(lambda n: "john%s" % n)
    last_name = factory.Sequence(lambda n: "doe%s" % n)
    email = factory.LazyAttribute(lambda o: "%s@example.org" % o.username)


class UserTokenFactory(factory.Factory):
    class Meta:
        model = UserToken

    user = factory.SubFactory(UserFactory)
