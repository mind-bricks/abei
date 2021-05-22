from typing import (
    Dict,
    Optional
)

from abei.interfaces import (
    IProcedureFunc,
    IProcedureFuncClass,
    IProcedureParam,
    IProcedureLink,
)


class ProcedureFuncBasic(IProcedureFunc):
    signature = 'NA'
    docstring = 'NA'
    input_signatures = {}
    output_signatures = {}

    def __init__(
            self,
            procedure_func_class: IProcedureFuncClass,
            signature: Optional[str] = None,
            docstring: Optional[str] = None,
            input_signatures: Optional[Dict[int, str]] = None,
            output_signatures: Optional[Dict[int, str]] = None,
            **kwargs,
    ):
        self.procedure_func_class = procedure_func_class
        self.signature: str = signature or self.signature
        self.docstring: str = docstring or self.docstring
        self.input_signatures = input_signatures or self.input_signatures
        self.output_signatures = output_signatures or self.output_signatures

    def get_class(self):
        return self.procedure_func_class

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

    def valid_input(self, procedure_args):
        if len(procedure_args) != len(self.input_signatures):
            raise AssertionError('invalid data list')

        has_missing_params = False
        for i, arg in procedure_args.items():
            if arg is None:
                has_missing_params = True
                continue

            sig = self.input_signatures.get(i)
            if sig is None:
                raise AssertionError(f'invalid procedure arg index {i}')

            if not isinstance(arg, IProcedureParam):
                raise AssertionError(f'invalid procedure arg {str(arg)}')

            if arg.get_class().get_signature() != sig:
                raise AssertionError('procedure arg signature miss match')

        return not has_missing_params

    def run(self, procedure_args, **kwargs):
        if not self.valid_input(procedure_args):
            return self.run_exceptionally(procedure_args, **kwargs)

        return self.run_normally(procedure_args, **kwargs)

    def run_normally(self, procedure_args, **kwargs):
        return {i: None for i in self.output_signatures.keys()}

    def run_exceptionally(self, procedure_args, **kwargs):
        return {i: None for i in self.output_signatures.keys()}


class ProcedureFuncClassBasic(IProcedureFuncClass):
    def __init__(
            self,
            signature,
            docstring,
            procedure_func_type,
            **kwargs,
    ):
        self.signature = signature
        self.docstring = docstring
        self.procedure_type = procedure_func_type
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


class ProcedureFuncComposite(ProcedureFuncBasic, IProcedureLink):
    output_joints = []
    output_indices = []
    indices = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_ref_func(self):
        pass

    def get_imp_func(self):
        pass

    def get_links(self):
        pass

    def link(
            self,
            input_index: int,
            func_output_index: int,
            func_ref,
    ):
        pass

    def unlink(
            self,
            input_index: int
    ):
        pass

    def run_normally(self, procedure_args, **kwargs):
        return {
            # i: (
            #     joint_run(
            #         in_joint,
            #         procedure_data_list,
            #         **kwargs
            #     )[in_i] if
            #     in_joint else procedure_data_list[in_i]
            # )
            # for in_joint, in_i, i in self.get_joints()
        }


class ProcedureClassComposite(IProcedureClass):
    def get_signature(self):
        return 'composite'

    def get_docstring(self):
        return 'composite procedure class'

    def instantiate(self, *args, **kwargs):
        return ProcedureFuncComposite(*args, **kwargs)


class ProcedureFuncUnaryOperator(ProcedureFuncBasic):

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


class ProcedureFuncBinaryOperator(ProcedureFuncBasic):
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


class ProcedureFuncComparator(ProcedureFuncBasic):
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


class ProcedureFuncProbe(ProcedureFuncBasic):
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


class ProcedureFuncDiverge2(ProcedureFuncBasic):

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


class ProcedureFuncConverge2(ProcedureFuncBasic):

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


class ProcedureFuncCast(ProcedureFuncBasic):

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
procedure_class_not = ProcedureFuncClassBasic(
    signature='not',
    docstring='logic not',
    procedure_func_type=ProcedureFuncUnaryOperator,
    native_function=lambda x: not x,
)
procedure_class_and = ProcedureFuncClassBasic(
    signature='and',
    docstring='logic and',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x and y,
)
procedure_class_or = ProcedureFuncClassBasic(
    signature='or',
    docstring='logic or',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x or y,
)

# calculation procedure classes ---------------------------
procedure_class_negate = ProcedureFuncClassBasic(
    signature='neg',
    docstring='negate operator',
    procedure_func_type=ProcedureFuncUnaryOperator,
    native_function=lambda x: not x,
)
procedure_class_add = ProcedureFuncClassBasic(
    signature='add',
    docstring='add operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x + y,
)
procedure_class_subtract = ProcedureFuncClassBasic(
    signature='sub',
    docstring='subtract operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x - y,
)
procedure_class_multiply = ProcedureFuncClassBasic(
    signature='mul',
    docstring='multiply operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x * y,
)
procedure_class_divide = ProcedureFuncClassBasic(
    signature='div',
    docstring='divide operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x / y,
)
procedure_class_modulo = ProcedureFuncClassBasic(
    signature='mod',
    docstring='modulo operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x % y,
)
procedure_class_mod_divide = ProcedureFuncClassBasic(
    signature='modDiv',
    docstring='modulo divide operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x // y,
)
procedure_class_square = ProcedureFuncClassBasic(
    signature='sq',
    docstring='square operator',
    procedure_func_type=ProcedureFuncUnaryOperator,
    native_function=lambda x: x * x,
)
procedure_class_power = ProcedureFuncClassBasic(
    signature='pow',
    docstring='power operator',
    procedure_func_type=ProcedureFuncBinaryOperator,
    native_function=lambda x, y: x ** y,
)

# comparision procedure classes ---------------------------
procedure_class_equal = ProcedureFuncClassBasic(
    signature='eq',
    docstring='equal',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x == y,
)
procedure_class_not_equal = ProcedureFuncClassBasic(
    signature='ne',
    docstring='not equal',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x != y,
)
procedure_class_less_than = ProcedureFuncClassBasic(
    signature='lt',
    docstring='less than',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x < y,
)
procedure_class_less_than_or_equal = ProcedureFuncClassBasic(
    signature='lte',
    docstring='less than or equal',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x <= y,
)
procedure_class_greater_than = ProcedureFuncClassBasic(
    signature='gt',
    docstring='greater than',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x > y,
)
procedure_class_greater_than_or_equal = ProcedureFuncClassBasic(
    signature='gte',
    docstring='greater than or equal',
    procedure_func_type=ProcedureFuncComparator,
    native_function=lambda x, y: x >= y,
)

# probe class --------------------------------------------
procedure_class_probe = ProcedureFuncClassBasic(
    signature='probe',
    docstring='probe',
    procedure_func_type=ProcedureFuncProbe,
)

# data class cast -----------------------------------------
procedure_class_cast_2_bool = ProcedureFuncClassBasic(
    signature='castToBool',
    docstring='cast to bool',
    procedure_func_type=ProcedureFuncCast,
    native_function=lambda x: bool(x),
)
procedure_class_cast_2_int = ProcedureFuncClassBasic(
    signature='castToInt',
    docstring='cast to int',
    procedure_func_type=ProcedureFuncCast,
    native_function=lambda x: int(x),
)
procedure_class_cast_2_float = ProcedureFuncClassBasic(
    signature='castToFloat',
    docstring='cast to float',
    procedure_func_type=ProcedureFuncCast,
    native_function=lambda x: float(x),
)

# data flow control ---------------------------------------
procedure_class_diverge = ProcedureFuncClassBasic(
    signature='diverge2',
    docstring='diverge 1 branch to 2',
    procedure_func_type=ProcedureFuncDiverge2,
)
procedure_class_converge = ProcedureFuncClassBasic(
    signature='converge2',
    docstring='converge 2 branches to 1',
    procedure_func_type=ProcedureFuncConverge2,
)


# implement procedure class factory -----------------------
class ProcedureFuncFactory(IProcedureFunc):
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
