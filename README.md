**PYOUTLET**
============

Python CLI & Web switcher for Etekcity power outlets using 433MHz RF
--------------------------------------------------------------------

Python wrapper around rfoutlet (from https://timleland.com/wireless-power-outlets/)
to control **Etekcity power outlets from a Raspberry Pi** using a 433MHz RF emitter module.

It has a simple **CLI** utility and a minimal **flask webapp** with ON/OFF buttons and a config editor.

- Install is as simple as `pip install pyoutlet`

- CLI usage:
    `switch off label_switch_5`
    `switch on 4`
        TURN ON SWITCH "4" -> Sending Code: 4529411. PIN: 0. Pulse Length: 185
    `switch --info`
        ** PYOUTLET JSON config in "/path/to/pyoutlet/codes_outlets.json"
        --> * 1                    -> ON:4527411, OFF:4527420
            * 2                    -> ON:4527555, OFF:4527564
            * 3                    -> ON:4527875, OFF:4527884
            * 4                    -> ON:4529411, OFF:4529420
            * label_switch_5       -> ON:4535555, OFF:4535564

- Outlet CODES are saved (and labeled) in a JSON file, inside `pyoutlet` module, like this:

	  {
	    "pulse_length": 185,
	    "outlets":
          [
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
			  "label": "4"
			},
			{
			  "on": 4535555,
			  "off": 4535564,
			  "label": "label_switch_5"
			}
		  ]
	  }
