import jft
import jftsettings
import time
import mdio


class ksz8031:
    def __init__(self, RST="", CRS_DV="", ANEN_SPEED="", REF_CLK=""):
        self.pin_reset = RST
        self.pin_crs_dv = CRS_DV
        self.pin_anen_speed = ANEN_SPEED
        self.pin_ref_clk = REF_CLK
        self.id1 = 0x0022
        self.id2 = 0x1550
        pass

    def MDIO_Init(self, SDA="", SCL="", Address=0x03):
        self.mdio = mdio.MDIO(SDA=SDA, SCL=SCL, Address=Address)

    def Get_Address(self):
        print("Проверка стандартного адреса микросхемы:\n")
        try:
            jft.DriveLow(self.pin_reset)
        except:
            print("Пин RST неопределен или недоступен!\n")
            exit(1)
        time.Wait_Time(100000)
        try:
            if jft.GetVar(self.pin_crs_dv):
                i2cAddress = 0x03
            else:
                i2cAddress = 0x00
            print(f"Стандартный адрес микросхемы - {hex(i2cAddress)}\n")
        except:
            print("Пин CRS_DV неопределен или недоступен!\n")
            exit(1)
        jft.DriveHigh(self.pin_reset)
        time.Wait_Time(100000)
        return i2cAddress

    def Check_Id(self):
        print("Проверка ID микросхемы:\n")
        id1 = hex(int(self.mdio.Read(0x02), 2))
        id2 = hex(int(self.mdio.Read(0x03), 2))
        if id1.__eq__(self.id1) and (id2 & 0xFC00).__eq__(self.id2):
            print(f"Микросхема опознана. Модель - {id2 & 0x3F0}\n")
            return 0
        else:
            print(f"ID не совпадает с ожидаемым. Считанный ID1 - {id1}, ID2 - {id2 & 0xFC00}\n")
            return 1

    def Check_DefaultMode(self):
        print("Проеерка режима работы по умолчанию\n")
        try:
            jft.DriveLow(self.pin_reset)
        except:
            print("Пин RST неопределен или недоступен!\n")
            exit(1)
        time.Wait_Time(100000)
        try:
            pinValue = jft.GetVar(self.pin_anen_speed)
        except:
            print("Пин ANEN_SPEED неопределен или недоступен!\n")
            exit(1)
        jft.DriveHigh(self.pin_reset)
        time.Wait_Time(100000)
        reg0 = self.mdio.Read(0x00) & 0x3000
        reg4 = self.mdio.Read(0x04) & 0x0180
        if pinValue:
            if reg0.__eq__(0x3000) and reg4.__eq__(0x0180):
                print("Скорость залочена на 100 Мб\с и включено автосогласование\n")
                return 0
            else:
                print("Микросхема не залочилась на желаемом режиме!\n")
                return 1
        else:
            if reg0.__eg__(0) and reg4.__eq__(0):
                print("Скорость залочена на 10 Мб\с и выключено автосогласование\n")
                return 0
            else:
                print("Микросхема не залочилась на желаемом режиме!\n")
                return 1

    def Check_SpeedModeSupport(self, speed=0, duplex=""):
        regValue = 0x0000
        modeReference = ""
        if duplex.__eq__("full"):
            regValue += 0x0100
            modeReference += "1"
        elif duplex.__eq__("half"):
            modeReference += "0"
        else:
            print("Неверное значение аргумента ''duplex''! Выберите ''half'' или ''full''\n")
            exit(1)
        if speed.__eq__(10):
            regValue += 0x0000
            modeReference += "01"
        elif speed.__eq__(100):
            regValue += 0x2000
            modeReference += "10"
        else:
            print("Неверное значение аргумента ''speed''! Выберите 10 или 100\n")
            exit(1)
        self.mdio.Write(0x00, regValue)
        status = self.mdio.Read(0x1E)
        print(f"Линк {'встал' if status[7].__eq__('1') else 'не встал'}\n")
        if status[13:16].__eq__("000"):
            print("Микросхема в режиме автосогласования\n")
        elif status[13:16].__eq__("001"):
            print("Микросхема в режиме 10Base half-duplex\n")
        elif status[13:16].__eq__("010"):
            print("Микросхема в режиме 100Base half-duplex\n")
        elif status[13:16].__eq__("101"):
            print("Микросхема в режиме 10Base full-duplex\n")
        elif status[13:16].__eq__("110"):
            print("Микросхема в режиме 100Base full-duplex\n")
        else:
            print("Микросхема в неизвестном режиме\n")
            return 1
        if modeReference.__ne__(status[13:16]):
            return 1
        return 0


    def Check_RefClock(self):
        try:
            jft.GetVar(self.pin_ref_clk)
        except:
            print("Пин REF_CLK неопределен или недоступен!\n")
            exit(1)
        tickCount = 500
        tickDifference = 0
        while tickCount.__gt__(0):
            tickCount -= 1
            tickDifference += 1 if jft.GetVar(self.pin_ref_clk) else -1
        if abs(tickDifference).__le__(250):
            return 0
        else:
            return 1


    def Check_Cable(self, pair = ""):
        if pair.__ne__("A") or pair.__ne__("B"):
            print("Неверный аргумент! Выберите 'А' или 'В'\n")
            exit(1)
        self.mdio.Write(0x1F, 0x2100) if pair.__eq__("A") else self.mdio.Write(0x1F, 0x6100)
        timeOut = 5
        status = "1"
        self.mdio.Write(0x1D, 0x8000)
        while status[0].__eq__("1") and timeOut.__gt__(0):
            status = self.mdio.Read(0x1D)
            timeOut -= 1
        if timeOut.__ne__(0):
            if status[1:3].__eq__("00"):
                print(f"Пара {pair} в хорошем состоянии")
                return 0
            elif status[1:3].__eq__("01"):
                print(f"В паре {pair} обнаружен разрыв!")
                return 1
            elif status[1:3].__eq__("10"):
                print(f"В паре {pair} обнаружено короткое замыкание!")
                return 1
            else:
                print(f"Проверка пары {pair} не удалась")
                return 1
