from Sensors.Mcp import Mcp
import time

mcp = Mcp(0,0)

while(True):
    print(mcp.read_channel(0))
    time.sleep(0.1)