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


SLEEP_INTERVAL = 2*60 # this sets the interval to check for new lending rates estimation and available balances (every n seconds)

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


ESTIMATE_RATE_MULTIPLIER = 0.005 # reduces your rate to be slightly below of the next estimated rate 0.005 = 0.5%

async def autolending():
	while True:
		try:
			logger.info("***************************************************")
			balance =api.get_balances()
			availablecoins = {}
			foundcoins = []

			lending = api.get_spot_margin_lending_rates()
			offers = api.get_spot_margin_lending_offer()

			for s in balance:
				if s["coin"] in ENVARGS:
					foundcoins.append(s["coin"])
					logger.info("%s %s total, %s available for lending" % (s["coin"],s["total"],s["availableWithoutBorrow"]))


					if s["availableWithoutBorrow"] <= 0:
						logger.info("%s maximum amount already in lending" % s["coin"])
					else:
						availablecoins[s["coin"]] = s["total"]
			
			lendingrates = {}
			for l in lending:
				if l["coin"] in availablecoins:
					logger.info("%s lending rate: %s" % (l["coin"],f'{l["previous"]*876000:.3f}'))
					lendingrates[l["coin"]] = l["estimate"]

			coin_submitted_updated_amount = []
			for c in lendingrates.keys():
				# print(c,availablecoins[c],lendingrates[c] )
				submit = api.submit_lending_offer(c,availablecoins[c],lendingrates[c]-(lendingrates[c]*ESTIMATE_RATE_MULTIPLIER))
				logger.info("New %s lending submmited, updated amount to %s" % (c,availablecoins[c]))
				coin_submitted_updated_amount.append(c)

			for c in ENVARGS:
				if c not in foundcoins:
					logger.info("there's no %s in your wallet" % c)

			#check for actual lending rates changes
			for o in offers:
				for l in lending:
					if o["coin"] == l["coin"] and o["coin"] not in coin_submitted_updated_amount and o["coin"] in ENVARGS:
						modified_l = l["estimate"]-(l["estimate"]*ESTIMATE_RATE_MULTIPLIER)
						logger.info("%s your offer lending rate %s, predicted rate %s" % (o["coin"],f'{o["rate"]*876000:.3f}',f'{l["estimate"]*876000:.3f}'))
						if (o["rate"] > modified_l) or ((o["rate"]/l["estimate"]) < 0.98): #if rate is bigger than estimate or more then 2% away
							logger.info("%s submiting lending with new updated rate %s" % (o["coin"],f'{modified_l*876000:.3f}'))
							submit = api.submit_lending_offer(o["coin"],o["size"],modified_l)


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



