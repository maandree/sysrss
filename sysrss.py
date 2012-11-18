#!/usr/bin/env python3
# -*- mode: python, coding: utf-8  -*-
'''
sysrss – Let your system generate a maintenance notification RSS

Copyright © 2012  Mattias Andrée (maandree@kth.se)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import datetime
from subprocess import Popen, PIPE



'''
Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in
programs by default, report them to Princess Celestia so she can banish them to the moon)

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def print(text = '', end = '\n'):
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))
    sys.stdout.buffer.flush()

'''
stderr equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printerr(text = '', end = '\n'):
    sys.stderr.buffer.write((str(text) + end).encode('utf-8'))
    sys.stderr.buffer.flush()

'''
Link {@link #print}, only better because this does not take a text ending
but takes a format and parameters

@param  master:str  Formated string
@param  slave:str*  Parameters for the formated string
'''
def printf(master, *slave):
    sys.stdout.buffer.write((master % slave).encode('utf-8'))

'''
Flush stdout
'''
def flush():
    sys.stdout.buffer.flush()



'''
Mane class
'''
class SysRSS:
    '''
    Mane method and constructor
    '''
    def __init__(self):
        self.root = os.getenv('HOME') + '/.sysrss/'
        self.sysinit()
    
    
    '''
    Initialise the system
    '''
    def sysinit(self):
        if not os.path.isdir(self.root):
            os.mkdir(self.root)
            printf('Created root directory, %s.\n', self.root)
        
        if not os.path.isfile(self.root + 'log'):
            with open(self.root + 'log', 'wb') as file:
                file.flush()
            printf('Created log file, %s, it contains ever thing that have ever happend, ever.\n', self.root + 'log')
            flush()
        
        if not os.path.isfile(self.root + 'maintenance.rss'):
            date = self.getTime()
            with open(self.root + 'maintenance.rss', 'wb') as file:
                file.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
                file.write('<rss version="2.0">\n'.encode('utf-8'))
                file.write('  <channel>\n'.encode('utf-8'))
                file.write('    <title>SysRSS</title>\n'.encode('utf-8'))
                file.write('    <description>System maintenance notification RSS</description>\n'.encode('utf-8'))
                file.write('    <link>http://localhost/</link>\n'.encode('utf-8'))
                file.write(('    <lastBuildDate>%s</lastBuildDate>\n' % date).encode('utf-8'))
                file.write(('    <pubDate>%s</pubDate>\n' % date).encode('utf-8'))
                file.write('    <ttl>1800</ttl>\n'.encode('utf-8'))
                file.write('\n'.encode('utf-8'))
                file.write('  </channel>\n'.encode('utf-8'))
                file.write('</rss>\n'.encode('utf-8'))
                file.write('\n'.encode('utf-8'))
                file.flush()
            printf('Created rss file %s, your should set you news feed aggregator to syndicate this file.\n', self.root + 'maintenance.rss')
            flush()
    
    
    '''
    Get a locale independent time stamp in RSS's [poor] format
    
    @return  :str  The current time
    '''
    def getTime(self):
        time = datetime.datetime.utcnow().strftime('(%w), %d [%m] %Y %H:%M:%S +0000')
        
        time = time.replace('(1)', 'Mon')
        time = time.replace('(2)', 'Tue')
        time = time.replace('(3)', 'Wed')
        time = time.replace('(4)', 'Thu')
        time = time.replace('(5)', 'Fri')
        time = time.replace('(6)', 'Sat')
        time = time.replace('(0)', 'Sun') # [sic!]
        
        time = time.replace('[01]', 'Jan')
        time = time.replace('[02]', 'Feb')
        time = time.replace('[03]', 'Mar')
        time = time.replace('[04]', 'Apr')
        time = time.replace('[05]', 'May')
        time = time.replace('[06]', 'Jun')
        time = time.replace('[07]', 'Jul')
        time = time.replace('[08]', 'Aug')
        time = time.replace('[09]', 'Sep')
        time = time.replace('[10]', 'Oct')
        time = time.replace('[11]', 'Nov')
        time = time.replace('[12]', 'Dec')
        
        return time



'''
Execute mane method if started using this file
'''
if __name__ == '__main__':
    SysRSS()

