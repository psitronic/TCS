"""!/usr/bin/python
Created on Tue Jul 25 08:17:18 2017
by A.A. Sidorenko aka spintronic

Class and functions to control a triple current source from Leiden Cryogenics

It is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with triple_CS.py. If not, see <http://www.gnu.org/licenses/>.

"""

import serial, time

### Special characters: command end or command separators    
SPECIAL_CHARACTERS = { 
  'CR':  "\x0D", # Carriage Return
  'LF':  "\x0A", # Line Feed
  'HT': "\x09", # Command Separator
  'SPACE': "\x20", # Empty Character Place
}

LINE_TERMINATION = SPECIAL_CHARACTERS['LF']

SYMBOL_ON_OFF = {
   'ON': "1",
   'OFF': "0",
   'on': "1",
   'off': "0",
   '1': "1",
   '0': "0",
}

class TripleCS(object):
    def __init__(self, serialPort, baud=9600, debug=False):
        self.debug=debug
        try:
            self.connection = serial.Serial(port=serialPort, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=1)
        except serial.serialutil.SerialException as se:
            raise se
            exit()
#        try:
#            self.connection.open()
#        except Exception, e:
#            print "error open serial port: " + str(e)
#            exit()
            
        if self.connection.isOpen():
            try:
                self.connection.flushInput() #flush input buffer, discarding all its contents
                self.connection.flushOutput()#flush output buffer, aborting current output
                
                self.connection.write("ID?"+LINE_TERMINATION)
                ID_str = self.connection.readline().split(SPECIAL_CHARACTERS['HT'])[1]
                print("Triple CS connected: ID - %s" % str(ID_str))
                time.sleep(0.5)
                
            except Exception as e:
                print("error communicating...: %s" % str(e))

        self.logfilename = ''
        
    def setSorb(self, current):
        """
        set Sorb current in uA
        """
        self.connection.write("SETDAC 1 0 " + str(current)+LINE_TERMINATION)
        status = self.connection.readline()

    def setStill(self, current):
        """
        set Still current in uA
        """
        self.connection.write("SETDAC 2 0 " + str(current)+LINE_TERMINATION)
        status = self.connection.readline()

    def setMixingChamber(self, current):
        """
        set Mixing Chamber current in uA
        """
        self.connection.write("SETDAC 3 0 " + str(current)+LINE_TERMINATION)
        status = self.connection.readline()

        
    def toggle(self,sorb,still,mc):
        """
        """
        sorb_str = SYMBOL_ON_OFF[str(sorb)]
        still_str = SYMBOL_ON_OFF[str(still)]
        mc_str = SYMBOL_ON_OFF[str(mc)]
        
        self.connection.write('SETUP 0,0,'+sorb_str+',0,0,0,'+still_str+',0,0,0,'+mc_str+',0'+LINE_TERMINATION)
        status = self.connection.readline()
        self.check_status()
        
        
    def sorb(self,sorb='OFF'):
        sorb_str = SYMBOL_ON_OFF[str(sorb)]
        sorb_status = self.check_status()[0]
        if sorb_status != sorb_str:
            self.connection.write('SETUP 0,0,1,0,0,0,0,0,0,0,0,0' + LINE_TERMINATION)
            status = self.connection.readline()

    def still(self,still='OFF'):
        still_str = SYMBOL_ON_OFF[str(still)]
        still_status = self.check_status()[1]
        if still_status != still_str:
            self.connection.write('SETUP 0,0,0,0,0,0,1,0,0,0,0,0' + LINE_TERMINATION)
            status = self.connection.readline()

    def mixingchamber(self,mc='OFF'):
        mc_str = SYMBOL_ON_OFF[str(mc)]
        mc_status = self.check_status()[2]
        if mc_status != mc_str:
            self.connection.write('SETUP 0,0,0,0,0,0,0,0,0,0,1,0' + LINE_TERMINATION)
            status = self.connection.readline()

    def check_status(self):
        self.connection.write('STATUS?' + LINE_TERMINATION)
        status_all = self.connection.readline().split(SPECIAL_CHARACTERS['HT'])[1]
        status = status_all.split(',')
        cs_status = status[0]
        sorb_status = status[3]
        still_status = status[7]
        mc_status = status[11]
        return sorb_status, still_status, mc_status
    
    def close(self):
        self.connection.close()    
        
    def __del__(self):
        self.close()


dilution = TripleCS('COM7')

dilution.setSorb(80000) # set Sorb current in uA
dilution.setStill(000) #  set Still current in uA
dilution.setMixingChamber(0) #  set Mixing Chamber current in uA

dilution.sorb('on')
dilution.still('on')
dilution.mixingchamber('on')

#dilution.toggle(sorb = '0', still = '0', mc = '0') # current toggle on/off
dilution.close()
