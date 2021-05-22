from typing import (
    Dict,
    Iterator,
    Optional,
    Tuple,
)

from .procedure_func import (
    IProcedureFunc
)
from ..service import (
    abstractmethod,
    IService,
)


class IProcedureLink(IService):
    """
    procedure function reference
    """

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure func ref
        :return str: this signature is probably an dynamic generated one
        """

    @abstractmethod
    def get_ref_func(self) -> IProcedureFunc:
        """
        get procedure func to which current link is referencing
        :return IProcedureFunc:
        """

    @abstractmethod
    def get_imp_func(self) -> IProcedureFunc:
        """
        get procedure func of which current link is implementing
        :return IProcedureFunc:
        """

    @abstractmethod
    def get_links(self) -> Dict[int, Tuple[int, Optional[IService]]]:
        """
        get links map of procedure func ref with type of
        Dict[int, Tuple(int, Optional[IProcedureLink])]
        :return: map of procedure links
        """

    @abstractmethod
    def link(
            self,
            input_index: int,
            func_output_index: int,
            func_ref: Optional[IService],
    ) -> bool:
        """
        link procedure func
        :param input_index:
        :param func_output_index:
        :param func_ref: IProcedureLink or None
        :return bool: succeed or not
        """

    @abstractmethod
    def unlink(
            self,
            input_index: int
    ) -> bool:
        """
        unlink procedure func
        :param input_index:
        :return bool: succeed or not
        """


class IProcedureLinkSite(IService):
    """
    procedure link site
    """

    def add_link(
            self,
            procedure_func: Optional[IProcedureFunc],
    ) -> IProcedureLink:
        """
        add link
        :param procedure_func:
        :return IProcedureLink:
        """

    def del_link(self, signature: str) -> bool:
        """
        delete link
        :param signature:
        :return bool:
        """

    def iterate_links(self) -> Iterator[IProcedureLink]:
        """
        iterate links in this site
        :return Iterator[IProcedureLink]:
        """
