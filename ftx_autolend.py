import logging
import sys
import api_data
import requests
import asyncio, signal, functools
import time
import hmac
import hashlib
from ftxclient import FtxClient


richlog = True
try:
	from rich.logging import RichHandler
except:
	richlog = False




if 'win32' in sys.platform:
	# Windows specific event-loop policy & cmd
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


SLEEP_INTERVAL = 5*60 # this sets the interval to check for new open positions (every n seconds)

#===============================================================================
# env args
#===============================================================================
ENVARGS = []
if len(sys.argv) >= 1:
	for n in range(1,len(sys.argv)):
		ENVARGS.append(sys.argv[n].upper())
#===============================================================================
# env args end
#===============================================================================

#===============================================================================
# logger setup
#===============================================================================
logger = logging.getLogger("ftx")
logger.setLevel(level=logging.INFO)

if richlog == True:
	rlog = RichHandler()
	logger.addHandler(rlog)
else:
	handler = logging.StreamHandler()
	logger.addHandler(handler)
#===============================================================================
# logger setup end 
#===============================================================================


API_KEY = api_data.ftx["apiKey"]
API_SECRET = api_data.ftx["secret"]

api = FtxClient(api_key=API_KEY,api_secret=API_SECRET)


if len(ENVARGS) == 0:
	logger.error("please inform the coins symbols on the arguments\ni.e python ftx_autolend.py BTC LTC ETH")
	quit()




async def autolending():
	while True:
		try:

			balance =api.get_balances()
			availablecoins = {}
			foundcoins = []
			for s in balance:
				if s["coin"] in ENVARGS:
					foundcoins.append(s["coin"])
					logger.info("%s %s total, %s available for borrow" % (s["coin"],s["total"],s["availableWithoutBorrow"]))
					if s["availableWithoutBorrow"] <= 0:
						logger.info("%s maximum amount already in lending" % s["coin"])
					else:
						availablecoins[s["coin"]] = s["total"]

						logger.info("Checking lending rates for %s" % availablecoins)
						lending = api.get_spot_margin_lending_rates()

						lendingrates = {}
						for s in lending:
							if s["coin"] in availablecoins:
								logger.info("%s lending rate: %s" % (s["coin"],s["previous"]))
								lendingrates[s["coin"]] = s["previous"]


						for c in lendingrates.keys():
							# print(c,availablecoins[c],lendingrates[c] )
							x = api.submit_lending_offer(c,availablecoins[c],lendingrates[c]/10)
							logger.info("New %s lending submmited" % c)
			for c in ENVARGS:
				if c not in foundcoins:
					logger.info("there's no %s in your wallet" % c)



		except:
			e = sys.exc_info()
			logger.error("EXCEPTION ERROR - line %s, %s %s" % (e[-1].tb_lineno, type(e).__name__, e))
		finally:
			delay = await asyncio.sleep(SLEEP_INTERVAL)



#===============================================================================
# loop signal handler to exit with ctrl+c
#===============================================================================
def ask_exit(signame):
	logger.info("Got signal %s: exiting" % signame)
	loop.stop()
	try:
		request_client.cancel_order(main_symbol,origClientOrderId="buylimit")
	except:
		pass

loop = asyncio.get_event_loop()
for signame in ('SIGINT', 'SIGTERM'):
	try:
		loop.add_signal_handler(getattr(signal, signame),functools.partial(ask_exit, signame))
	except NotImplementedError:
		pass  # Ignore if not implemented. Means this program is running in windows.


#===============================================================================
# end of loop signal handler
#===============================================================================

def auto_lending():
	asyncio.ensure_future(autolending())  
	logger.info("Event loop running forever, press Ctrl+C to interrupt.")

	try:
		loop.run_forever()
	finally:
		loop.close()

if __name__ == '__main__':
	auto_lending()



