# openPEGASYS
Re-implementation of basic features of the ancient proprietary PEGASYS CardKey P900 software to control the (door) access system.

The original Windows software is older than I am and hard to operate securely on modern Windows versions. This projects aims to provide the basic features using a modern software environment on Linux basis.

For details about the communication with the controllers, read [Controller Communication.md](Controller%20Communication.md).

## Installation
1. Install dependencies
   - `apt install python3-dbfread`

2. Migrate data or create empty database
   - You can import the dBASE files (found in the program's `/data` directory) from the original software by executing:
      ```
      ./import.py path/to/User32.dbf path/to/Levels32.dbf path/to/LevelRel32.dbf path/to/Points32.dbf path/to/Frames32.dbf path/to/HardSys32.dbf
      ```
   - You can execute it without parameters to create an empty database file (data.db) with the required schema.

3. Debug run
   - Execute `sudo ./pegasys.py` and check the output.
   - Test via `echo -en "%39V00:1223724,1,210926,1234,0,00,0 01#" > /dev/udp/127.0.0.1/23` (requires a temporary HardSys table entry for 127.0.0.1).

4. If everything works as expected, install it as systemd service:
   - copy `pegasys.service` int `/etc/systemd/system/`
   - adjust the path to your `pegasys.py`
   - `systemctl enable pegasys && systemctl start pegasys`

Have fun.
