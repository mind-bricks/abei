from .base import (
    abstractmethod,
    IService,
)


class IProcedureData(IService):

    @abstractmethod
    def get_class(self):
        """
        get class of procedure data
        :return:
        """

    @abstractmethod
    def clone(self):
        """
        clone procedure data
        :return:
        """

    @abstractmethod
    def get_value(self):
        """
        get data value
        :return value:
        """

    @abstractmethod
    def set_value(self, value):
        """
        set data value
        :param value:
        :return boolean:
        """


class IProcedureDataClass(IService):

    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure data class
        :return:
        """

    @abstractmethod
    def get_label(self):
        """
        get label of procedure class
        :return:
        """

    @abstractmethod
    def instantiate(self, *args, **kwargs):
        """
        instantiate procedure data
        """


class IProcedureDataFactory(IService):

    @abstractmethod
    def create(self, class_signature, *args, **kwargs):
        """
        create procedure data directly
        :param class_signature:
        :param args:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def get_class(self, class_signature):
        """
        :param class_signature:
        :return:
        """

    @abstractmethod
    def query_class(self, class_signature):
        """
        :param class_signature:
        :return:
        """

    @abstractmethod
    def register_class(self, class_signature, procedure_data_class, **kwargs):
        """
        :param class_signature:
        :param procedure_data_class:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def iterate_classes(self):
        """
        :return:
        """
