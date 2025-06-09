# PLC Data Analysis

This example shows how to read cycle time and cell status values from a Siemens PLC and expose the data through a web interface. Cycle times are persisted in a SQLite database. The main page displays the last ten cycle times along with the average.

## Requirements

- Python 3.11+
- The packages listed in `requirements.txt`
- Network access to the PLC

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Running

Update the IP address, rack and slot in `app.py` as needed. The monitor reads
cycle times from DB9994 using a set of predefined offsets and connects to
`192.168.3.1` by default. It will read all known cells (currently 16) unless a
different count is specified. Run:

```bash
python app.py
```

Navigate to `http://localhost:5000` to see the web page.

The application continuously polls the PLC and records cycle time and status values in `plc_data.db`.
