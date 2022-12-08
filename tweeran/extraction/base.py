import os
from abc import ABC, abstractmethod


class ExtractionManager(ABC):
    output_path: os.PathLike | str

    def __init__(self, output_path: os.PathLike | str) -> None:
        self.output_path = output_path

    def __del__(self) -> None:
        self.cleanup()

    @abstractmethod
    def cleanup(self) -> None:
        ...

    @abstractmethod
    def run(self) -> None:
        ...
