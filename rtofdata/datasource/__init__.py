import abc

from rtofdata.parser.parser import DataEvent


class DataSource(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'update') and
                callable(subclass.update) and
                hasattr(subclass, 'get_records_by_type') and
                callable(subclass.get_records_by_type) or
                hasattr(subclass, 'get_single_record') and
                callable(subclass.get_single_record) or
                NotImplemented)

    @abc.abstractmethod
    def update(self, event: DataEvent):
        raise NotImplementedError

    @abc.abstractmethod
    def get_records_by_type(self, record: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_single_record(self, record: str, *keys):
        raise NotImplementedError
