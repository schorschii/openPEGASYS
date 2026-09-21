# Controller Communication
The software communicates over a serial interface with one or multiple hardware controllers. Those controllers are often connected via a serial-IP converter to transmit the data via network (from a branch office) to the control computer. Direct serial attachment is currently not implemented.

## Examples
### Status Request
Description: periodically (every 15s)  
From: computer, random UDP port  
To: controller, static configured UDP port (e.g. 10001)  
Content: `!F#`

### Status Response
Description: as response to a status request
From: controller, static configured UDP port (e.g. 10001)  
To: computer, random UDP port  
Content: `&F#`

### Access Request
Description: a card was scanned by a reader, check if access should be granted
From: controller, static configured UDP port (e.g. 10001)  
To: computer, static configured UDP port (e.g. 23)  
Content: `%39V00:1223724,1,210926,1234,0,00,0 09#`  
Content dissection:
- `%`       --> begin message
- `39V`     --> opcode?
- `00:1`    --> controller:reader
- `223724`  --> time
- `3`       --> day of week
- `210926`  --> date
- `1234`    --> card number
- `0`       --> ?
- `00`      --> ?
- `0 09`    --> ?
- `#`       --> end message

### Access Response
Description: as response to an access request (access granted)  
From: computer, static configured UDP port (e.g. 23)  
To: controller, static configured UDP port (e.g. 10001)  
Content: `&F#`
