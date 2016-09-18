# Telldus tdtool sensor logger

Logs Telldus tdtool sensors to selected Google Sheet.

## Setup

This requires a `credentials.json` file to be present in the file root, which
is used for getting authorization to use the Google Sheet. This can be
obtained from Googles Developer Console.

It looks for a environment variable to to select which Spreadsheet to choose,
called `GOOGLE_SPREADSHEET_KEY`. For a simple setup of this using systemd, see
the attached `temperature.service` file.

Since `tdtool` is used for displaying sensor information, this is a
requirement as well.

## Requirements

Python dependencies are listed in `requirements.txt`.


