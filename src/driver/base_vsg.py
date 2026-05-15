from abc import ABC, abstractmethod

class VSGDriver(ABC):
    def __init__(self, VSG):
        self.VSG = VSG

    @abstractmethod
    def vsg_configure(self) -> None:
        raise NotImplementedError

    def vsg_get_extra(self) -> str:
        return "none"

    @abstractmethod
    def vsg_save_state(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def vsg_set_frequency(self, freq: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def vsg_set_power(self, pwr: float) -> None:
        raise NotImplementedError
