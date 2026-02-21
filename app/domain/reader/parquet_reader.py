import pandas as pd
from app.domain.interfaces.eeg_reader_interface import EegReaderInterface

class ParquetEegReader(EegReaderInterface):

    def read(self, file_path: str) -> pd.DataFrame:
        
        df = pd.read_parquet(file_path)
        return df
