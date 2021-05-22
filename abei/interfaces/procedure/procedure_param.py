from typing import (
    Any,
    Iterator,
    Optional,
)

from ..service import (
    abstractmethod,
    IService,
)


class IProcedureParam(IService):
    """
    procedure parameter
    """

    @abstractmethod
    def get_class(self) -> IService:
        """
        get class of procedure param
        :return IProcedureParamClass:
        """

    @abstractmethod
    def get_value(self) -> Any:
        """
        get data value
        :return value:
        """

    @abstractmethod
    def set_value(self, value: Any) -> bool:
        """
        set data value
        :param value:
        :return boolean:
        """


class IProcedureParamClass(IService):

    @abstractmethod
    def get_signature(self) -> str:
        """
        get signature of procedure param class
        :return:
        """

    @abstractmethod
    def get_docstring(self) -> str:
        """
        get document string of procedure param class
        :return str:
        """

    @abstractmethod
    def set_docstring(self, doc: str) -> bool:
        """
        set document string of procedure param class
        :param doc:
        :return bool: succeed or not
        """

    @abstractmethod
    def instantiate(self, *args, **kwargs) -> IProcedureParam:
        """
        instantiate procedure param
        :return IProcedureParam:
        """


class IProcedureParamClassSite(IService):

    @abstractmethod
    def get_class(self, signature: str) -> IProcedureParamClass:
        """
        :param signature: class signature
        :return IProcedureParamClass:
        """

    @abstractmethod
    def query_class(self, signature: str) -> Optional[IProcedureParamClass]:
        """
        :param signature:
        :return IProcedureParamClass:
        """

    @abstractmethod
    def register_class(
            self,
            procedure_param_class: IProcedureParamClass,
            **kwargs,
    ):
        """
        :param procedure_param_class:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def iterate_classes(self) -> Iterator[IProcedureParamClass]:
        """
        :return:
        """
