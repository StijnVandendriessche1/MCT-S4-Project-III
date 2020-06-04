from Sensors.Mcp import Mcp
import time

mcp = Mcp(0,0)

while True:
    print("kanaal0: %f" % mcp.read_channel(0))
    print("kanaal1: %f" % mcp.read_channel(1))

    print("afgetrokken")
    print(mcp.read_channel(0) - mcp.read_channel(1))
    print(mcp.read_channel(1) - mcp.read_channel(2))

    print("opgeteld")
    print(mcp.read_channel(0) + mcp.read_channel(1))

    print("vermenigvuldigd")
    print(mcp.read_channel(0) * mcp.read_channel(1))

    print("kwadraten")
    print(mcp.read_channel(0) ** 2)
    print(mcp.read_channel(1) ** 2)

    #print("geschat gewicht")
    kwadraat = mcp.read_channel(0) ** 2
    dink = kwadraat - 300000
    #print(dink/30000)
    time.sleep(1)