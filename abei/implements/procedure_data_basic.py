from abei.interfaces import (
    IProcedureData,
    IProcedureDataClass,
    IProcedureDataFactory,
)


class ProcedureDataBasic(IProcedureData):

    def __init__(self, cls, value_type, value):
        self.cls = cls
        self.value_type = value_type
        self.value = value

    def get_class(self):
        return self.cls

    def clone(self):
        return ProcedureDataBasic(
            self.cls,
            self.value_type,
            self.value,
        )

    def get_value(self):
        return self.value

    def set_value(self, value):
        try:
            self.value = (
                value if
                isinstance(value, self.value_type) else
                self.value_type(value)
            )
            return True
        except (ValueError, TypeError):
            return False


class ProcedureDataClassBasic(IProcedureDataClass):

    def __init__(
            self,
            signature,
            label,
            value_type,
            value_default,
    ):
        self.signature = signature
        self.label = label
        self.value_type = value_type
        self.value_default = value_default

    def get_signature(self):
        return self.signature

    def get_label(self):
        return self.label

    def instantiate(self, *args, data_class=None, **kwargs):
        obj = ProcedureDataBasic(
            data_class or self,
            self.value_type,
            self.value_default,
        )
        value = args[0] if args else None
        if value is not None:
            obj.set_value(value)
        return obj


data_none = ProcedureDataClassBasic(
    signature='none',
    label='none',
    value_type=type(None),
    value_default=None,
)
data_bool = ProcedureDataClassBasic(
    signature='bool',
    label='bool',
    value_type=bool,
    value_default=True,
)
data_int = ProcedureDataClassBasic(
    signature='int',
    label='int',
    value_type=int,
    value_default=0,
)
data_float = ProcedureDataClassBasic(
    signature='float',
    label='float',
    value_type=float,
    value_default=0.0,
)
data_string = ProcedureDataClassBasic(
    signature='string',
    label='string',
    value_type=str,
    value_default='',
)


class ProcedureDataFactory(IProcedureDataFactory):
    def __init__(self, service_site, **kwargs):
        self.data_classes = dict([
            (data_none.get_signature(), data_none),
            (data_bool.get_signature(), data_bool),
            (data_int.get_signature(), data_int),
            (data_float.get_signature(), data_float),
            (data_string.get_signature(), data_string),
        ])

    def create(self, class_signature, *args, **kwargs):
        data_class = self.get_class(class_signature)
        return data_class.instantiate(*args, **kwargs)

    def get_class(self, class_signature):
        data_class = self.query_class(class_signature)
        if not data_class:
            raise LookupError('data class not found')
        return data_class

    def query_class(self, class_signature):
        return self.data_classes.get(class_signature)

    def register_class(
            self,
            class_signature,
            procedure_data_class,
            **kwargs,
    ):
        if class_signature in self.data_classes:
            raise AssertionError(
                '{} already registered'.format(class_signature))
        self.data_classes[class_signature] = procedure_data_class

    def iterate_classes(self):
        return self.data_classes.keys()
