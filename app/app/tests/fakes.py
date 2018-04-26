"""A bunch of fake objects for integration testing"""


class Fake(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeUser(Fake):
    def __init__(self, name, avatar_url):
        super(FakeUser, self).__init__(name=name,
                                       avatar_url=avatar_url)


class FakeRepo(Fake):
    def __init__(self, name):
        super(FakeRepo, self).__init__(name=name)


class FakeMileStone(Fake):

    def __init__(self, title, number, due_on, state):
        super(FakeMileStone, self).__init__(
            title=title,
            number=number,
            due_on=due_on,
            state=state)
