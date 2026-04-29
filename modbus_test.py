# Copyright (c) 2025 Prodrive Technologies New Energies B.V.
# This code is licensed under MIT license (see LICENSE for details)

import sys
from peblar_modbusclient.modbus import Modbus
from peblar_modbusclient.registers import ModbusAddresses

if __name__ == "__main__":
    print("Reading/Writing all modbus registers...")
    modbus = Modbus(sys.argv[1])
    for address in ModbusAddresses:
        if address.value.decoder is not None:
            print(f"Read {address.name}: ", end="")
            try:
                print(modbus.read(address.value))
            except ValueError:
                print("Failure")

    # for address in ModbusAddresses:
    #     if address.value.encoder is not None:
    #         print(f"Write '1' to {address.name}: ", end="")
    #         try:
    #             modbus.write(address.value, 1)
    #             print("Success")
    #         except ValueError:
    #             print("Failure")