from typing import (
    TextIO,
    Union,
)

from .procedure_site import (
    IProcedureSite,
)
from ..service import (
    abstractmethod,
    IService,
)


class IProcedureBuilder(IService):
    """
    procedure builder
    """

    @abstractmethod
    def load_json(
            self,
            procedure_site: IProcedureSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def save_json(
            self,
            procedure_site: IProcedureSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def load_yaml(
            self,
            procedure_site: IProcedureSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def save_yaml(
            self,
            procedure_site: IProcedureSite,
            file_or_filename: Union[str, TextIO],
    ):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """
