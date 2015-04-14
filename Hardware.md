= Ctrl-O Hardware Setup =

== Connections ==

=== Relays ===
Depending on your board there maybe 1-3 Orange Relays installed with corresponding blue screw terminals.  

==== Door Strike Relay ====
The small relay with terminals at the end of the board is used for the strike.

The proper connections for this is to connect the ground (if strike is polarized) to the center connection and the positive to the appropriate side based on strike type.
Side labelled NO is for normally open for strikes that are locked with unpowered.
Side labelled NC is for normally open for strikes that are locked only when powered.

==== Power Relays ====
The two power relays allow for switching power as a future option to control other hardware like tools and power vents..

=== Power ===
Power to the board is provided by a 7-36VDC power supply attached to the barrel jack .  This is typicaly connected to a PoE adapter set to 12VDC.

=== Strike Voltage Jumper ===
There is a 3 pin header J2 near the strike relay.  This is setup to jumper either the DC input supply (12V) or 5V from the regulator. This controls the voltage applied to the strike.

=== Reader Connector ===
There is an 8 pin connector J3 that is for connecting to the RFID reader.  This has the following pinout:
1: GND
2: +5V
3: RXD
4: TXD
5: Buzzer
6: Red LED
7: Green LED
8: Blue LED

== Networking ==
The ctrl-o board can be network enabled by using usb wifi adapters, or the integrated ethernet cable.  By using a PoE adapter and Ethernet to a local server/switch you can provide UPS'd power for multiple doors and only need to run one cable to each door.