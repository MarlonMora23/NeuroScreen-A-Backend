from abc import ABC, abstractmethod
import pandas as pd

class EegReaderInterface(ABC):

    @abstractmethod
    def read(self, file_path: str) -> pd.DataFrame:
        pass
