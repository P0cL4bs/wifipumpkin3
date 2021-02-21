# Changelog
All notable changes to this project will be documented in this file.


## [Unreleased]

## [1.0.X] - 2021-XX-XX


### Added 
- added route for get information of plugins and proxies on restAPI 
- added new attribute on plugins and proxies mode class 

### Changed

### Deprecated

### Removed

### Fixed
- fixed cli error when resquest restAPI plugins and proxies
- fixed restApi error when get exceptions http request
- fixed wirelesscontroller not started into restAPI mode
- fixed locale error in docker container

## [Released]

## [1.0.8] - 2020-11-14

### Added
- added inactivity poll default value to 60 min #67
- added check if process hostapd is running before start threads
- added settings binary path of iptables editable 
- added waitforfinish on Qprocess for add rules iptables 
- added frist restful api implementation 
- added DHCP command to select dhcp server configuration
- added stop all modules with the command stop or exit is runnning
- added new module for perform dns spoof attack with AP enable 

### Changed

### Deprecated

### Removed
- removed dependencies that be standard library #105

### Fixed
- fixed hide error object of type QProcess on WorkProcess class #93
- fixed settings dhcp for allow to change dhcp configuration
- fixed error when execute from github actions 
- fixed set restport by default 1337 
- fixed process init hostapd duplicated
- fixed clean code and code format improves
- fixed github actions error when try to run pytests
- fixed dhcp command for apply configurations on same session

## [Released]

## [1.0.7] - 2020-08-01

### Added
- added WorkProcess class for execute comand with Qprocess
- added correctly package beautifulsoup4 into requirements.txt
- added command banner:  display an awesome wp3 banner 
- added many improvements into system modules
- added improves module for running in background
- added command kill: terminate a module in background by id 
- added option on captiveflask to force redirect sucessful template
- added set ssid with any caracter utf8 

### Changed
- moved command info to extensions directory
- changed more flexible python version into dependencies #36
- improves the architecture files extensions commands

### Deprecated
- deprecated scapy_http and migrate to scapy 2.4.4 has native support for HTTP #35

### Removed
- removed folder core/controls from file structure arch 
- removed bs4==0.0.1 Dummy package for Beautiful Soup

### Fixed
- fixed improves method setIptables from wirelessmode default mode 
- fixed clear dependencies not used from requirements files
- fixed include message: the module not found or failed to import.
- fixed typo name proxys to proxies
- fixed version of dnslib from pydns_server #49
- restricting version module problems
- fixed description tool on setup.py file 
- fixed mode docker parser command line #56
- fixed deprecation warnings due to invalid escape sequences. [tirkarthi]
- fixed issue with self.udp_server #68



## [released]

## [1.0.5] - 2020-05-29

### Added 
- added new module extra-captiveflask templates [mh4x0f]
- added plugins folder on config user [mh4x0f] 
- added command update in core commands [mh4x0f]
- added new implementation for load native extensions [mh4x0f] 
- added helps for all available commands [mh4x0f]
- added category to improvements the help command [mh4x0f]
- added new module wifideauth for send deauthentication packets [mh4x0f]
- added show up pydhcpserver log explanation [mh4x0f]
- added redirecting HTTPS traffic to captive portal [mh4x0f]
- added new format table for pretty printing [mh4x0f]

### Changed
- changed structure of all plugins and proxies [mh4x0f]
- update requirements files to unlock version [mh4x0f]

### Deprecated

### Removed
- removed rules iptables block https comunication captiveflask #37 [mh4x0f]

### Fixed
- fixed improves test_coverage makefile [mh4x0f]
- fixed requests module dependency on requirements.txt [mh4x0f]
- fixed PyQt5 error on docker image creation #44 [mh4x0f]
- fixed set a tag version at the base image in Dockerfile #43 [mh4x0f]
- fixed responder3 object has no attribute logger #39 [mh4x0f]
- fixed DHCP offer Apple device can’t connect to ap #32 [mh4x0f]
- fixed get multi language options on captiveflask plugin #30 [mh4x0f]
- fixed check if hostapd is installed in the system [mh4x0f]
- fixed better mode to print stop/start threads info [mh4x0f]
- fixed AttributeError Sniffkin3 object has no attribute help_plugins [mh4x0f]
- fixed set as default HOSTNAME  key on leases object [mh4x0f]
- fixed settings default status_ap values that change on #23 [mh4x0f]
- fixed lock command start when AP is running [mh4x0f]
- fixed NoProxy object has no attribute parser_set_noproxy #24 [mh4x0f]
- fixed keyError: args command --no-colors [mh4x0f]
- fixed list sub-plugins currently on command info [mh4x0f]
- fixed bug on dnserver try create AP without internet [mh4x0f]
- fixed error iptables with try create AP without internet [mh4x0f]


## [Released]

## [1.0.0] - 2020-04-18

### Added
- added allow sniffkin3 capture POST requests on session [mh4x0f]
- added more terminal colors on function setcolor [mh4x0f]
- added notification when client joined the AP [mh4x0f]
- added check python version when install tool [mh4x0f]
- added community tag discord on readme.md [mh4x0f]
- added news pulp templates on scripts [mh4x0f]
- added ISSUE_TEMPLATE.md on project [mh4x0f]
- added donate patreon on readme.md [mh4x0f]
- added autocomplete on command restore [mh4x0f]
- added system commands iptables,ls, clear, nano [mh4x0f]
- added file manifast.in [mh4x0f]
- added check must be run as root. [mh4x0f]
- added initial logo design tool on README.md [mh4x0f] 
- added initial details for tool on  README.md [mh4x0f] 
- added code formarter black tool [mh4x0f] 
- added makefile configuration [mh4x0f]
- added no-colors arguments commands [mh4x0f] 
- added info command list all plugin from proxys [mh4x0f]
- added parser for set plugin pummpkinproxy [mh4x0f]
- added packet http info into sniffkin3 json log [mh4x0f] 
- added alert when the client left the ap [mh4x0f]
- added exceptions implementation error [mh4x0f]
- added license header __init__ file [mh4x0f]
- added license header all files in plugins [mh4x0f]
- added license header all files in modules [mh4x0f]
- added license header all files in core/wirelessmode [mh4x0f]
- added license header all files in core/widgets [mh4x0f]
- added license header all files in core/utility [mh4x0f]
- added license header all files in core/ui [mh4x0f]
- added partial codereview on servers plugins and proxys [mh4x0f]
- added license header all files in core/packets and controls [mh4x0f]
- added license header all files in core/common [mh4x0f]
- added start tool with finish install on docker [mh4x0f]
- added enable security WPA,WEP, WPA2 mode wireless [mh4x0f]
- added parser wireless mode options [mh4x0f]
- Added changelog 1.0.0 version. [mh4x0f]
- Added generate random session id. [mh4x0f]
- Added random banners ascii art. [mh4x0f]
- Added somes improvements controller system. [mh4x0f]
- Added tabulate data captive portal credentails. [mh4x0f]
- Added keyboard interruption event on cmdloop. [mh4x0f]
- Added settings load plugin pumpkinproxy. [mh4x0f]
- Added command jobs, added function display_tabulate. [mh4x0f]
- Added command info modules/proxys. [mh4x0f]
- Added wi command on dockerfile. [mh4x0f]
- Added command mode, initial docker wireless mode. [mh4x0f]
- Added captiveflask proxy plugin. [mh4x0f]
- Added pumpkinproxy plugins visualization. [mh4x0f]
- Added implementation core plguin,proxy parser function. [mh4x0f]
- Added config plugins, show plugin status, fixed responder3. [mh4x0f]
- Added description change to tabulate info modules. [mh4x0f]
- Added sniffkin3 mitm modules. [mh4x0f]
- Added commands, proxy and plugins implementation. [mh4x0f]
- Added monitor dhcp requests ui terminal. [mh4x0f]
- Merge pull request #2 from mh4x0f/beta. [Marcos Bomfim] bump version to dev
- Merge pull request #1 from mh4x0f/news. [Marcos Bomfim] bump to beta version
- Added implementation of ssltrip3 & PumpkinProxy. [mh4x0f]
- Build the package wifipumpkin3. [mh4x0f]
- Improved info_ap command print mode. [mh4x0f]
- Added initial implementation of PumpkinProxy. [mh4x0f]
- Added cyan color print, new banner format and etc. [mh4x0f]
- Added wifiscan 1.1 new implementation. [mh4x0f]
- Initial implementation modules architeture. [mh4x0f]
- Added interactive sessions can be scripted with .pulp file and string.[mh4x0f]
- Added loguru lib. [mh4x0f]
- Added LoggerManager module. [mh4x0f]
- Added Responder3 tool as a plugin mitmMode. [mh4x0f]
- Added mitmcontroller and mitm module test. [mh4x0f]
- Added DNSServer logger. [mh4x0f]
- Added proxycontroller. [mh4x0f]
- Added dns controller, new python DNSServer. [mh4x0f]
- Initial module architecture components. [mh4x0f]
- Plugins filter invalid arguments. [mh4x0f]
- Added function getColorStatusPlugin. [mh4x0f]
- Added PumpkinProxy options for activate plugin. [mh4x0f]
- More files compiler removed. [mh4x0f]
- Added exclude files. [mh4x0f]
- Initial commit. [mh4x0f]

### Changed
- changed implemenation on proxymode base class [mh4x0f]
- changed interface key to None in file config.ini [mh4x0f] 
- changed requirements PyQt5==5.14.0 to PyQt5==5.14.2 [mh4x0f]
- restore folder logs from .gitignore [mh4x0f]
- changed check is rootuser for use on github actions deploy [mh4x0f]
- changed name author to made by into bin/wifipumpkin3 [mh4x0f] 
- refactored all controllers implementation codestyle [mh4x0f]
- improved folder copy code on setup.py [mh4x0f]
- exclude config folder from language statistics [mh4x0f]
- changed codename to nidavellir [mh4x0f]
- moved /scripts to user dir config [mh4x0f]
- changed logs folder model [mh4x0f]
- Moved __main__ code  to __init__ [mh4x0f]
- Changed python3.6 to python3.7. [mh4x0f]
- Change do_info command to tabulate style. [mh4x0f]
- Changed prompt line to more simple ;) [mh4x0f]


### Deprecated

### Removed
- removed force specific version of module PyQt [mh4x0f]
- removed function old setup_logger wp2 [mh4x0f] 
- removed all python modules on test folder [mh4x0f]
- removed old implementation loader accesspoint [mh4x0f]
- Removed history.md file [mh4x0f]
- Removed keys not using in project. [mh4x0f]
- Remove lib not using in the project. [mh4x0f]
- Removed somes import nyscreen. [mh4x0f]
- Removed folder .idea files settings. [mh4x0f]
- Removed folder vscode files settings. [mh4x0f]
- Removed all plugins from python2 implementation. [mh4x0f]
- Removed error BeautifulTable. [mh4x0f]
- Removed file test. [mh4x0f]
- Removed all files *.py compiler. [mh4x0f]
  
### Fixed
- fixed Error: PyQt5.sip not found, but it is installed. [mh4x0f]
- fixed IndexError: list index out of range #14 [mh4x0f]
- fixed error depedency PyQt5-sip when try on virtualenv [mh4x0f] 
- fixed set iptables exception for each rules [mh4x0f] 
- fixed typo name on readme.md [mh4x0f]
- fixed disable security auth wireless by default [mh4x0f]
- added depedency PyQt5-sip==12.7.2 to requirements.txt [mh4x0f]
- fixed downgrade version pyqt 5.14.2 to version 5.14 [mh4x0f]
- fixed require coverage on test makefile [mh4x0f]
- stable version that contains [mh4x0f]
- fixed website links on Readme.md [mh4x0f] 
- force copy all files `config` to user_config_dir [mh4x0f]
- fixed description plugin responder3 [mh4x0f]
- fixed description all plugin and proxy [mh4x0f] 
- fixed dependency of wireless-tools for use iwconfig command [mh4x0f] 
- fixed beef parameter hook to url_hook [mh4x0f]
- fixed makefile option to clean setup.py [mh4x0f]
- fixed error hostpad_response when client left ap [mh4x0f] 
- fixed log hostapd send (state) with close the ap [mh4x0f]
- fixed set linguist-vendored=false to exclude language statistics [mh4x0f]
- fixed try to exclude files from git language statistics [mh4x0f]
- fixed bug when try restart AP with modification in interface name [mh4x0f]
- fixed bug when try mout AP on wirelesscontroller [mh4x0f]
- fixed set as default require python version 3.7 [mh4x0f]
- fixed  set linguist-documentation to false [mh4x0f]
- fixed exclude all files from config the language statistics [mh4x0f]
- fixed module print infor data [mh4x0f]
- fixed bug file descriptor bad dhcpserver [mh4x0f]
- fixed bug when try to load all plugins on sniffkin3 [mh4x0f]
- fixed mascared bug file descriptor bad partial solution [mh4x0f]
- Fixed session id not empty when start app. [mh4x0f]
- Fixed wirelessmode docker remount ap without errors. [mh4x0f]
- Fixed name file configuration. [mh4x0f]
- Fixed logger pydnsserver and clear somes code. [mh4x0f]
- Fixed terminal module display_tabulate. [mh4x0f]
- Fixed color ui show clients connected. [mh4x0f]
- Fixed error when try to use module wifiscan. [mh4x0f]
- Fixed limit caracter description plugin and proxys. [mh4x0f]
- Fixed constants dns hosts. [mh4x0f]
- Fixed new banner app. [mh4x0f]
- Fixed logger ssltrip3 class. [mh4x0f]
- Fix small bug on get interfaces. [mh4x0f]
- Fixed stop hostapd and some improvements. [mh4x0f]
- Fixed somes bugs on UI and add more features. [mh4x0f]
- Fixed argparse arguments. [mh4x0f]
- Fixed window urwid implementation. [mh4x0f]
