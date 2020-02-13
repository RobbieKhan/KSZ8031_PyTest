import jft

class MDIO:
    def __init__(self, SDA="", SCL="", Address = 0x03):
        self.sda = SDA
        self.scl = SCL
        self.address = Address

    def __ConditionStart(self):
        jft.HighZ(self.sda)
        jft.DriveHigh(self.scl)
        jft.DriveLow(self.sda)
        jft.DriveLow(self.scl)

    def __ConditionStop(self):
        jft.DriveLow(self.sda)
        jft.DriveLow(self.scl)
        jft.DriveHigh(self.scl)
        jft.HighZ(self.sda)

    def __SlaveACK(self):
        jft.HighZ(self.sda)
        jft.DriveLow(self.scl)
        jft.DriveHigh(self.scl)
        acknowledgement = jft.GetVar(self.sda)
        jft.DriveLow(self.scl)
        return acknowledgement

    def __ByteWrite(self, byte):
        for bit in range(8):
            if byte[bit].__eq__("1"):
                jft.HighZ(self.sda)
            else:
                jft.DriveLow(self.sda)
            jft.DriveHigh(self.scl)
            jft.HighZ(self.sda)
            jft.DriveLow(self.scl)
            bit += 1

    def __ByteRead(self):
        byte = ""
        jft.HighZ(self.sda)
        jft.DriveLow(self.scl)
        for bit in range(8):
            jft.DriveHigh(self.scl)
            jft.DriveLow(self.scl)
            byte += str(jft.GetVar(self.sda))
            bit += 1
        return byte

    def Write(self, regAddress, regValue):
        CMD_WR = 0x15
        # Forming 2 instruction bytes, consisted of slave address, write code, desired register
        instructionHi = "{0:=05b}".format(CMD_WR) + "{0:=03b}".format(self.address >> 2)
        instructionLo = "{0:=02b}".format(self.address & 0x3) + "{0:=05b}".format(regAddress) + "1"
        # Forming 2 data bytes to be written into desired register
        dataHi = "{0:=08b}".format(regValue >> 8)
        dataLo = "{0:=08b}".format(regValue & 0xFF)
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite(instructionHi)
        self.__ByteWrite(instructionLo)
        # Sending one bit 0
        jft.DriveLow(self.sda)
        jft.DriveLow(self.scl)
        jft.DriveHigh(self.scl)
        jft.HighZ(self.sda)
        jft.DriveLow(self.scl)
        # Writing data
        self.__ByteWrite(dataHi)
        self.__ByteWrite(dataLo)

    def Read(self, regAddress):
        CMD_RD = 0x16
        # Forming 2 instruction bytes, consisted of slave address, read code, desired register
        instructionHi = "{0:=05b}".format(CMD_RD) + "{0:=03b}".format(self.address >> 2)
        instructionLo = "{0:=02b}".format(self.address & 0x3) + "{0:=05b}".format(regAddress) + "0"
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite("11111111")
        self.__ByteWrite(instructionHi)
        self.__ByteWrite(instructionLo)
        # Reading data
        dataHi = self.__ByteRead()
        dataLo = self.__ByteRead()
        return dataHi + dataLo