mport machine
import time
from struct import unpack as unp
from math import atan2, degrees, pi

class MPU6050():
    '''
    Module for the MPY6050 6DOF IMU.
    By default interrupts are disabled while reading or writing to the device. This
    prevents occasional bus lockups in the presence of pin interrupts, at the cost
    of disabling interrupts for about 250uS.
    '''

    mpu_addr = 0x68  # address of MPU6050
    _I2Cerror = "I2C communication failure"

    def __init__(self, disable_interrupts=False):
        # create i2c object
        self._timeout = 10
        self.disable_interrupts = disable_interrupts

        # configure SDA and SCL pins (fixed pins on Raspberry Pi Pico)
        self.sda_pin = machine.Pin(0)  # GPIO 0
        self.scl_pin = machine.Pin(1)  # GPIO 1
        self._mpu_i2c = machine.I2C(0, sda=self.sda_pin, scl=self.scl_pin)

        self.chip_id = int(unp('>h', self._read(2, 0x75, self.mpu_addr))[0])

        # now apply user setting for interrupts
        self.disable_interrupts = disable_interrupts

        # wake it up
        self.wake()
        self.accel_range(1)
        self._ar = self.accel_range()
        self.gyro_range(0)
        self._gr = self.gyro_range()



    # read from device
    def _read(self, count, memaddr, devaddr):
        irq_state = True
        if self.disable_interrupts:
            irq_state = machine.disable_irq()

        try:
            result = self._mpu_i2c.readfrom_mem(devaddr, memaddr, count)
        except OSError as e:
            print("Error reading from I2C:", e)
            result = b'\x00' * count  # Return zero-filled buffer in case of error

        machine.enable_irq(irq_state)
        return result


    # write to device
    def _write(self, data, memaddr, devaddr):
        '''
        Perform a memory write. Caller should trap OSError.
        '''
        irq_state = True
        if self.disable_interrupts:
            irq_state = machine.disable_irq()
        self._mpu_i2c.writeto_mem(devaddr, memaddr, bytes([data]))
        machine.enable_irq(irq_state)

    # wake
    def wake(self):
        '''
        Wakes the device.
        '''
        try:
            self._write(0x01, 0x6B, self.mpu_addr)
        except OSError:
            print(MPU6050._I2Cerror)
        return 'awake'

    # mode
    def sleep(self):
        '''
        Sets the device to sleep mode.
        '''
        try:
            self._write(0x40, 0x6B, self.mpu_addr)
        except OSError:
            print(MPU6050._I2Cerror)
        return 'asleep'

    # sample rate
    def sample_rate(self, rate=None):
        '''
        Returns the sample rate or sets it to the passed arg in Hz. Note that
        not all sample rates are possible. Check the return value to see which
        rate was actually set.
        '''

        gyro_rate = 8000  # Hz

        # set rate
        try:
            if rate is not None:
                rate_div = int(gyro_rate / rate - 1)
                if rate_div > 255:
                    rate_div = 255
                self._write(rate_div, 0x19, self.mpu_addr)

            # get rate
            rate = gyro_rate / (unp('<H', self._read(1, 0x19, self.mpu_addr))[0] + 1)
        except OSError:
            rate = None
        return rate

    # accelerometer range
    def accel_range(self, accel_range=None):
        '''
        Returns the accelerometer range or sets it to the passed arg.
        Pass:               0   1   2   3
        for range +/-:      2   4   8   16  g
        '''
        # set range
        try:
            if accel_range is None:
                pass
            else:
                ar = (0x00, 0x08, 0x10, 0x18)
                try:
                    self._write(ar[accel_range], 0x1C, self.mpu_addr)
                except IndexError:
                    print('accel_range can only be 0, 1, 2 or 3')
            # get range
            ari = int(unp('<H', self._read(2, 0x1C, self.mpu_addr))[0] / 8)
        except OSError:
            ari = None
        if ari is not None:
            self._ar = ari
        return ari

    # gyroscope range
    def gyro_range(self, gyro_range=None):
        '''
        Returns the gyroscope range or sets it to the passed arg.
        Pass:               0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        '''
        # set range
        try:
            if gyro_range is None:
                pass
            else:
                gr = (0x00, 0x08, 0x10, 0x18)
                try:
                    self._write(gr[gyro_range], 0x1B, self.mpu_addr)
                except IndexError:
                    print('gyro_range can only be 0, 1, 2 or 3')
            # get range
            gri = int(unp('<H', self._read(2, 0x1C, self.mpu_addr))[0] / 8)
        except OSError:
            gri = None

        if gri is not None:
            self._gr = gri
        return gri

    # get raw acceleration
    def get_accel_raw(self):
        '''
        Returns the accelerations on xyz in bytes.
        '''
        try:
            axyz = self._read(6, 0x3B, self.mpu_addr)
        except OSError:
            axyz = b'\x00\x00\x00\x00\x00\x00'
        return axyz

    # get acceleration
    def get_acc(self, xyz=None):
        '''
        Returns the accelerations on axis passed in arg. Pass xyz or every
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        scale = (16384, 8192, 4096, 2048)
        raw = self.get_accel_raw()
        axyz = {'x': unp('>h', raw[0:2])[0] / scale[self._ar],
                'y': unp('>h', raw[2:4])[0] / scale[self._ar],
                'z': unp('>h', raw[4:6])[0] / scale[self._ar]}

        aout = []
        for char in xyz:
            aout.append(axyz[char])
        return aout

    # get pitch
    def pitch(self):
        '''
        Returns pitch angle in degrees based on x and c accelerations.

        '''
        scale = (16384, 8192, 4096, 2048)
        raw = self.get_accel_raw()
        x = unp('>h', raw[0:2])[0] / scale[self._ar]
        z = unp('>h', raw[4:6])[0] / scale[self._ar]
        pitch = degrees(pi + atan2(-x, -z))
        if (pitch >= 180) and (pitch <= 360):
            pitch -= 360
        return -pitch

    # get raw gyro
    def get_gyro_raw(self):
        '''
        Returns the turn rate on xyz in bytes.
        '''
        try:
            gxyz = self._read(6, 0x43, self.mpu_addr)
        except OSError:
            gxyz = b'\x00\x00\x00\x00\x00\x00'
        return gxyz


    def get_gyro(self, xyz=None, use_radians=False):
        '''
        Returns the turn rate on the specified axis.

        Parameters:
        - xyz: String indicating the axis to retrieve (e.g., 'xyz' or 'yx').
           If None, defaults to 'xyz'.
        - use_radians: If True, returns angular velocity in radians per second.
                   If False, returns angular velocity in degrees per second.
        '''
        if xyz is None:
            xyz = 'xyz'

        if use_radians:
            scale = (7150, 3755, 1877.5, 938.75)
        else:
            scale = (131.0, 65.5, 32.8, 16.4)

        raw = self.get_gyro_raw()

        gyro_data = {
            'x': int.from_bytes(raw[0:2], 'big') / scale[self._gr],
            'y': int.from_bytes(raw[2:4], 'big') / scale[self._gr],
            'z': int.from_bytes(raw[4:6], 'big') / scale[self._gr]
        }

        return [gyro_data[char] for char in xyz]
 
    # get gyro pitch - y - axis in degrees
    def get_gy(self):
        scale = (131.0, 65.5, 32.8, 16.4)
        raw = self.get_gyro_raw()
        gy = unp('>h', raw[2:4])[0] / scale[self._gr]
        return gy
