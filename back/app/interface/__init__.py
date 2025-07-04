from abc import ABC, abstractmethod


class IContextManager(ABC):
    """上下文管理器接口"""
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass
