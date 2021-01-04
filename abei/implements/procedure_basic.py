from abei.interfaces import (
    IProcedure,
    IProcedureClass,
    IProcedureFactory,
    IProcedureData,
    IProcedureLink,
)
from .procedure_joint_basic import (
    joint_validate,
    joint_run,
)


class ProcedureBasic(IProcedure):
    signature = 'NA'
    docstring = 'NA'
    input_signatures = []
    output_signatures = []

    def __init__(
            self,
            signature=None,
            docstring=None,
            input_signatures=None,
            output_signatures=None,
            **kwargs,
    ):
        self.signature = signature or self.signature
        self.docstring = docstring or self.docstring
        self.input_signatures = input_signatures or self.input_signatures
        self.output_signatures = output_signatures or self.output_signatures

    def get_signature(self):
        return self.signature

    def get_input_signatures(self):
        return self.input_signatures

    def get_output_signatures(self):
        return self.output_signatures

    def get_docstring(self):
        return self.docstring

    def set_docstring(self, docstring):
        self.docstring = docstring

    def run(self, procedure_data_list, **kwargs):
        # assert isinstance(kwargs.setdefault('procedure_cache', {}), dict)
        return (
            self.run_normally(procedure_data_list, **kwargs) if
            self.run_validation(
                procedure_data_list, self.input_signatures) else
            self.run_exceptionally(procedure_data_list, **kwargs)
        )

    @staticmethod
    def run_validation(procedure_data_list, signatures):
        if len(procedure_data_list) != len(signatures):
            raise AssertionError('invalid data list')

        has_missing_params = False
        for d, sig in zip(procedure_data_list, signatures):
            if d is None:
                has_missing_params = True
                continue
            if not isinstance(d, IProcedureData):
                raise AssertionError('invalid data list')
            if d.get_class().get_signature() != sig:
                raise AssertionError('data signature miss match')

        return not has_missing_params

    def run_normally(self, procedure_data_list, **kwargs):
        return [None] * len(self.output_signatures)

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return [None] * len(self.output_signatures)


class ProcedureClassBasic(IProcedureClass):
    def __init__(
            self,
            signature,
            docstring,
            procedure_type,
            **kwargs,
    ):
        self.signature = signature
        self.docstring = docstring
        self.procedure_type = procedure_type
        self.kwargs = kwargs

    def get_signature(self):
        return self.signature

    def get_docstring(self):
        return self.docstring

    def instantiate(
            self,
            *args,
            **kwargs,
    ):
        kwargs.update(self.kwargs)
        kwargs.update(
            signature=self.generate_signature(**kwargs),
            docstring=self.generate_docstring(**kwargs)
        )
        return self.procedure_type(*args, **kwargs)

    def generate_signature(self, data_class=None, **kwargs):
        if not data_class:
            return self.signature

        return '{}[{}]'.format(self.signature, data_class.get_label())

    def generate_docstring(self, data_class=None, **kwargs):
        if not data_class:
            return self.docstring

        return '{} for {}'.format(self.docstring, data_class.get_signature())


class ProcedureComposite(IProcedureLink, ProcedureBasic):
    output_joints = []
    output_indices = []

    def get_joints(self):
        return [(f, i) for f, i in zip(
            self.output_joints, self.output_indices)]

    def set_joints(self, joints, indices):
        joint_validate(
            joints,
            indices,
            self,
            self.output_signatures,
        )
        self.output_joints = joints
        self.output_indices = indices

    def run_normally(self, procedure_data_list, **kwargs):
        return [
            joint_run(joint, procedure_data_list, **kwargs)[i] if
            joint else procedure_data_list[i]
            for joint, i in self.get_joints()
        ]


class ProcedureClassComposite(IProcedureClass):
    def get_signature(self):
        return 'composite'

    def get_docstring(self):
        return 'composite procedure class'

    def instantiate(self, *args, **kwargs):
        return ProcedureComposite(*args, **kwargs)


class ProcedureUnaryOperator(ProcedureBasic):

    def __init__(
            self,
            *args,
            native_function=None,
            data_class=None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        self.input_signatures = [data_class.get_signature()]
        self.output_signatures = [data_class.get_signature()]
        self.native_function = native_function

    def run_normally(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value()))
        return [ret]


class ProcedureBinaryOperator(ProcedureBasic):
    # native_function = staticmethod(lambda x, y: x)

    def __init__(
            self,
            *args,
            native_function=None,
            data_class=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        self.input_signatures = [
            data_class.get_signature(),
            data_class.get_signature(),
        ]
        self.output_signatures = [
            data_class.get_signature(),
        ]
        self.native_function = native_function

    def run_normally(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureComparator(ProcedureBasic):
    def __init__(
            self,
            *args,
            native_function=None,
            data_class=None,
            bool_class=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        assert bool_class
        self.input_signatures = [
            data_class.get_signature(),
            data_class.get_signature(),
        ]
        self.output_signatures = [
            bool_class.get_signature(),
        ]
        self.bool_class = bool_class
        self.native_function = native_function

    def run_normally(self, procedure_data_list, **kwargs):
        ret = self.bool_class.instantiate(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureProbe(ProcedureBasic):
    def __init__(
            self,
            *args,
            data_class=None,
            bool_class=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        assert bool_class
        self.input_signatures = [
            data_class.get_signature(),
        ]
        self.output_signatures = [
            bool_class.get_signature(),
        ]
        self.bool_class = bool_class

    def run_normally(self, procedure_data_list, **kwargs):
        return [
            self.bool_class.instantiate(bool(
                procedure_data_list[0].get_value() is not None))
        ]

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return self.run_normally(procedure_data_list, **kwargs)


class ProcedureDiverge2(ProcedureBasic):

    def __init__(
            self,
            *args,
            data_class=None,
            bool_class=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        assert bool_class
        self.input_signatures = [
            bool_class.get_signature(),
            data_class.get_signature(),
        ]
        self.output_signatures = [
            data_class.get_signature(),
            data_class.get_signature(),
        ]

    def run_normally(self, procedure_data_list, **kwargs):
        flag = procedure_data_list[0].get_value()
        ret = procedure_data_list[1]
        return flag and [ret, None] or [None, ret]

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return self.run_normally(procedure_data_list, **kwargs)


class ProcedureConverge2(ProcedureBasic):

    def __init__(
            self,
            *args,
            data_class=None,
            bool_class=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        assert bool_class
        self.input_signatures = [
            bool_class.get_signature(),
            data_class.get_signature(),
            data_class.get_signature(),
        ]
        self.output_signatures = [
            data_class.get_signature(),
        ]

    def run_normally(self, procedure_data_list, **kwargs):
        flag = procedure_data_list[0].get_value()
        ret = procedure_data_list[flag and 1 or 2]
        return [ret]

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return self.run_normally(procedure_data_list, **kwargs)


class ProcedureCast(ProcedureBasic):

    def __init__(
            self,
            *args,
            data_class=None,
            data_class_to=None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert data_class
        self.input_signatures = [data_class.get_signature()]
        self.output_signatures = [data_class_to.get_signature()]
        self.data_class_to = data_class_to

    def run_normally(self, procedure_data_list, **kwargs):
        ret = self.data_class_to.instantiate(
            procedure_data_list[0].get_value())
        return [ret]


# composite procedure class ------------------------------
procedure_class_composite = ProcedureClassComposite()

# bool procedure classes ----------------------------------
procedure_class_not = ProcedureClassBasic(
    signature='not',
    docstring='logic not',
    procedure_type=ProcedureUnaryOperator,
    native_function=lambda x: not x,
)
procedure_class_and = ProcedureClassBasic(
    signature='and',
    docstring='logic and',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x and y,
)
procedure_class_or = ProcedureClassBasic(
    signature='or',
    docstring='logic or',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x or y,
)

# calculation procedure classes ---------------------------
procedure_class_negate = ProcedureClassBasic(
    signature='neg',
    docstring='negate operator',
    procedure_type=ProcedureUnaryOperator,
    native_function=lambda x: not x,
)
procedure_class_add = ProcedureClassBasic(
    signature='add',
    docstring='add operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x + y,
)
procedure_class_subtract = ProcedureClassBasic(
    signature='sub',
    docstring='subtract operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x - y,
)
procedure_class_multiply = ProcedureClassBasic(
    signature='mul',
    docstring='multiply operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x * y,
)
procedure_class_divide = ProcedureClassBasic(
    signature='div',
    docstring='divide operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x / y,
)
procedure_class_modulo = ProcedureClassBasic(
    signature='mod',
    docstring='modulo operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x % y,
)
procedure_class_mod_divide = ProcedureClassBasic(
    signature='modDiv',
    docstring='modulo divide operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x // y,
)
procedure_class_square = ProcedureClassBasic(
    signature='sq',
    docstring='square operator',
    procedure_type=ProcedureUnaryOperator,
    native_function=lambda x: x * x,
)
procedure_class_power = ProcedureClassBasic(
    signature='pow',
    docstring='power operator',
    procedure_type=ProcedureBinaryOperator,
    native_function=lambda x, y: x ** y,
)

# comparision procedure classes ---------------------------
procedure_class_equal = ProcedureClassBasic(
    signature='eq',
    docstring='equal',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x == y,
)
procedure_class_not_equal = ProcedureClassBasic(
    signature='ne',
    docstring='not equal',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x != y,
)
procedure_class_less_than = ProcedureClassBasic(
    signature='lt',
    docstring='less than',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x < y,
)
procedure_class_less_than_or_equal = ProcedureClassBasic(
    signature='lte',
    docstring='less than or equal',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x <= y,
)
procedure_class_greater_than = ProcedureClassBasic(
    signature='gt',
    docstring='greater than',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x > y,
)
procedure_class_greater_than_or_equal = ProcedureClassBasic(
    signature='gte',
    docstring='greater than or equal',
    procedure_type=ProcedureComparator,
    native_function=lambda x, y: x >= y,
)

# probe class --------------------------------------------
procedure_class_probe = ProcedureClassBasic(
    signature='probe',
    docstring='probe',
    procedure_type=ProcedureProbe,
)

# data class cast -----------------------------------------
procedure_class_cast_2_bool = ProcedureClassBasic(
    signature='castToBool',
    docstring='cast to bool',
    procedure_type=ProcedureCast,
    native_function=lambda x: bool(x),
)
procedure_class_cast_2_int = ProcedureClassBasic(
    signature='castToInt',
    docstring='cast to int',
    procedure_type=ProcedureCast,
    native_function=lambda x: int(x),
)
procedure_class_cast_2_float = ProcedureClassBasic(
    signature='castToFloat',
    docstring='cast to float',
    procedure_type=ProcedureCast,
    native_function=lambda x: float(x),
)

# data flow control ---------------------------------------
procedure_class_diverge = ProcedureClassBasic(
    signature='diverge2',
    docstring='diverge 1 branch to 2',
    procedure_type=ProcedureDiverge2,
)
procedure_class_converge = ProcedureClassBasic(
    signature='converge2',
    docstring='converge 2 branches to 1',
    procedure_type=ProcedureConverge2,
)


# implement procedure class factory -----------------------
class ProcedureFactory(IProcedureFactory):
    """
    basic procedure class factory
    """

    def __init__(self, service_site, **kwargs):
        self.procedure_classes = {
            p.get_signature(): p for p in [
                procedure_class_composite,

                procedure_class_or,
                procedure_class_and,
                procedure_class_not,

                procedure_class_negate,
                procedure_class_add,
                procedure_class_subtract,
                procedure_class_multiply,
                procedure_class_divide,
                procedure_class_modulo,
                procedure_class_mod_divide,
                procedure_class_square,
                procedure_class_power,

                procedure_class_equal,
                procedure_class_not_equal,
                procedure_class_greater_than,
                procedure_class_greater_than_or_equal,
                procedure_class_less_than,
                procedure_class_less_than_or_equal,

                procedure_class_probe,

                procedure_class_cast_2_bool,
                procedure_class_cast_2_int,
                procedure_class_cast_2_float,

                procedure_class_diverge,
                procedure_class_converge,
            ]
        }

    def create(self, class_signature, *args, **kwargs):
        procedure_class = self.get_class(class_signature)
        return procedure_class.instantiate(*args, **kwargs)

    def get_class(self, class_signature):
        procedure_class = self.query_class(class_signature)
        if not procedure_class:
            raise LookupError('procedure class not found')
        return procedure_class

    def query_class(self, class_signature):
        return self.procedure_classes.get(class_signature)

    def register_class(self, class_signature, procedure_class, **kwargs):
        assert isinstance(procedure_class, IProcedureClass)
        if class_signature in self.procedure_classes:
            raise AssertionError(
                '{} already registered'.format(class_signature))
        self.procedure_classes[class_signature] = procedure_class

    def iterate_classes(self):
        return self.procedure_classes.keys()
