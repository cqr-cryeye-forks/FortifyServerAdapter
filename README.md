# Fortify Server Adapter

Share you local Fortify app to the network.

you can run locals scan or use my custom client for scanning local files on remote Fortify

## Run
`main.py` with some of the flags bellow.
Select host and port for listening. You can use no-ip or other services for running analyse through all web, not only local network 


## Setup

```angular2html
usage: main.py [-h] [-ht HOST] [-p PORT] [-s SOURCES] [-l] [-o OUTPUT]
               [-of OUTPUT_FORMAT] [-t TARGET]

Fortify Server

optional arguments:
  -h, --help            show this help message and exit
  -ht HOST, --host HOST
                        Server host. Default 0.0.0.0
  -p PORT, --port PORT  Server port. Default 33333
  -s SOURCES, --sources SOURCES
                        Path to fortify scan application. Default is
                        C:\Users\nicko\Documents\bin\sourceanalyzer.exe
  -l, --local           [Only for local scan] Use if want to analyze target
                        locally
  -o OUTPUT, --output OUTPUT
                        Output file
  -of OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        [Only for local scan] File extension for output.
                        Default: fvdl
  -t TARGET, --target TARGET
                        [Only for local scan] Path for analyzing. Default is parent dir

```
