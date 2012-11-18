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
import time
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

@dependency  util-linux::uuidgen
'''
class SysRSS:
    '''
    Mane method and constructor
    '''
    def __init__(self):
        self.root = os.getenv('HOME') + '/.sysrss/'
        self.sysinit()
        if not self.initSites():
            exit(255)
        if len(self.sites) == 0:
            print('There are no sites, update %s.' % (self.root + 'sites'))
            exit(254)
        
        proper = []
        for site in self.sites:
            site.interval = int(site.interval)
            if site.interval <= 0:
                print('Site %s does not have a positive interval and will therefore only be checked right now.' % site.name)
            else:
                proper.append(site)
            message = site()
            if (message is not None) and (len(message) > 0):
                self.publish(site.name, message)
        self.sites = proper
        
        while True:
            next = min(self.sites, key = lambda site : site.next).next
            for site in self.sites:
                if next > 0:
                    time.sleep(next * 60)
                if site.next == next:
                    message = site()
                    if (message is not None) and (len(message) > 0):
                        self.publish(site.name, message)
                    site.next = site.interval
                else:
                    site.next -= next
    
    
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
            printf('Created rss file, %s, your should set you news feed aggregator to syndicate this file.\n', self.root + 'maintenance.rss')
            flush()
            self.pubdate = date
            self.publish('Welcome to SysRSS', 'This is going to be so awesome! 😄 \n\nEx animo\nSysRSS\n\n')
        else:
            data = None
            with open(self.root + 'maintenance.rss', 'rb') as file:
                data = file.read()
            data = data.decode('utf8', 'replace')
            data = data[data.find('<pubDate>') + len('<pubDate>'):]
            data = data[:data.find('</')]
            self.pubdate = data
    
    
    '''
    Initialise site list
    
    @return  :boolean  Whether the program can continue
    '''
    def initSites(self):
        self.sites = []
        sites = self.sites
        sitefile = self.root + 'sites'
        if os.path.exists(sitefile):
            with open(sitefile, 'rb') as file:
                code = file.read().decode('utf8', 'replace') + '\n'
                code = compile(code, sitefile, 'exec')
                exec(code)
        else:
            with open(sitefile, 'wb') as file:
                file.write('# -*- mode: python, coding: utf-8  -*-\n'.encode('utf-8'))
                file.write('\n'.encode('utf-8'))
                file.write('# self.sites (alternatively sites) is a list that you\n'.encode('utf-8'))
                file.write('# should fill with Site:s, a site descripts a subsystem\n'.encode('utf-8'))
                file.write('# that generates updates. Site\'s constructor takes 3\n'.encode('utf-8'))
                file.write('# arguments: name, interval, implementation. The first\n'.encode('utf-8'))
                file.write('# `name` is the name of the subsystme, it is displayed\n'.encode('utf-8'))
                file.write('# as the title on all updates. `interval` is the number\n'.encode('utf-8'))
                file.write('# is minutes between update checks. `implementation` is\n'.encode('utf-8'))
                file.write('# function or functor that returns an update message,\n'.encode('utf-8'))
                file.write('# or an empty string if there are no updates.\n'.encode('utf-8'))
                file.write('\n'.encode('utf-8'))
                file.flush()
            printf('Created site file, %s, you should fill it in and then restart this program.\n', sitefile)
            flush()
            return False
        return True
    
    
    '''
    Publish a news item to the RSS
    
    @param  system:str   The subsystem that generated the message
    @param  message:str  Message to display
    '''
    def publish(self, system, message):
        date = self.getTime()
        addendum = self.makeNews(system, message).encode('utf-8')
        
        with open(self.root + 'log', 'ab') as file:
            file.write(addendum)
            file.flush()
        printf('The feed log as been updated with %s.\n', system)
        
        with open(self.root + 'tmp', 'wb') as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
            file.write('<rss version="2.0">\n'.encode('utf-8'))
            file.write('  <channel>\n'.encode('utf-8'))
            file.write('    <title>SysRSS</title>\n'.encode('utf-8'))
            file.write('    <description>System maintenance notification RSS</description>\n'.encode('utf-8'))
            file.write('    <link>http://localhost/</link>\n'.encode('utf-8'))
            file.write(('    <lastBuildDate>%s</lastBuildDate>\n' % date).encode('utf-8'))
            file.write(('    <pubDate>%s</pubDate>\n\n' % self.pubdate).encode('utf-8'))
            with open(self.root + 'log', 'rb') as logfile:
                file.write(logfile.read())
            file.write('  </channel>\n'.encode('utf-8'))
            file.write('</rss>\n'.encode('utf-8'))
            file.write('\n'.encode('utf-8'))
            file.flush()
        Popen(['mv', self.root + 'tmp', self.root + 'maintenance.rss']).wait()
        printf('The feed as been updated with %s.\n', system)
    
    
    '''
    Generate RSS item
    
    @param   system:str   The subsystem that generated the message
    @param   message:str  Message to display
    @return  :str         RSS item
    '''
    def makeNews(self, system, message):
        def makeUglyButReadable(data):
            data = data.replace(']]>', ']]]]><![CDATA[>')
            data = data.replace('\n', '<br>') # [sic!]
            return '<![CDATA[' + data + ']]>'
        return('<item>\n  <title>%s</title>\n  <guid>%s</guid>\n  <pubDate>%s</pubDate>\n  <description>%s</description>\n</item>\n\n' %
               (makeUglyButReadable(system), self.generateUUID(), self.getTime(), makeUglyButReadable(message)))
    
    
    '''
    Generate an UUID
    
    @return  An UUID
    '''
    def generateUUID(self):
        uuid = Popen(['uuidgen'], stdout=PIPE).communicate()[0].decode('utf-8', 'replace')
        if uuid[-1] == '\n':
            uuid = uuid[:-1]
        return uuid
    
    
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
Subsystem definition class
'''
class Site:
    '''
    Constructor
    
    @param  name                   System name
    @param  interval:int           Generation interval in minutes
    @param  implementation:()→str  Publish message generator, empty string is ignored
    '''
    def __init__(self, name, interval, implementation):
        self.name = name
        self.interval = interval
        self.implementation = implementation
        self.next = interval
    
    
    
    '''
    Invocation method
    
    @return  :str  Message to publish
    '''
    def __call__(self):
        return self.implementation()



'''
Execute mane method if started using this file
'''
if __name__ == '__main__':
    SysRSS()

