README.md

Viptela Automation


This repo contains a set of tools to automate workflows and build CI/CD pipelines for Cisco Viptela SDWAN.
Note: The tools in this repo only work from a Unix environment. (e.g. Linux, MacOS, etc.) 

Installation

Cloning the repo
https://github.com/lipa-devops/viptela.git

All operations are run out of the viptela directory:
cd viptela
chmod 700 *

Software Dependancies
•	Python 3 with the dependencies listed in requirements.txt

Automation tools
•	activate site 
•	activation test
•	backup vManage database
•	data prefix list
•	image default
•	image upgrade
•	smart account
o	add serial number
o	verify serial number
o	sync account with vManage
•	vEdge speed test
•	template attach
•	template detach

Inventory and description

Site activation
tool will fetch all information about vEdge from vManage and guide you to run set of tools for a site activation. You can attach/detach templates, upgrade/set default image, run speed test, activation test. Tool is by default verifying if serial number is registered on Cisco smart account.   

Activation test
script will connect to vEdge over SSH and run several tests necessary for Ops team to take vEdge under management support which you can upload to ESP portal.

Test consists from these steps:
 - system version
 - mtu / packet size
 - hardware alarms
 - hardware environment
 - hardware inventory
 - control connections
 - bfd sessions
 - bgp summary
 - interface list
 - interface stats
 - interface details
 - policies from vsmart
 - vpn 0 configuration
 - vpn 1 default route
 - vpn 1 route to internal ip
 - vpn 1 traceroute google dns
 - vpn 1 traceroute internal ip
 - vpn 1 ping google dns
 - vpn 1 ping internal ip
 - vpn 0 ping all default gateways
 - vpn 0 ping google dns for INET circuits
 - vpn 0 ping gateway for PIP circuits
 - speed test to remote


Backup vManage database
script will connect to vManage over SSH and download database to your home folder ~/viptela/backup

Data prefix list
create / add / update or delete data prefix list

Image default
set default image version for vEdge devices

Image upgrade
upgrade image version on vEdge devices
Smart account
Script will connect to Cisco smart servers and verify if serial number is registered with your smart and virtual account. If serial number doesn’t exist will add it and synchronize with your vManage database. 

Speed test
Script will connect to vEdge device and start speed test. You will be asked to provide destination (remote) vEdge device to test the speed with and if more transport colors it will also ask to choose color.

Template attach
Attach template to vEdge. Script will ask you which template to assign into vEdge and will also ask you to fill all template variables. After list of variables provided you need to press “Ctrl d”.

Template detach
Template will be detached from vEdge.


Setup


You will need to run this tool only once to fill necessary information for tools to work properly.
You will need to provide all these below information which will be stored in ~/viptela/.conf file located in your home folder used only by automation tools. Config file can either be in clear text or fully encrypted. If encrypted. You will be always asked to provide decryption key. Don’t forget a key otherwise you will need to remove .conf file and run setup again to provide necessary information.

vManage / vEdge:
  - vManage IP address       
  - vManage username
  - vManage password
  - transport colors over internet
  - transport colors over mpls
  - vEdge image version                                                   (e.g: 18.4.5)
  - vEdge vpn id for customer / internal network            (e.g: vpn 1)
  - routable IP address in customer's vpn for ping tests
  
  Cisco:
  - Cisco account username
  - Cisco account password
  - Cisco client ID              (used for API access)
  - Cisco client secret        (used for API access)
  - Cisco smart account    (e.g: sdwan.verizon.com)
  - Cisco virtual account  
  
  Misc:
  - Your email address      (used by reports)







