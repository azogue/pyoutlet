**PYOUTLET**
============

Python CLI & Web switcher for Etekcity power outlets using 433MHz RF
--------------------------------------------------------------------

Python wrapper around rfoutlet (from https://timleland.com/wireless-power-outlets/)
to control **Etekcity power outlets from a Raspberry Pi** using a 433MHz RF emitter module.

It has a simple **CLI** utility and a minimal **flask webapp** with ON/OFF buttons.

- Outlet CODES are saved (and labeled) in a JSON file, inside `pyoutlet` module, like this:

	  {
	    "pulse_length": 185,
	    "outlets": [
			{
			  "on": 4527411,
			  "off": 4527420,
			  "label": "1"
			},
			{
			  "on": 4527555,
			  "off": 4527564,
			  "label": "2"
			},
			{
			  "on": 4527875,
			  "off": 4527884,
			  "label": "3"
			},
			{
			  "on": 4529411,
			  "off": 4529420,
			  "label": "switch X"
			},
			{
			  "on": 4535555,
			  "off": 4535564,
			  "label": "switch Y"
			}
		  ]
		}
		{
		"pulse_length": 185,
