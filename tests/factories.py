import factory
from factory.alchemy import SQLAlchemyModelFactory

from jobless import models
from jobless.enums import Location, Status


class SkillFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Skill
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"skill-{n}")


class CompanyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Company
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"Company {n}")
    url = factory.Sequence(lambda n: f"https://company-{n}.example.com")
    industry = factory.Faker("bs")


class ContactFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Contact
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"contact{n}@example.com")
    phone = factory.Sequence(lambda n: f"+1555{n:07d}")
    url = factory.Sequence(lambda n: f"https://contact-{n}.example.com")


class ApplicationFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Application
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    title = factory.Faker("job")
    description = factory.Faker("text")
    salary = factory.LazyAttribute(
        lambda _: f"${factory.Faker('random_int', min=50, max=200)}k"
    )
    url = factory.Sequence(lambda n: f"https://{n}.example.com")
    location_type = Location.ON_SITE
    status = Status.SAVED
    company = factory.SubFactory(CompanyFactory)

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if extracted:
            self.skills = list(extracted)

    @factory.post_generation
    def contacts(self, create, extracted, **kwargs):
        if extracted:
            self.contacts = list(extracted)
