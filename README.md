[![Author](https://img.shields.io/badge/author-Pulsar7-lightgrey.svg?colorB=9900cc&style=flat-square)](https://github.com/Pulsar7)
[![Release](https://img.shields.io/github/release/dmhendricks/file-icon-vectors.svg?style=flat-square)](https://github.com/Pulsar7/Schlafdokumentation/releases)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/dmhendricks/file-icon-vectors.svg?style=social)](https://twitter.com/SevenPulsar)

# Schlafdokumentation
A precise overview of your own sleep and possible influences on sleeping behavior. 
**But**: This is not a scientific proven script. It only shows you some variables, that could have influence on your sleep behavior. It does not replace any doctor! The science behind our sleep behaviour is much more complicated than this script is able to compute.

## :pushpin: Table of contents

* :point_right: [Installation](#installation)
* :point_right: [Usage](#usage)
* :point_right: [ToDo](#ToDo)
* :point_right: [Suggestions & Reports](#suggestions--reports)

## Installation

:small_orange_diamond: **Download the repository from github with git and go to directory**
 
    sudo apt-get install git
    git clone https://github.com/Pulsar7/Schlafdokumentation.git
    cd Schlafdokumentation

:small_orange_diamond: **Create virtual environment & install requirements**

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    

## Usage

    python3 sleep_doku.py --file '[DATABASE_PATH].db'

or 

    python3 sleep_doku.py 

Then enter the *database-filepath* in the given input.

## ToDo
- [ ] 


## Suggestions & Reports

Suggestions or errors are welcome to be [:link: reported](https://github.com/Pulsar7/Schlafdokumentation/issues)!
