import numpy as np
import pandas as pd
import typing

class dataPipeline:

    def __init__(self, df: pd.DataFrame):
        """
        Constructor for data pipeline.
            @param df : Dataframe to be transformed.
        """
        self.df = df
        self.processed_df = None
        
    def getProcessedData(self) -> pd.DataFrame:
        """
        Getter for processed data.
            @return Processed data.
        """
        return self.processed_df
    
    def oddsGenerator(self, df_: pd.DataFrame, colName: str) -> pd.DataFrame:
      """
      Generates odds based on money line data.
        @param df_ : Dataframe to create odds from.
        @param colName : Column name to create odds from.
        @return Dataframe with generated odds.
      """
      df = df_.copy()
      df = df[df[colName + "1"].notna() & df[colName + "2"].notna()]
      f = lambda x: 1 + x / 100 if x >= 0 else 1 - 100 / x
      df["winOdds_" + colName] = df[colName + "1"].apply(f)   
      df["lossOdds_" + colName] = df[colName + "2"].apply(f)
      return df
    
    def dataProcessing(self):
      """
      Gets needed column and performs transformation needed.
      """
      df = self.df.copy()
      df = df[["book_name", "game_id", "matchup", "game_date", 
                "ml_price1", "ml_price2", "sp_price1", "sp_price2", "ou_price1", "ou_price2"]]
      for name in ["ml_price", "sp_price", "ou_price"]:
         df = self.oddsGenerator(df, name)
      self.processed_df = df
      return self
    
    def run(self) -> pd.DataFrame:
        """
        Runs the entire pipeline.
            @return Transformed data.
        """
        return self.dataProcessing().getProcessedData()