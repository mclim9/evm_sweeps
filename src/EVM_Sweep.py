from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import datetime
import timeit
import logging


@dataclass
class SweepConfig:
    freq_arry: list[float]
    pwr_arry: list[int]
    lvl_arry: list[str]
    output_dir: Path = Path("results")
    file_prefix: str = "evm_sweep"

    def output_path(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{self.file_prefix}_{timestamp}.txt"


class SweepResultWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.path, "a", encoding="utf-8")

    def write_line(self, line: str) -> None:
        self.file.write(line + "\n")
        logging.info(line)

    def close(self) -> None:
        self.file.close()


class SweepRunner:
    def __init__(self, vsa, vsg, config: SweepConfig, writer: SweepResultWriter | None = None):
        self.vsa = vsa
        self.vsg = vsg
        self.config = config
        self.writer = SweepResultWriter(config.output_path())

    def run(self) -> None:
        self.vsa.vsa_configure()
        self.vsg.vsg_configure()

        self.writer.write_line(f"VSA: {self.vsa.VSA.idn}")
        self.writer.write_line(f"VSG: {self.vsg.VSG.idn}")
        self.writer.write_line(self.vsa.vsa_get_waveform_info())
        self.writer.write_line(
            "Date,Time,Freq,Power[dBm],RefLvl[dBm],Attn[dB],ChPwr[dBm],EVM[dB],Leveling,AL-Time,EVMT,TotalTime,VSA_extra,VSG_extra"
        )

        total_steps = len(self.config.freq_arry) * len(self.config.pwr_arry) * len(self.config.lvl_arry)
        start_time = timeit.default_timer()
        step = 0

        for mode in self.config.lvl_arry:
            for freq in self.config.freq_arry:
                self.vsa.vsa_set_frequency(freq)
                self.vsg.vsg_set_frequency(freq)
                for power in self.config.pwr_arry:
                    step += 1

                    self.vsg.vsg_set_power(power)
                    level_time = self.vsa.vsa_set_level(mode)
                    vsa_extra = self.vsa.vsa_get_extra()
                    vsg_extra = self.vsg.vsg_get_extra()
                    evm, evm_time = self.vsa.vsa_get_evm()
                    attn, ref_lvl = self.vsa.vsa_get_attn_ref()
                    ch_pwr = self.vsa.vsa_get_ch_power()

                    timestamp = datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")
                    total_time = level_time + evm_time
                    row = (
                        f"{timestamp},{freq},{power},{ref_lvl:.2f},{attn},{ch_pwr:.2f},"
                        f"{evm:.2f},{mode},{level_time:.3f},{evm_time:.3f},{total_time:.3f},"
                        f"{vsa_extra},{vsg_extra}"
                    )
                    self.writer.write_line(row)

                    elapsed = timeit.default_timer() - start_time
                    remaining = elapsed / step * (total_steps - step)
                    logging.info(
                        f"{step}/{total_steps} done, estimated {remaining / 60:.2f} min left"
                    )

        self.writer.close()
