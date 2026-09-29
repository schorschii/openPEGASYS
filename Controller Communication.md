# Controller Communication
The software communicates over a serial interface with one or multiple hardware controllers. Those controllers are often connected via a serial-IP converter to transmit the data via network (from a branch office) to the control computer. Direct serial attachment is currently not implemented.

## Examples
### Status Request
Description: periodically (every 15s)  
From: computer, random UDP port  
To: controller, static configured UDP port (e.g. 10001)  
Content: `!F#`

#### Response
From: controller, static configured UDP port (e.g. 10001)  
To: computer, random UDP port (same as request)  
Content: `&F#`

### Read Info
Description: a card was scanned by a module (card reader)  
From: controller, static configured UDP port (e.g. 10001)  
To: computer, static configured UDP port (e.g. 23)  
Content example: `%39V00:1223724,1,210926,1234,0,00,0 FD#`  
Content dissection:
- `%`       --> begin message
- `39`      --> message length (including `%` and `#`)
- `V`       --> opcode?
- `00:1`    --> controller:module
- `223724`  --> time
- `3`       --> day of week
- `210926`  --> date
- `1234`    --> card number
- `0`       --> ?
- `00`      --> ?
- `0`       --> ?
- `FD`      --> uppercase hex additive modulo 256 checksum (sum % 256, including `%` and ` ` (space)), zero-padded to 2 chars
- `#`       --> end message

#### Response
From: computer, static configured UDP port (e.g. 23)  
To: controller, static configured UDP port (e.g. 10001)  
Content: `&F#`

### Permission Change
Description: administrator changed permission of a user record  
From: computer, static configured UDP port (e.g. 23)  
To: controller, static configured UDP port (e.g. 10001)  

Content example (line breaks added for reabability):  
```
%21C*:*U=1234,0,D A1#
%32C*:*U=1234,0,E,2,0,D,,0,0 B2#
%24C20:9U=1234,0,A,E 59#
%24C11:9U=1234,0,A,E 59#
```

Content dissection (opcode `C`):
- line 1: reset cached permissions on controller
- line 2: grant access to level `2`
  - `*:*`    --> any controller:module
  - `U=1234` --> card no 1234
  - `0` --> ?
  - `E` --> enabled/disabled?
  - `2` --> level ID (table Levels)
  - `0` --> ?
  - `D` --> ?
  - ``  --> PIN
  - `0` --> ?
  - `0` --> ?
- line 3 & 4: grant access on controller:module 20:9 and 11:9
  - only sent to hardware systems where the corresponsing module is connected
- checksum as described above

#### Response
From: controller, static configured UDP port (e.g. 10001)  
To: computer, static configured UDP port (e.g. 23) 
Content: `&F#`
