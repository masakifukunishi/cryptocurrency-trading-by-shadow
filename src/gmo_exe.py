import sys
import logging

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)

from app.controllers.gmo.trade import Trade

if __name__ == "__main__":
    trade = Trade()
    trade.trade()