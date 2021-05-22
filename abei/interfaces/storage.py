from typing import Optional

from .service import (
    abstractmethod,
    IService,
)


class IStorage(IService):

    @abstractmethod
    def get_value(self, key: str) -> Optional[str]:
        """
        get value by key
        """

    @abstractmethod
    def set_value(self, key: str, value: str) -> bool:
        """
        set value with key
        """

    @abstractmethod
    def del_value(self, key: str) -> bool:
        """
        del value by key
        """
