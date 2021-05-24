# 3c_bot_max_deals_updater
For use with the BitParty/BotParty SDCA strategy on 3Commas bots. It will automatically set the max active deals for the your BTC and USDT bots based on your capital allocation for each bot and the number of safety orders already filled.

**Use this script at your own risk.**

Before first running the script for the first time, you will need to run

    pip install py3cw

At the top of the script you need to enter, in the spaces provided, 
- 3Commas API key
- 3Commas Secret Key
- the ID for the account in which the bots are (look in the URL on 3Commas when you got to the account summary for that account)
- the exact name of the BTC SDCA bot (this is case sensitive)
- the capital allocation for the BTC bot
- the exact name of the USDT bot
- the capital allocation for the USDT bot
- the percentage reserved for safety order 7 and above (0.25 is recommended in the BotParty/Bitparty Strategy Guide

Each time this script is run it calculates the average completed safety order per deal and uses this to adjust the number of max active deals according to capital allocation and the amount kept in reserve. This means that when the market is in an upward trend so the bots are mostly just scalping and filling very few safeties, the bots will be running at 200% capacity. As more safety orders are filled then the max deals are reduced. When the average SO per deal is over 5 then they will be running at 100%. 
