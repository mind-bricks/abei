from base64 import urlsafe_b64encode
from typing import (
    Dict,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid1

from abei.interfaces import (
    IProcedureFunc,
    IProcedureLink,
    # IProcedureLinkSite,
)


class ProcedureLinkBasic(IProcedureLink):
    """
    basic procedure link
    """

    def __init__(
            self,
            signature: Union[str, None],
            inner_procedure_func: IProcedureFunc,
            outer_procedure_func: IProcedureFunc,
    ):
        # generate a random signature for this link
        self.signature: str = signature or urlsafe_b64encode(
            uuid1().bytes).strip(b'=').decode('utf8')

        # inner_procedure_func may be equal to outer_procedure_func
        # only when this link is connect to output of procedure func
        self.inner_procedure: IProcedureFunc = inner_procedure_func
        self.outer_procedure: IProcedureFunc = outer_procedure_func

        self.links: Dict[int, Tuple[int, Optional[IProcedureLink]]] = {}

    def get_signature(self) -> str:
        return self.signature

    def get_ref_func(self) -> IProcedureFunc:
        return self.inner_procedure

    def get_imp_func(self) -> IProcedureFunc:
        return self.outer_procedure

    def get_links(self) -> Dict[int, Tuple[int, Optional[IProcedureLink]]]:
        return self.links

    def link(
            self,
            input_index: int,
            link_output_index: int,
            link: Optional[IProcedureLink],
    ) -> bool:
        if input_index in self.links:
            return False

        self.links[input_index] = (link_output_index, link)
        return True

    def unlink(
            self,
            input_index: int
    ) -> bool:
        if input_index in self.links:
            return False

        del self.links[input_index]
        return True
