from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.exc import NoResultFound as ORMNoResultFound
from sqlalchemy.exc import OperationalError
from sqlalchemy import func
from datetime import datetime
from .logger import Logger
from time import sleep
Base = declarative_base()


class ORM:
    engine: Engine
    session: Session  # type: Session

    def __init__(self, db_string: str):
        Logger.info('ORM is initializing')
        self.engine = create_engine(db_string, echo=False)
        self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=True)()
        Base.metadata.create_all(self.engine)


class ProcessedElementLog(Base):
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_NOT_TAKEN = ''
    STATUS_DONE = 'done'

    """
    Model for a history of all processed/in-progress items
    """

    __tablename__ = 'riotkit_kropotcli_processed_element_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    element_id = Column(String, nullable=False)
    element_type = Column(String, nullable=False)
    element_date = Column(DateTime, nullable=False)
    element_tz = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
    status = Column(String, nullable=True)
    node = Column(String, nullable=False)
    crypto_iv = Column(String, nullable=True)

    def mark_as_in_progress(self, instance_name: str):
        self.status = self.STATUS_IN_PROGRESS
        self.node = instance_name

    def mark_as_processed(self):
        self.processed_at = datetime.now()
        self.status = self.STATUS_DONE

    def to_raw_event(self) -> dict:
        """ Return as raw event that comes in from API """

        date: datetime = self.element_date

        return {
            'id': self.element_id,
            'type': self.element_type,
            'date': int(date.timestamp()),
            'tz': self.element_tz,
            'form': self.data
        }


class LogRepository:
    """
    Repository - interacts with database, operating on ProcessedElementLog model
    """

    _orm: ORM

    def __init__(self, orm: ORM):
        self._orm = orm

    def persist(self, log: ProcessedElementLog):
        try:
            self._orm.session.add(log)
            self._orm.session.flush([log])
            Logger.debug('Flushing: %s, %s' % (log.element_id, log.status))

        except OperationalError:
            Logger.info('Database locked, waiting')
            sleep(1)
            self.persist(log)

    def find_last_processed_element_date(self, entry_type: str) -> datetime:
        return self._orm.session.query(func.max(ProcessedElementLog.element_date))\
            .filter(ProcessedElementLog.element_type == entry_type)\
            .scalar()

    def find(self, entry_type: str, entry_id: str) -> ProcessedElementLog:
        return self._orm.session.query(ProcessedElementLog)\
            .filter(ProcessedElementLog.element_type == entry_type, ProcessedElementLog.element_id == entry_id) \
            .order_by(ProcessedElementLog.element_date.asc()) \
            .limit(1)\
            .one()

    def exists(self, entry_type: str, entry_id: str) -> bool:
        try:
            self.find(entry_type, entry_id)
            return True

        except ORMNoResultFound:
            return False

    def find_all_not_finished_elements(self, instance_name: str) -> list:
        return self._orm.session.query(ProcessedElementLog)\
            .filter(
                ProcessedElementLog.status != ProcessedElementLog.STATUS_DONE,
                ProcessedElementLog.node == instance_name
            )\
            .order_by(ProcessedElementLog.element_date.asc())\
            .all()

    def find_or_create(self, entry_type: str, entry_id: str,
                       date: datetime, tz: str, form: str) -> ProcessedElementLog:
        try:
            return self.find(entry_type, entry_id)

        except ORMNoResultFound:
            log = ProcessedElementLog()
            log.element_id = entry_id
            log.element_type = entry_type
            log.element_date = date
            log.element_tz = tz
            log.data = form
            log.processed_at = datetime.now()
            log.crypto_iv = None

            return log

    def was_already_processed(self, entry_type: str, entry_id: str):
        try:
            element = self.find(entry_type, entry_id)
            return element.status == ProcessedElementLog.STATUS_DONE

        except ORMNoResultFound:
            return False
