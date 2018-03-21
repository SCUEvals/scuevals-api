import factory

from scuevals_api import models


class VoteFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Vote
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    value = factory.Iterator([models.Vote.UPVOTE, models.Vote.DOWNVOTE])
