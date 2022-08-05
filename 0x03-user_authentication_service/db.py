#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Saves a user to a database """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)
            self._session.commit()
        except Exception:
            self._session.rollback()
            new_user = None
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """ Returns the first row in the 'users' table as filtered by the
        input arguments.

        The 'NoResultFound' and 'InvalidRequestError' are raised when no
        results are found or when wrong query arguments are passed respectively
        """
        keys = []
        values = []
        i = 0
        for k, v in kwargs.items():
            if not hasattr(User, k):
                raise InvalidRequestError()
            keys.append(getattr(User, k))
            values.append(v)
        row = self._session.query(User).filter(tuple_(*keys).in_(
            [tuple(values)])).first()

        if row is None:
            raise NoResultFound()

        return row

    def update_user(self, user_id: int, **kwargs) -> None:
        """ Updates a User object """
        user = self.find_user_by(id=user_id)
        for k, v in kwargs.items():
            if not hasattr(User, k):
                raise ValueError()
            user.k = v
