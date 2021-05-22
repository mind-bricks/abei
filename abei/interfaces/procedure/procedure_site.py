from typing import Iterator

from ..service import (
    abstractmethod,
    IService,
)


class IProcedureSite(IService):
    """
    site of procedure func class
    """

    def iterator_dependencies(self) -> Iterator[IService]:
        """
        get dependent sites
        :return iterator of IProcedureSite:
        """

    def add_dependency(self, procedure_site: IService) -> bool:
        """
        add another procedure site as a dependency of current site
        :param procedure_site: IProcedureSite
        :return bool:
        """

    def del_dependency(self, procedure_site: IService) -> bool:
        """
        delete a procedure site on which is being depended by current site
        :param procedure_site: IProcedureSite
        :return bool:
        """


class IProcedureSiteClass(IService):

    @abstractmethod
    def instantiate(self, *args, **kwargs) -> IProcedureSite:
        """
        create new procedure site
        :param args:
        :param kwargs:
        :return:
        """
