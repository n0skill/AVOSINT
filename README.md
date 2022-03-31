# AVOSINT
A tool to search Aviation-related intelligence from public sources.

## Usage
### Launch parsr docker image (for pdf-file stored registers)
`docker run -p 3001:3001 axarev/parsr`

### Launch avosint
`./avosint.py [--action ACTION] [--tail-number TAIL-NUMBER] [--icao ICAO]`

With ACTION being either `ICAO`, `tail`, `convert`, `monitor`

`tail` - Gather infos starting from tail number. Option `--tail-number` is required.

`convert` - Convert USA hex to ICAO. Option `--icao` is required.

`monitor` - Gathers positionnal information from osint sources and detects hovering patterns. Requires `--icao` number 

Returns the following informations when possible:
* Owner of the aircraft
* User of the aircraft
* Aircraft transponder id
* Aircraft manufacturer serial number
* Aircraft model
* Aircraft picture links
* Aircraft incident history

The following display is then presented:
```==========================================
Current Status: [Done]
Last action: tail
Current tail: {tail_n}
==========================================
✈️ Aircraft infos:

        Manufacturer: {}
        Manufacturer Serial Number: {}
        Tail Number: {}
        Call Sign: {}
        Last known position: {}
        Last known altitude: {}
        
🧍 Owner infos

        Name: {} 
        Street: {}   
        City: {} 
        ZIP: {}
        Country: {}
            
New Action [ICAO, tail, convert, monitor, exit, quit] (None):
```

## Dependencies
### Install python requirements
`pip install -r requirements.txt`

This tool also uses the OpenSkyApi available at https://github.com/openskynetwork/opensky-api. Install it using:
```bash
git clone https://github.com/openskynetwork/opensky-api 
pip install -e /path/to/repository/python
```
### Install Parsr docker image
`docker run -p 3001:3001 axarev/parsr`
### Parsr 
As some registers are in the form of a pdf file, AVOSINT uses parsr (https://github.com/axa-group/Parsr)
Due to a bug in the current version of the parsr library (https://github.com/axa-group/Parsr/issues/565#issue-1111665010) it is necessary to apply the following fix in the `parsr-client` python library:


```diff
return {
- 'file': file,
- 'config': config,
+ 'file': file_path,
+ 'config': config_path,
  'status_code': r.status_code,
  'server_response': r.text
}
```
### Donations
If you wish to offer me a coffee, you can donate at 
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K4BO91O)
