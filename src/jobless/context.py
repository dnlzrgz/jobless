from sqlalchemy.orm import sessionmaker

from jobless.mapper import Mapper


class AppContext:
    def __init__(
        self,
        session_factory: sessionmaker,
        mapper: Mapper,
    ) -> None:
        self.session_factory = session_factory
        self.mapper = mapper

    def get_session(self):
        return self.session_factory()
