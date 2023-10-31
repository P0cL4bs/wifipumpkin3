from wifipumpkin3.core.common.terminal import ModuleUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import display_messages, setcolor
from wifipumpkin3.core.common.threads import ProcessThread

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class ModPump(ModuleUI):
    """Perform a dns spoof with accesspoint attack"""

    name = "dns_spoof"

    default_hosts = [
        "# this is an example zones file",
        "# each line with parts split on white space are considered thus:",
        "#     1:               the host",
        "#     2:               the record type",
        '#     everything else: either a single string or json list if it starts with "["',
        "#     lines starting with white space are striped of white space (including newline)",
        "#     and added to the previous line",
        "example.com  A       10.0.0.1",
        "example.com  CNAME   whatever.com",
        'example.com  MX      ["whatever.com.", 5]',
        'example.com  MX      ["mx2.whatever.com.", 10]',
        'example.com  MX      ["mx3.whatever.com.", 20]',
        "example.com  NS      ns1.whatever.com.",
        "example.com  NS      ns2.whatever.com.",
        "example.com  TXT     hello this is some text",
        'example.com  SOA     ["ns1.example.com", "dns.example.com"]',
        "# because the next record exceeds 255 in length dnserver will automatically",
        "# split it into a multipart record, the new lines here have no effect on that",
        "testing.com  TXT    one long value: IICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAg",
        "    FWZUed1qcBziAsqZ/LzT2ASxJYuJ5sko1CzWFhFuxiluNnwKjSknSjanyYnm0vro4dhAtyiQ7O",
        "    PVROOaNy9Iyklvu91KuhbYi6l80Rrdnuq1yjM//xjaB6DGx8+m1ENML8PEdSFbKQbh9akm2bkN",
        "    w5DC5a8Slp7j+eEVHkgV3k3oRhkPcrKyoPVvniDNH+Ln7DnSGC+Aw5Sp+fhu5aZmoODhhX5/1m",
        "    ANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA26JaFWZUed1qcBziAsqZ/LzTF2ASxJYuJ5sk",
    ]

    options = {
        "redirectTo": ["10.0.0.1", "ip address to redirect traffic"],
        "domains": [None, "the targets domain's name server"],
    }
    completions = list(options.keys())

    domains = []

    def __init__(self, parse_args=None, root: dict =None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name
        self.filepath_dns_hosts = C.DNSHOSTS
        self.rules_model = "{dns}  A       {redirect}\n"
        super(ModPump, self).__init__(parse_args=self.parse_args, root=self.root)
        self.options["redirectTo"][0] = self.conf.get("dhcp", "router")

    def initialize(self):
        self.options["redirectTo"][0] = self.conf.get("dhcp", "router")
        
    def do_add(self, args):
        """add domain for perform attack dns spoof"""
        if not self.options.get("domains")[0]:
            self.options["domains"][0] = ",".join([args])
            return

        targets = self.options.get("domains")[0].split(",")
        targets.append(args)
        self.options["domains"][0] = ",".join(targets)

    def do_rm(self, args):
        """remove a domain from list dns spoof"""
        if not self.options.get("domains")[0]:
            return print(display_messages("the list of domains is empty", error=True))

        targets = self.options.get("domains")[0].split(",")
        try:
            targets.remove(args)
            if targets != []:
                self.options["domains"][0] = ",".join(targets)
            else:
                self.options["domains"][0] = None
        except ValueError:
            return print(
                display_messages(
                    "the value {} not in the domains list".format(args), error=True
                )
            )

    def do_start(self, args):
        """start update dns zones file"""
        if self._background_mode:
            print(
                display_messages(
                    "there are a dnsspoof module in brackground.", error=True
                )
            )
            return

        redirectTo = self.options.get("redirectTo")[0]

        if not self.options.get("domains")[0]:
            print(
                display_messages(
                    "please, select a domains to perform attack ", error=True
                )
            )
            return

        print(display_messages("DnsSpoof attack", info=True, sublime=True))
        print(
            display_messages(
                "Redirect to: {} ".format(setcolor(redirectTo, color="blue")),
                info=True,
            )
        )
        print(display_messages("Targets:", info=True, sublime=True))
        for target in self.options.get("domains")[0].split(","):
            print(
                display_messages(
                    "-> [{}] ".format(setcolor(target, color="red")),
                    info=True,
                )
            )

        self.handler_dnshosts = open(self.filepath_dns_hosts, "a")
        for target in self.options.get("domains")[0].split(","):
            self.handler_dnshosts.write(
                self.rules_model.format(dns=target, redirect=redirectTo)
            )
        self.handler_dnshosts.close()

        self.set_background_mode(True)

    def do_stop(self, args):
        """stop or restore the default dns zone file"""
        self.handler_dnshosts = open(self.filepath_dns_hosts, "w")
        for line in self.default_hosts:
            self.handler_dnshosts.write(line + "\n")
        self.handler_dnshosts.close()
        self.set_background_mode(False)
