from typing import (
    Any,
    Dict,
    Iterator,
    Optional,
)

from abei.interfaces import (
    IProcedureParam,
    IProcedureParamClass,
    IProcedureParamClassSite,
)


class ProcedureParamBasic(IProcedureParam):

    def __init__(
            self,
            cls: IProcedureParamClass,
            value_type: Any,
            value: Any,
    ):
        self.cls = cls
        self.value_type = value_type
        self.value = value

    def get_class(self) -> IProcedureParamClass:
        return self.cls

    def get_value(self) -> Any:
        return self.value

    def set_value(self, value: Any) -> bool:
        try:
            self.value = (
                value if
                isinstance(value, self.value_type) else
                self.value_type(value)
            )
            return True
        except (ValueError, TypeError):
            return False


class ProcedureParamClassBasic(IProcedureParamClass):

    def __init__(
            self,
            signature: str,
            docstring: str,
            value_type: Any,
            value_default: Any,
    ):
        self.signature = signature
        self.docstring = docstring
        self.value_type = value_type
        self.value_default = value_default

    def get_signature(self) -> str:
        return self.signature

    def get_docstring(self) -> str:
        return self.docstring

    def set_docstring(self, doc: str) -> bool:
        return False

    def instantiate(
            self,
            *args,
            procedure_param_class=None,
            **kwargs
    ) -> IProcedureParam:
        obj = ProcedureParamBasic(
            procedure_param_class or self,
            self.value_type,
            self.value_default,
        )
        value = args[0] if args else None
        if value is not None:
            obj.set_value(value)
        return obj


data_none = ProcedureParamClassBasic(
    signature='none',
    docstring='none',
    value_type=type(None),
    value_default=None,
)
data_bool = ProcedureParamClassBasic(
    signature='bool',
    docstring='bool',
    value_type=bool,
    value_default=True,
)
data_int = ProcedureParamClassBasic(
    signature='int',
    docstring='int',
    value_type=int,
    value_default=0,
)
data_float = ProcedureParamClassBasic(
    signature='float',
    docstring='float',
    value_type=float,
    value_default=0.0,
)
data_string = ProcedureParamClassBasic(
    signature='string',
    docstring='string',
    value_type=str,
    value_default='',
)


class ProcedureParamClassSite(IProcedureParamClassSite):
    def __init__(self, service_site, **kwargs):
        self.data_classes: Dict[str, IProcedureParamClass] = dict([
            (data_none.get_signature(), data_none),
            (data_bool.get_signature(), data_bool),
            (data_int.get_signature(), data_int),
            (data_float.get_signature(), data_float),
            (data_string.get_signature(), data_string),
        ])

    def get_class(self, signature) -> IProcedureParamClass:
        data_class = self.query_class(signature)
        if not data_class:
            raise LookupError('data class not found')
        return data_class

    def query_class(
            self, signature
    ) -> Optional[IProcedureParamClass]:
        return self.data_classes.get(signature)

    def register_class(
            self,
            procedure_data_class: IProcedureParamClass,
            **kwargs,
    ) -> bool:
        signature = procedure_data_class.get_signature()
        if signature in self.data_classes:
            return False

        self.data_classes[signature] = procedure_data_class
        return True

    def iterate_classes(self) -> Iterator[IProcedureParamClass]:
        return iter(self.data_classes.values())
