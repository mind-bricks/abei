from ..service import (
    abstractmethod,
    IService,
)


class IProcedure(IService):

    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure
        :return:
        """

    @abstractmethod
    def get_input_signatures(self):
        """
        get list of input signatures
        :return:
        """

    @abstractmethod
    def get_output_signatures(self):
        """
        get list of output signatures
        :return:
        """

    @abstractmethod
    def get_docstring(self):
        """
        get document string of procedure
        :return:
        """

    @abstractmethod
    def set_docstring(self, docstring):
        """
        set document string of procedure
        :param docstring:
        :return:
        """

    @abstractmethod
    def run(self, procedure_data_list, **kwargs):
        """
        :param procedure_data_list: input code data list
        :param kwargs: extra arguments
        :return output code data list:
        """


class IProcedureClass(IService):
    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure class
        :return:
        """

    @abstractmethod
    def get_docstring(self):
        """
        get document string of procedure
        :return:
        """

    @abstractmethod
    def instantiate(self, *args, **kwargs):
        """
        instantiate procedure object
        """


class IProcedureFactory(IService):
    @abstractmethod
    def create(self, class_signature, *args, **kwargs):
        """
        create procedure directly
        :param class_signature:
        :param args:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def get_class(self, class_signature):
        """
        :param class_signature:
        :return:
        """

    @abstractmethod
    def query_class(self, class_signature):
        """
        :param class_signature:
        :return:
        """

    @abstractmethod
    def register_class(self, class_signature, procedure_class, **kwargs):
        """
        register procedure class
        :param class_signature:
        :param procedure_class:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def iterate_classes(self):
        """
        iterate procedure classes
        :return:
        """
