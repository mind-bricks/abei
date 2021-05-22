from typing import (
    Dict,
    Iterator,
    Optional,
)

from .procedure_param import (
    IProcedureParam
)
from ..service import (
    abstractmethod,
    IService,
)


class IProcedureFunc(IService):
    """
    procedure function
    """

    @abstractmethod
    def get_class(self) -> IService:
        """
        get class interface of current procedure func
        actually the return object should be IProcedureFuncClass
        :return: IProcedureFuncClass
        """

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure
        :return: str
        """

    @abstractmethod
    def get_input_signatures(self) -> Dict[int, str]:
        """
        get map of input signatures with type of dict[int, str]
        where int indicate input index
        and str indicate input signature
        :return : dict[int, str]
        """

    @abstractmethod
    def get_output_signatures(self) -> Dict[int, str]:
        """
        get map of output signatures with type of dict[int, str]
        where int indicate output index
        and str indicate output signature
        :return: dict[int, str]
        """

    @abstractmethod
    def get_docstring(self) -> str:
        """
        get document string of procedure
        :return: str
        """

    @abstractmethod
    def set_docstring(self, docstring: str) -> bool:
        """
        set document string of procedure
        :param docstring:
        :return bool: succeed or not
        """

    @abstractmethod
    def run(
            self,
            procedure_args: Dict[int, IProcedureParam],
            **kwargs,
    ) -> Dict[int, IProcedureParam]:
        """
        :param procedure_args:
            input data with type of dict[int, IProcedureParam]
            where int indicate input index
        :param kwargs: extra arguments
        :return dict[int, IProcedureParam]:
        """


class IProcedureFuncSite(IService):
    """
    procedure function site
    """

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure site
        :return str:
        """

    @abstractmethod
    def get_func(self, signature: str, **kwargs) -> IProcedureFunc:
        """
        get procedure func instance by signature
        raise exception if no procedure func found
        :param signature: signature of procedure func
        :return IProcedureFunc:
        """

    @abstractmethod
    def query_func(
            self, signature: str, **kwargs) -> Optional[IProcedureFunc]:
        """
        query procedure instance by signature
        :param signature: signature of procedure func
        :return IProcedureFunc:
        """

    @abstractmethod
    def register_func(self, procedure_func: IProcedureFunc, **kwargs) -> bool:
        """
        register procedure
        :param procedure_func: procedure func
        :param kwargs:
        :return bool: succeed or not
        """

    @abstractmethod
    def iterate_funcs(self) -> Iterator[IProcedureFunc]:
        """
        iterate funcs
        :return iterator of IProcedureFunc:
        """


class IProcedureFuncClass(IService):
    """
    class of procedure function,
    you might consider it as a template class for procedure func
    """

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure func class
        :return: str
        """

    @abstractmethod
    def get_docstring(self) -> str:
        """
        get document string of procedure func class
        :return: str
        """

    @abstractmethod
    def instantiate(self, *args, **kwargs) -> IProcedureFunc:
        """
        instantiate procedure func class
        """


class IProcedureFuncClassSite(IService):
    """
    site of procedure function class
    """

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure func class site
        :return str:
        """

    @abstractmethod
    def get_class(self, signature: str) -> IProcedureFuncClass:
        """
        :param signature: signature of procedure func class
        :return IProcedureFuncClass:
        may raise exception if procedure func class not found
        """

    @abstractmethod
    def query_class(self, signature: str) -> Optional[IProcedureFuncClass]:
        """
        :param signature: signature of procedure func class
        :return IProcedureFuncClass:
        """

    @abstractmethod
    def register_class(
            self,
            procedure_func_class: IProcedureFuncClass,
            **kwargs,
    ) -> bool:
        """
        register procedure func class
        :param procedure_func_class: procedure func class instance
        :param kwargs:
        :return bool: succeed or not
        """

    @abstractmethod
    def iterate_classes(self) -> Iterator[IProcedureFuncClass]:
        """
        iterate procedure func classes
        :return iterator of procedure func classes:
        """
