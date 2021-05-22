import os
import random
import unittest

from abei.interfaces import (
    IProcedureBuilder,
    IProcedure,
    IProcedureFuncFactory,
    IProcedureDataFactory,
    IProcedureJoint,
    IProcedureJointFactory,
    IProcedureFuncSite,
    IProcedureSiteFactory,
    service_entry as _
)
from abei.implements.procedure_basic import (
    ProcedureClassBasic,
    ProcedureUnaryOperator,
)
from abei.implements.procedure_data_basic import (
    ProcedureDataClassBasic,
)

from .basic import TestCaseBasic

data_class_test = ProcedureDataClassBasic(
    signature='test',
    label='test',
    value_type=type(None),
    value_default=None,
)

class_test = ProcedureClassBasic(
    signature='test',
    docstring='test',
    procedure_type=ProcedureUnaryOperator,
    native_function=lambda x: x,
)


class TestProcedure(TestCaseBasic):
    service_config_files = [
        'test-components-basic.yml',
    ]

    def test_procedure_factory(self):
        service = self.service_site.get_service(_(IProcedureFuncFactory))
        procedure_classes = list(service.iterate_classes())
        procedure_class_count = len(procedure_classes)
        self.assertNotEqual(procedure_class_count, 0)

        service.register_class(class_test.get_signature(), class_test)
        procedure_classes = list(service.iterate_classes())
        self.assertEqual(len(procedure_classes), procedure_class_count + 1)

        instance = service.create(
            class_test.get_signature(), data_class=data_class_test)
        self.assertIsNotNone(instance)

    def test_procedure_data_factory(self):
        service = self.service_site.get_service(_(IProcedureDataFactory))
        data_classes = list(service.iterate_classes())
        data_class_count = len(data_classes)
        self.assertNotEqual(data_class_count, 0)

        service.register_class(
            data_class_test.get_signature(), data_class_test)
        data_classes = list(service.iterate_classes())
        self.assertEqual(len(data_classes), data_class_count + 1)

        instance = service.create(data_class_test.get_signature())
        self.assertIs(instance.get_class(), data_class_test)

    def test_procedure_joint_factory(self):
        factory_p = self.service_site.get_service(_(IProcedureFuncFactory))
        factory_d = self.service_site.get_service(_(IProcedureDataFactory))
        outer_procedure = factory_p.create('composite')
        inner_procedure = factory_p.create(
            'add', data_class=factory_d.get_class('int'))
        self.assertIsInstance(outer_procedure, IProcedure)
        self.assertIsInstance(inner_procedure, IProcedure)
        joint_factory = \
            self.service_site.get_service(_(IProcedureJointFactory))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(inner_procedure, inner_procedure))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(outer_procedure, outer_procedure))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(outer_procedure, inner_procedure))
        procedure_joint = \
            joint_factory.create(inner_procedure, outer_procedure)
        self.assertIsInstance(procedure_joint, IProcedureJoint)

    def test_procedure_site_factory(self):
        service = self.service_site.get_service(_(IProcedureSiteFactory))
        instance = service.create(None, signature='test')
        procedures = instance.iterate_procedures()
        procedure_1 = instance.query_procedure('add[int]')
        procedure_2 = instance.query_procedure('add[int]', depth=0)
        procedure_3 = instance.query_procedure('add[int]', site='builtin')
        procedure_4 = instance.query_procedure('add[int]', site='test')
        self.assertEqual(len(procedures), 0)
        self.assertIsNotNone(procedure_1)
        self.assertIsNone(procedure_2)
        self.assertIsNotNone(procedure_3)
        self.assertIsNone(procedure_4)

        base_sites = instance.get_base_sites()
        self.assertIsInstance(instance, IProcedureFuncSite)
        self.assertEqual(len(base_sites), 1)

        instance = base_sites[0]
        procedures = instance.iterate_procedures()
        procedure_5 = instance.query_procedure('add[int]', depth=0)
        procedure_6 = instance.query_procedure('add[int]', site='test')
        self.assertNotEqual(len(procedures), 0)
        self.assertIs(procedure_1, procedure_5)
        self.assertIsNone(procedure_6)

    def test_procedure_builder(self):
        site_factory = self.service_site.get_service(_(IProcedureSiteFactory))
        site = site_factory.create(None)
        builder = self.service_site.get_service(_(IProcedureBuilder))
        self.assertRaises(
            AssertionError,
            lambda: builder.load_yaml(
                site,
                os.path.join(
                    self.service_config_dir,
                    'test-procedures-corrupted-1.yml'),
            ))


class TestProcedureRunBasic(TestCaseBasic):
    service_config_files = []
    procedure_config_files = []
    procedure_site = None
    procedure_data_factory = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.procedure_data_factory = cls.service_site.get_service(
            _(IProcedureDataFactory))

        cls.procedure_site = cls.service_site.get_service(
            _(IProcedureSiteFactory)).create(None, signature='test')

        builder = cls.service_site.get_service(_(IProcedureBuilder))
        for config_file in cls.procedure_config_files:
            builder.load_yaml(
                cls.procedure_site,
                os.path.join(cls.service_config_dir, config_file),
            )


class TestProcedureRunSimple(TestProcedureRunBasic):
    service_config_files = [
        'test-components-basic.yml',
    ]
    procedure_config_files = [
        'test-procedures-1.yml',
    ]

    def test_run_1(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.1')
        self.assertIsNotNone(procedure)
        self.assertEqual(
            procedure.get_docstring(),
            'this is test procedure 1.1'
        )
        input_1 = self.procedure_site.get_data_class('int').instantiate()
        input_2 = self.procedure_site.get_data_class('int').instantiate()
        input_1.set_value(1)
        input_2.set_value(2)
        outputs = procedure.run([input_1, input_2])
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(outputs))
        self.assertEqual(outputs[0].get_value(), 3)
        self.assertEqual(outputs[1].get_value(), -1)

    def test_run_2(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.2')
        self.assertIsNotNone(procedure)
        self.assertEqual(
            procedure.get_docstring(),
            'this is test procedure 1.2'
        )
        input_1 = self.procedure_site.get_data_class('int').instantiate()
        input_2 = self.procedure_site.get_data_class('int').instantiate()
        input_1.set_value(1)
        input_2.set_value(2)
        self.assertRaises(
            AssertionError,
            lambda: procedure.run([input_1, input_2])
        )

        input_1 = self.procedure_site.get_data_class('float').instantiate()
        input_2 = self.procedure_site.get_data_class('float').instantiate()
        input_1.set_value(2.0)
        input_2.set_value(3.0)
        outputs = procedure.run([input_1, input_2])
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(outputs))
        self.assertEqual(outputs[0].get_value(), 30)
        self.assertEqual(outputs[1].get_value(), 11)

    def test_run_3(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.3')
        self.assertIsNotNone(procedure)
        self.assertEqual(procedure.get_docstring(), '(x + y) * z')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)
        z = random.random() * random.randint(1, 10)
        input_1 = self.procedure_site.get_data_class('float').instantiate(x)
        input_2 = self.procedure_site.get_data_class('float').instantiate(y)
        input_3 = self.procedure_site.get_data_class('float').instantiate(z)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), (x + y) * z)

    def test_run_4(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.4')
        self.assertIsNotNone(procedure)
        self.assertEqual(procedure.get_docstring(), 'x + y * z')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)
        z = random.random() * random.randint(1, 10)
        input_1 = self.procedure_site.get_data_class('float').instantiate(x)
        input_2 = self.procedure_site.get_data_class('float').instantiate(y)
        input_3 = self.procedure_site.get_data_class('float').instantiate(z)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x + y * z)

    def test_run_5(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.5')
        self.assertIsNotNone(procedure)
        self.assertEqual(procedure.get_docstring(), 'z ? x + y : x - y')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)

        input_1 = self.procedure_site.get_data_class('bool').instantiate(True)
        input_2 = self.procedure_site.get_data_class('float').instantiate(x)
        input_3 = self.procedure_site.get_data_class('float').instantiate(y)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x + y)

        input_1 = self.procedure_site.get_data_class('bool').instantiate(False)
        input_2 = self.procedure_site.get_data_class('float').instantiate(x)
        input_3 = self.procedure_site.get_data_class('float').instantiate(y)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x - y)

    def test_run_6(self):
        procedure = self.procedure_site.get_procedure('test-procedure-1.6')
        self.assertIsNotNone(procedure)
        self.assertEqual(
            procedure.get_docstring(), 'z ? x + y : x - y (optimized)')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)

        input_1 = self.procedure_site.get_data_class('bool').instantiate(True)
        input_2 = self.procedure_site.get_data_class('float').instantiate(x)
        input_3 = self.procedure_site.get_data_class('float').instantiate(y)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x + y)

        input_1 = self.procedure_site.get_data_class('bool').instantiate(False)
        input_2 = self.procedure_site.get_data_class('float').instantiate(x)
        input_3 = self.procedure_site.get_data_class('float').instantiate(y)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x - y)


class TestProcedureRunAlgorithm(TestProcedureRunBasic):
    service_config_files = [
        'test-components-basic.yml',
    ]
    procedure_config_files = [
        'test-procedures-2.yml',
    ]

    @unittest.skip('')
    def test_number_count(self):
        procedure = self.procedure_site.get_procedure('number-count')
        self.assertIsNotNone(procedure)
        input_1 = self.procedure_data_factory.create('int', 1)
        input_2 = self.procedure_data_factory.create('int', 1)
        input_3 = self.procedure_data_factory.create('int', 10)
        outputs = procedure.run([input_1, input_2, input_3])
        assert outputs
