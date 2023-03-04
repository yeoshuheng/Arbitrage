import numpy as np
import pandas as pd
import typing
from collections import defaultdict

class NoArbitrageError(Exception):
  def __str__(self):
    return "No Arbitrage Opportunity Present."

class betEngine():
   def __init__(self, df: pd.DataFrame, bankroll: float, type: str = "unbiased") -> None:
        """
        Constructor for bet engine.
         @param df : Transformed dataframe.
         @param bankroll : TODO
         @param type : Bet type, currently, only biased betting is available.
        """
        self.df = df
        self.bankroll = bankroll
        self.type = type
        # TODO: Create a residual betting strategy? Biased allocation.
        self.techniques = {
           "unbiased" : lambda x: self.unbiasedArb(x),
           "biased" : None
        }
   
   def canBeArbitrage(self, dfWin : pd.DataFrame, dfLoss : pd.DataFrame, IV : float) -> bool:
      """
      Checks for arbitrage opportunity.
         @param dfWin : row of dataframe consisting of highest win odds.
         @param dfLoss : row of dataframe consisting of highest loss odds.
         @param IV : implied volatility of the odds.
         @return Whether this is a arbitrage opportunity.
      """
      return (dfWin["book_name"] != dfLoss["book_name"]) and IV < 1 
   
   def arbBet(self, date: str) -> dict:
      """
      Checks for arbitage opportunities at a given date.
         @param date : date to check.
         @return Dictionary of arbitrage opportunities at this date.
      """
      df = self.df.copy()
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

            impliedVolatility = (1 / winOdds) + (1 / lossOdds) #+ (1 / drawOdds)
               
            # We require implied volatility less than 1 for successful arbitrage.
            if not self.canBeArbitrage(dfHighestWin, dfHighestLoss, impliedVolatility):
               continue

            odds = [winOdds, lossOdds]
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
      """
      Generating allocation for unbiased arbitrage strategies.
         @param : List of maximal odds.
         @return Allocation for win and loss based on odds.
      """
      stake = 100
      winOdds = odds[0]
      #drawOdds = odds[1]
      lossOdds = odds[1]
      totalOdds = winOdds + lossOdds

      def getAllocation(odd: float) -> float:
         return round((stake / 2) * (odd / totalOdds), 2)
        
      return {
           "win" : getAllocation(winOdds),
           "loss" : getAllocation(lossOdds),
           #"draw" : getAllocation(drawOdds)
      }
    
   def run(self, date: str) -> dict:
      """
      Generator for arbitrage opportunity on a single day.
         @param date : date to look for arbitrage.
         @return Dictionary of all arbitrage opportunities.
      """
      return self.arbBet(date)
   
   def run(self, startDate: str, endDate: str) -> dict:
      """
      Generator for arbitrage opportunities over a time horizon.
      Mainly for backtesting purposes.
         @param startDate : date to start looking for arbitrage.
         @param endDate : end of time horizon.
         @return Dictionary of all arbitrage opportunities.
      """
      df = self.df.copy()
      df = df[(df["game_date"] >= startDate) & (df["game_date"] <= endDate)]
      retDict = {}
      for date in set(df["game_date"]):
         try:
            retDict[date] = self.arbBet(date)
         except NoArbitrageError:
            continue
      return retDict
      
       
           
           
           


        



       
       
       
       

       



        


       

       

    


        
        




    