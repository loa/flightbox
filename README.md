# FlightBox

FlightBox is a modular, event-based processing framework for aviation-related data, writen in Python. It can be used, e.g., to receive GNSS/GPS, ADS-B and FLARM signals, process them, and provide a data stream to navigation systems, like SkyDemon.

For receiving ADS-B and FLARM signals, two DVB-T USB dongles with a certain chip set, which are compatible to the rtl-sdr tools (<http://sdr.osmocom.org/trac/wiki/rtl-sdr>), are required.

Currently, the default configuration assumes that the FlightBox files are located at `/home/pi/opt/flightbox`, and OGN receiver tools in `/home/pi/opt/rtlsdr-ogn`.  There is a watchdog script called `flightbox_watchdog.py`, which starts and monitors all required processes except the `dump1090` daemon (required for receiving ADS-B data). 

## Requirements

Below are requirements from the hardware and software perspective.  Note that a system with reduced features, like only receiving ADS-B, works, too.

### Hardware

* Computing device, like Raspberry Pi 3
* DVB-T USB dongle that is supported by rtl-sdr (one required for ADS-B reception and another one for receiving FLARM)
* GNSS (GPS/GLONASS) UART
  * E.g., with u-blox 8 chipset

### Software

* ADS-B decoder that provides SBS1 data stream, like dump1090
* OGN FLARM decoder
* Screen (in case the watchdog script is used)
* Python 3


### Transformation

#### SBS1/OGN/NMEA to FLARM NMEA converter

To process all GNSS, OGN, and SBS1 data and generate a FLARM data stream (TCP Port 2000, containing position and traffic information), the module `transformation_sbs1ognnmea` implements all required processing steps.  Therefore, the module consumes NMEA, OGN, and SBS1 messages (types `nmea`, `ogn`, `sbs1`) from the data hub and inserts FLARM messages (type `flarm`) back to the data hub after processing.

## Installation procedure

https://github.com/biturbo/flightbox-setup
