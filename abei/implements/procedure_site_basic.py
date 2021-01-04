from base64 import urlsafe_b64encode
from uuid import uuid1

from abei.interfaces import (
    IProcedure,
    IProcedureDataClass,
    IProcedureSite,
    IProcedureSiteFactory,
    IProcedureDataFactory,
    IProcedureFactory,
    service_entry as _
)
from abei.implements.util import LazyProperty


class ProcedureDataClassWrapper(IProcedureDataClass):

    def __init__(self, data, site):
        self.data = data
        self.site = site

    def get_signature(self):
        sig = self.data.get_signature()
        assert '@' not in sig
        return '{}@{}'.format(sig, self.site)

    def get_label(self):
        return self.data.get_label()

    def instantiate(self, *args, **kwargs):
        return self.data.instantiate(*args, data_class=self, **kwargs)


class ProcedureSiteBuiltin(IProcedureSite):
    def __init__(self):
        self.data = {}
        self.procedures = {}

    def load_data_class(self, builtin_data, factory):
        sign = self.get_signature()
        self.data.clear()
        for d_class in builtin_data:
            d = factory.get_class(d_class)
            self.data[d.get_signature()] = ProcedureDataClassWrapper(d, sign)

    def load(self, builtin_config, factory):
        bool_class = self.get_data_class('bool')
        self.procedures.clear()
        for d_class, p_class in builtin_config:
            p = factory.create(
                p_class,
                data_class=self.get_data_class(d_class),
                bool_class=bool_class,
            )
            self.procedures[p.get_signature()] = p

    def get_signature(self):
        return 'builtin'

    def get_procedure(self, signature, **kwargs):
        procedure = self.query_procedure(signature, **kwargs)
        if not procedure:
            raise LookupError(
                'procedure {} not found'.format(signature))
        return procedure

    def query_procedure(self, signature, site=None, **kwargs):
        site = site and str(site)
        signature = str(signature)
        return (
            (site is None or self.get_signature() == site) and
            self.procedures.get(signature) or None
        )

    def register_procedure(self, procedure, **kwargs):
        return None

    def iterate_procedures(self):
        return self.procedures.keys()

    def get_data_class(self, signature, **kwargs):
        parameter = self.query_data_class(signature, **kwargs)
        if not parameter:
            raise LookupError(
                'data {} not found'.format(signature))
        return parameter

    def query_data_class(self, signature, site=None, **kwargs):
        site = site and str(site)
        signature = str(signature)
        return (
            (site is None or self.get_signature() == site) and
            self.data.get(signature) or None
        )

    def register_data_class(self, parameter, **kwargs):
        return None

    def iterate_data_classes(self):
        return self.data.keys()

    def get_base_sites(self):
        return []


class ProcedureSiteBasic(IProcedureSite):

    def __init__(self, signature=None, dependencies=None):
        # signature will be set to random string if not specified
        self.signature = signature or urlsafe_b64encode(
            uuid1().bytes).strip(b'=').decode()
        self.dependencies = dependencies or []
        self.procedures = {}
        self.data = {}

    def get_signature(self):
        return self.signature

    def get_procedure(self, signature, **kwargs):
        procedure = self.query_procedure(signature, **kwargs)
        if not procedure:
            raise LookupError(
                'procedure {} not found'.format(signature))
        return procedure

    def query_procedure(self, signature, depth=-1, site=None, **kwargs):
        site = site and str(site)
        signature = str(signature)

        procedure = (
            (site is None or self.get_signature() == site) and
            self.procedures.get(signature) or None
        )
        if procedure:
            return procedure

        if depth == 0:
            return None

        # try to find in dependent sites
        for s in self.dependencies:
            procedure = s.query_procedure(
                signature, depth=depth - 1, site=site, **kwargs)
            if procedure:
                return procedure

        return None

    def register_procedure(self, procedure, **kwargs):
        assert isinstance(procedure, IProcedure)
        signature = str(procedure.get_signature())
        if (
                not kwargs.get('overwrite') and
                self.query_procedure(signature)
        ):
            raise AssertionError('procedure already registered')

        self.procedures[signature] = procedure
        return procedure

    def iterate_procedures(self):
        return self.procedures.keys()

    def get_data_class(self, signature, **kwargs):
        data = self.query_data_class(signature, **kwargs)
        if not data:
            raise LookupError('data {} not found'.format(signature))
        return data

    def query_data_class(self, signature, depth=-1, site=None, **kwargs):
        site = site and str(site)
        signature = str(signature)

        data = (
            (site is None or self.get_signature() == site) and
            self.data.get(signature) or None
        )
        if data:
            return data

        if depth == 0:
            return None

        # try to find in dependent sites
        for s in self.dependencies:
            data = s.query_data_class(
                signature, depth=depth - 1, site=site, **kwargs)
            if data:
                return data

        return None

    def register_data_class(self, data, **kwargs):
        assert isinstance(data, IProcedureDataClass)
        signature = str(data.get_signature())
        if (
                not kwargs.get('overwrite') and
                self.query_data_class(signature)
        ):
            raise AssertionError('data already registered')

        data = ProcedureDataClassWrapper(data, self.get_signature())
        self.data[signature] = data
        return data

    def iterate_data_classes(self):
        return self.data.keys()

    def get_base_sites(self):
        return list(self.dependencies)


class ProcedureSiteFactory(IProcedureSiteFactory):

    def __init__(self, service_site, **kwargs):
        self.service_site = service_site

    @LazyProperty
    def builtin_config(self):
        return [
            ('bool', 'not'),
            ('bool', 'and'),
            ('bool', 'or'),

            ('int', 'neg'),
            ('int', 'add'),
            ('int', 'sub'),
            ('int', 'mul'),
            ('int', 'mod'),
            ('int', 'modDiv'),
            ('int', 'sq'),
            ('int', 'eq'),
            ('int', 'ne'),
            ('int', 'lt'),
            ('int', 'lte'),
            ('int', 'gt'),
            ('int', 'gte'),
            ('int', 'probe'),
            ('int', 'diverge2'),
            ('int', 'converge2'),

            ('float', 'neg'),
            ('float', 'add'),
            ('float', 'sub'),
            ('float', 'mul'),
            ('float', 'div'),
            ('float', 'mod'),
            ('float', 'modDiv'),
            ('float', 'sq'),
            ('float', 'eq'),
            ('float', 'ne'),
            ('float', 'lt'),
            ('float', 'lte'),
            ('float', 'gt'),
            ('float', 'gte'),
            ('float', 'probe'),
            ('float', 'diverge2'),
            ('float', 'converge2'),

            ('string', 'eq'),
            ('string', 'ne'),
            ('string', 'probe'),
            ('string', 'diverge2'),
            ('string', 'converge2'),
        ]

    @LazyProperty
    def builtin(self):
        instance = ProcedureSiteBuiltin()
        instance.load_data_class([
            'bool',
            'int',
            'float',
            'string',
        ], self.service_site.get_service(_(IProcedureDataFactory)))
        instance.load(
            self.builtin_config,
            self.service_site.get_service(_(IProcedureFactory))
        )
        return instance

    def create(self, procedure_sites, signature=None, **kwargs):
        if not procedure_sites and not signature:
            return self.builtin

        return ProcedureSiteBasic(
            signature=signature,
            dependencies=procedure_sites or [self.builtin],
        )
