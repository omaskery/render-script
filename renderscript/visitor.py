import inspect


class Visitor:

    def __init__(self, throw_on_unknown=False):
        self._accept_method_lookup = {}
        self._throw_on_unknown = throw_on_unknown

    def auto_detect_accept_methods(self):
        for _, method in inspect.getmembers(self, inspect.ismethod):
            parameter = self._get_single_annotated_parameter(method)
            if parameter:
                self.register_accept_method(method)

    def register_accept_method(self, method):
        parameter = self._get_single_annotated_parameter(method)
        if parameter is None:
            raise Exception("expected one parameter")
        parameter_type = parameter.annotation
        self._accept_method_lookup[parameter_type] = method

    def accept(self, visitable):
        visitable_type = type(visitable)
        method = self._accept_method_lookup.get(visitable_type)
        if method:
            return method(visitable)
        elif not self._throw_on_unknown:
            return self.accept_other(visitable)
        else:
            raise Exception(f"no accept function to handle visitor of type {visitable_type.__name__}")

    def accept_other(self, visitable):
        pass

    @staticmethod
    def _extract_non_self_parameters(method):
        signature = inspect.signature(method)
        return [p for p in signature.parameters.values() if p.name != "self"]

    @classmethod
    def _get_single_annotated_parameter(cls, method):
        parameters = cls._extract_non_self_parameters(method)
        if len(parameters) != 1:
            return None
        parameter = parameters[0]
        if parameter.annotation is inspect.Parameter.empty:
            return None
        return parameter

