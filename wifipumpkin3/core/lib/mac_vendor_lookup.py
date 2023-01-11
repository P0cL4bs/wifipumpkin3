import asyncio
import os
import logging
import sys
from datetime import datetime
import aiofiles

# This library provides an easy way to get vendor information from a MAC address.
# It contains a local copy of the IEEE's OUI prefix list. 
# It has an asynchronous interface using Python 3's asyncio as well as a regular 
# synchronous interface for old-school usage.
# source:  https://github.com/bauerj/mac_vendor_lookup

class InvalidMacError(Exception):
    pass


class VendorNotFoundError(KeyError):
    def __init__(self, mac):
        self.mac = mac

    def __str__(self):
        return f"The vendor for MAC {self.mac} could not be found. " \
               f"Either it's not registered or the local list is out of date. Try MacLookup().update_vendors()"


class BaseMacLookup(object):
    cache_path = os.path.expanduser('~/.cache/mac-vendors.txt')

    @staticmethod
    def sanitise(_mac):
        mac = _mac.replace(":", "").replace("-", "").replace(".", "").upper()
        try:
            int(mac, 16)
        except ValueError:
            raise InvalidMacError("{} contains unexpected character".format(_mac))
        if len(mac) > 12:
            raise InvalidMacError("{} is not a valid MAC address (too long)".format(_mac))
        return mac

    def get_last_updated(self):
        vendors_location = self.find_vendors_list()
        if vendors_location:
            return datetime.fromtimestamp(os.path.getmtime(vendors_location))

    def find_vendors_list(self):
        possible_locations = [
            BaseMacLookup.cache_path,
            sys.prefix + "/cache/mac-vendors.txt",
            os.path.dirname(__file__) + "/../../cache/mac-vendors.txt",
            os.path.dirname(__file__) + "/../../../cache/mac-vendors.txt",
        ]

        for location in possible_locations:
            if os.path.exists(location):
                return location


class AsyncMacLookup(BaseMacLookup):
    def __init__(self):
        self.prefixes = None

    async def load_vendors(self):
        self.prefixes = {}

        vendors_location = self.find_vendors_list()
        if vendors_location:
            logging.log(logging.DEBUG, "Loading vendor list from {}".format(vendors_location))
            async with aiofiles.open(vendors_location, mode='rb') as f:
                # Loading the entire file into memory, then splitting is
                # actually faster than streaming each line. (> 1000x)
                for l in (await f.read()).splitlines():
                    if b"(base 16)" in l:
                        prefix, vendor = (i.strip() for i in l.split(b"(base 16)", 1))
                        self.prefixes[prefix] = vendor
        else:
            try:
                os.makedirs("/".join(AsyncMacLookup.cache_path.split("/")[:-1]))
            except OSError:
                pass
        logging.log(logging.DEBUG, "Vendor list successfully loaded: {} entries".format(len(self.prefixes)))

    async def lookup(self, mac):
        mac = self.sanitise(mac)
        if not self.prefixes:
            await self.load_vendors()
        if type(mac) == str:
            mac = mac.encode("utf8")
        try:
            return self.prefixes[mac[:6]].decode("utf8")
        except KeyError:
            raise VendorNotFoundError(mac)


class MacLookup(BaseMacLookup):
    def __init__(self):
        self.async_lookup = AsyncMacLookup()
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def lookup(self, mac):
        return self.loop.run_until_complete(self.async_lookup.lookup(mac))

    def load_vendors(self):
        return self.loop.run_until_complete(self.async_lookup.load_vendors())

