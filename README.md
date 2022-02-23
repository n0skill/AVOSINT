# AVOSINT
![Logo of AVOSINT](./logo/AVOSINT.svg)

A tool to search Aviation-related intelligence from public sources.

## Usage

```
./avosint.py [--action ACTION] [--tail-number TAIL-NUMBER] [--icao ICAO]
```

With ACTION being either 'ICAO', 'tail', 'convert'.

ICAO - Gather infos from ICAO transponder hex code.
tail - Gather info from tail number. Option `--tail-number` is required.
convert - Convert USA hex to ICAO. Option `--icao` is required.


