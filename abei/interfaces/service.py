from abc import (
    ABCMeta,
    abstractmethod,
)

from typing import (
    Callable,
    Iterator,
    Optional,
    TextIO,
    Union,
)


def service_entry(interface, name=None):
    return ServiceEntry(interface, name)


class ServiceEntry(object):
    def __init__(self, interface, name):
        self.interface = interface
        self.name = name or ''


class IService(metaclass=ABCMeta):
    """
    the root interface for service
    """

    @classmethod
    def ensure_dependencies(cls) -> None:
        """
        install all dependencies of current service
        """


class IServiceSite(IService):
    @abstractmethod
    def get_service(self, entry: ServiceEntry) -> IService:
        """
        get service instance by service entry
        raise exception if no service found
        """

    @abstractmethod
    def query_service(self, entry: ServiceEntry) -> Optional[IService]:
        """
        query service instance by service entry
        """

    @abstractmethod
    def register_service(
            self,
            entries: Iterator[ServiceEntry],
            service_class: Callable,
            **kwargs,
    ) -> IService:
        """
        register service with service entries
        """


class IServiceBuilder(IService):

    @abstractmethod
    def load_json(
            self,
            service_site: IServiceSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        register service to service site by reading configuration file
        """

    @abstractmethod
    def save_json(
            self,
            service_site: IServiceSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        save service from service site to configuration file
        """

    @abstractmethod
    def load_yaml(
            self,
            service_site: IServiceSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        register service to service site by reading configuration file
        """

    @abstractmethod
    def save_yaml(
            self,
            service_site: IServiceSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        save service from service site to configuration file
        """
