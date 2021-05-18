# ftx_autolend
This python script will automatically compound lend your crypto, taking the lending profits and re-lending it for you on the FTX exchange

# ftx_compoundstake
This python script will automatically compound stake your staking profits, taking the staking profits and submitting a stake offer on the FTX exchange

# Demo video
https://youtu.be/9KmnBRN7SFk
=======


# Install intructions:

requires Python 3+ and the following additional modules:

requests<br/>
rich (not essential, just some fancy console coloring)<br/>

If you are starting with a fresh python v3.X install, make sure to run "pip install requests" and "pip install rich"  to get your python environment set up to run everything that this script asks for. If your default python install is another version (2.7), you might need to use a virtual environment like Conda (https://docs.conda.io/en/latest/miniconda.html)

rename api_data_template.py to api_data.py and add you ftx API key/secret inside the file.

# Running the script:
python ftx_autolend.py BTC MOB USD USDT<br/>
python ftx_compoundstake RAY SRM MSRM MSRM_LOCKED


As you can see, just type the symbols of coins that you want to lend after "python ftx_autolend.py" or "python ftx_compoundstake" and it will check your wallet and assign all the available balance to the lending/staking

# Tips and tricks

If you use Subaccounts edit line 59 and add your subaccount name on the script:
api = FtxClient(api_key=API_KEY,api_secret=API_SECRET),subaccount_name="YOUR_SUBACCOUNT_NAME")

If you get Exceptions with "Size too large" errors, cancel the lending on the web interface and let the script do it itself, do not submit manually from the web interface before running the script to avoid this error. (still investigating it)

# DONATIONS

If you like this and made a lot of extra lending/staking money, feel free to contribute to my beer fund<br/>
btc: 1DN6jvGZbQkYT9RoCjCVzTs5MwC3xvdmMh<br/>
ltc: LTT8Gj8nnwBCEGAcapjfLy9EyZtiu6Ntqh<br/>
mob: 64exapUSWRjWTGKqppQpd9PxDQvH277cS7uhPyEqTZaCSHLiqWNrXMTnpiUJTGY4qv9aQ2ZWA7cyJnn2YZHaJWMN33bGcS75JcPSR51Eqw8<br/>
usdt TRC20: TYXR6fkC3dKwfSFtEdkgcPVr2em3cPUnT9<br/>
# Help? Bugs?
https://molibden.io/about/
