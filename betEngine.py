import numpy as np
import pandas as pd
import typing
from collections import defaultdict

class NoArbitrageError(Exception):
  def __str__(self):
    return "No Arbitrage Opportunity Present."

class betEngine():
   def __init__(self, df: pd.DataFrame, bankroll: float, type: str = "unbiased") -> None:
        self.df = df
        self.bankroll = bankroll
        self.type = type
        self.techniques = {
           "unbiased" : lambda x: self.unbiasedArb(x),
           "biased" : None
        }
        self.processed_df = None

   def oddsGenerator(self, df_: pd.DataFrame, colName: str) -> pd.DataFrame:
      df = df_.copy()
      df = df[df[colName + "1"].notna() & df[colName + "2"].notna()]
      f = lambda x: 1 + x / 100 if x >= 0 else 1 - 100 / x
      df["winOdds_" + colName] = df[colName + "1"].apply(f)   
      df["lossOdds_" + colName] = df[colName + "2"].apply(f)
      return df
   
   def dataProcessing(self) -> None:
      df = self.df.copy()
      df = df[["book_name", "game_id", "matchup", "game_date", 
                "ml_price1", "ml_price2", "sp_price1", "sp_price2", "ou_price1", "ou_price2"]]
      for name in ["ml_price", "sp_price", "ou_price"]:
         df = self.oddsGenerator(df, name)
      self.processed_df = df
    
   def getProcessedData(self) -> pd.DataFrame:
       return self.processed_df

   def arbBet(self, date: str) -> dict:
        df = self.processed_df.copy()
        df = df[df['game_date'] == date]

        # Dictionary of Possible arbitrages
        returnDict = defaultdict(dict)
        arbTechnique = self.techniques[self.type]

        for id in set(df['game_id']):
            dfCurr = df.copy()
            dfCurr = df[df['game_id'] == id]

            for currBet in ["ml_price", "ou_price", "sp_price"]:
               # Get highest odds for all outcomes
               dfHighestWin = dfCurr.loc[dfCurr["winOdds_" + currBet].idxmax()]
               dfHighestLoss = dfCurr.loc[dfCurr["lossOdds_" + currBet].idxmax()]
               #dfHighestDraw =  dfCurr.loc(df["drawOdds_"].idxmax())
               winOdds = dfHighestWin["winOdds_" + currBet]
               lossOdds = dfHighestLoss["winOdds_" + currBet]
               #drawOdds = dfHighestDraw['drawOdds']

               # TODO: Should we consider only accepting a arbitrage opportunity under the following conditions:
               # 1. No 2 allocations are under the same book.
               impliedVolatility = (1 / winOdds) + (1 / lossOdds) #+ (1 / drawOdds)
               
               # We require implied volatility less than 1 for successful arbitrage.
               if impliedVolatility > 1:
                  continue

               odds = [winOdds, lossOdds]

               # Missing data to conduct arbitrage.
               if None in odds:
                  continue

               oddsDict = arbTechnique(odds)
               finalDict = {
                  "Win" : [dfHighestWin["book_name"], oddsDict["win"]],
                  "Loss" : [dfHighestLoss["book_name"], oddsDict["loss"]],
                  #"Draw" : [dfHighestDraw["book_name"], oddsDict["draw"]]
               }
               returnDict[id][currBet] = finalDict
            
        if not returnDict:
           raise NoArbitrageError
        return returnDict
    
   def unbiasedArb(self, odds: list) -> dict:
      # We assume desired winnings to be 100.
      win = 1000
      winOdds = odds[0]
      #drawOdds = odds[1]
      lossOdds = odds[1]

      def getAllocation(odd: float) -> float:
         return round((win / odd), 2)
        
      return {
           "win" : getAllocation(winOdds),
           "loss" : getAllocation(lossOdds),
           #"draw" : getAllocation(drawOdds)
      }
    
   def run(self, date: str) -> dict:
      self.dataProcessing()
      return self.arbBet(date)
   
   def run(self, startDate: str, endDate: str) -> dict:
      self.dataProcessing()
      df = self.processed_df.copy()
      df = df[(df["game_date"] >= startDate) & (df["game_date"] <= endDate)]
      retDict = {}
      for date in set(df["game_date"]):
         try:
            retDict[date] = self.arbBet(date)
         except NoArbitrageError:
            continue
      return retDict
      
       
           
           
           


        



       
       
       
       

       



        


       

       

    


        
        




    