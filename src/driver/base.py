from abc import ABC, abstractmethod
from typing import Tuple


class InstrumentDriver(ABC):
    def __init__(self, VSA, VSG):
        self.VSA = VSA
        self.VSG = VSG

# Common methods
    @abstractmethod
    def set_frequency(self, freq: float) -> None:
        raise NotImplementedError

# VSA methods
    @abstractmethod
    def vsa_configure(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def vsa_get_ACLR(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def vsa_get_attn_ref(self) -> Tuple[str, float]:
        raise NotImplementedError

    @abstractmethod
    def vsa_get_evm(self) -> Tuple[float, float]:
        raise NotImplementedError

    @abstractmethod
    def vsa_get_ch_power(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def vsa_get_waveform_info(self) -> str:
        raise NotImplementedError

    def vsa_get_extra(self) -> str:
        return "none"

    @abstractmethod
    def vsa_set_level(self, mode: str) -> float:
        raise NotImplementedError

# VSG methods
    @abstractmethod
    def vsg_configure(self) -> None:
        raise NotImplementedError

    def vsg_get_extra(self) -> str:
        return "none"

    @abstractmethod
    def vsg_set_power(self, pwr: float) -> None:
        raise NotImplementedError
