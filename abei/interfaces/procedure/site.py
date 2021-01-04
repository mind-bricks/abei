from .base import (
    abstractmethod,
    IService,
)


class IProcedureSite(IService):
    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure site
        :return:
        """

    @abstractmethod
    def get_procedure(self, signature, **kwargs):
        """
        get procedure instance by signature
        raise exception if no procedure found
        """

    @abstractmethod
    def query_procedure(self, signature, **kwargs):
        """
        query procedure instance by signature
        """

    @abstractmethod
    def register_procedure(self, procedure, **kwargs):
        """
        register procedure
        """

    @abstractmethod
    def iterate_procedures(self):
        """
        iterate procedures
        """

    @abstractmethod
    def get_data_class(self, signature, **kwargs):
        """
        get procedure data class by signature
        raise exception if no data found
        """

    @abstractmethod
    def query_data_class(self, signature, **kwargs):
        """
        query procedure data class by signature
        """

    @abstractmethod
    def register_data_class(self, signature, **kwargs):
        """
        register procedure data class by signature
        """

    @abstractmethod
    def iterate_data_classes(self):
        """
        iterate procedure data class
        """

    @abstractmethod
    def get_base_sites(self):
        """
        get dependent procedure sites
        :return:
        """


class IProcedureSiteFactory(IService):

    @abstractmethod
    def create(self, procedure_sites, **kwargs):
        """
        create new procedure site which depends on procedure_sites
        :param procedure_sites:
        :param kwargs:
        :return:
        """
