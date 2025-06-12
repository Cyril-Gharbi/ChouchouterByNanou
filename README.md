# Chouchouter By Nanou

**CHOUCHOUTER_BY_NANOU** is a python application intended to be used as a showcase site.
It allows visitors to consult its achievements, to know its services with possibility to make
appointements by sending them back to the booking site and to have a loyalty follow-up.

This application is created for a nail technician who needs very simple use.
An admin dashboard is also created to facilitate its management.

The application is being created for an RNCP project and will be deployed afterwards.

For the moment, the coding is done on a 27' screen and I have not yet done the coding for adaptation to other screen sizes.
There may be display issues.


## Installation

1. Clone this repository :
   ```bash
   git clone git@github.com:Cyril-Gharbi/ChouchouterByNanou.git
   cd CHOUCHOUTER_BY_NANOU

2. Create and activate a virtual environment

3. Install dependancies (requirements.txt):
   type './setup_env.bat' in terminal


## Use

* Lauch the application :
    type 'python main.py' in terminal

* use of the QRcode :
    You need a local network accessible from several devices (ex: ngrok).
    Open another terminal : ngrok http 5000
    Add the IP adress ngrok on 'generate_qr.py' in 'url'
    Type 'python generate_qr.py' in terminal (a new file with a QRcode to be created)
    Scan the QRcode (an upstream account creation is essential)


## Auteur

   The application is developed by Cyril Gharbi.

