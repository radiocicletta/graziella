#!/usr/bin/env python
#
#
# regia automatica

import datetime
import socket
import shutil
import os
import sys
import re
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent, IN_CREATE, IN_MOVED_TO, IN_CLOSE_WRITE, IN_DELETE
from threading import Thread, Condition
from time import sleep

AUTODIR = "/media/archivio/automatico"
AUTOSHAREDIR = "/media/archivio/.dropbox/automatici"
timedict = {}
lock = Condition()
pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}.*")

class Dropboxer(ProcessEvent):
   def process_IN_MOVED_TO(self, event):
      self.process_event(event)

   def process_IN_CLOSE_WRITE(self, event):
      self.process_event(event)

   def process_event(self, event):
      if pattern.match(event.name):
         lock.acquire()
         try:
            print "moving %s" % event.name
            shutil.move("%s/%s" % (event.path, event.name), AUTODIR)
            if datetime.datetime.strptime(event.name[:16], "%Y-%m-%d_%H-%M") >= datetime.datetime.now():
               timedict[event.name[:16]] = "%s/%s" % (AUTODIR, event.name)
            print "New:", timedict
         except Exception, e:
            print e
            #pass
         finally:
            lock.release()


class Autodir(ProcessEvent):

   def process_IN_DELETE(self, event):
      if pattern.match(event.name):
         if timedict.has_key(event.name[:16]):
            print "delete", event.name
            lock.acquire()
            del timedict[event.name[:16]]
            lock.release()

   def process_IN_CLOSE_WRITE(self, event):
      if pattern.match(event.name):
         if not timedict.has_key(event.name[:16]):
            print "add", event.name
            lock.acquire()
            if datetime.datetime.strptime(event.name[:16], "%Y-%m-%d_%H-%M") >= datetime.datetime.now():
               timedict[event.name[:16]] = "%s/%s" % (AUTODIR, event.name)
            lock.release()
               

class Pusher(Thread):

   def __init__(self, remote):

      Thread.__init__(self)
      self.remote = remote
      self.runnable = True
      self.date = None

   def run(self):

      while self.runnable:
         self.date = datetime.datetime.now()
         sleep(60 - self.date.second)
         lock.acquire()
         try:
            i = self.date.strftime("%Y-%m-%d_%H-%M")
            print "Tick", i, timedict
            if timedict.has_key(i):
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               sock.connect((self.remote, 1234))
               sock.send("request.push %s\n" % timedict[i])
               print sock.recv(1024)
               sock.close()
               del timedict[i]
         except Exception, e:
            print e
            #pass
         finally:
            lock.release()

   def stop(self):
      self.runnable = False

def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):

   try: 
      pid = os.fork() 
      if pid > 0:
          sys.exit(0)   # Exit first parent.
   except OSError, e: 
      sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
      sys.exit(1)

   os.chdir("/") 
   os.umask(0) 
   os.setsid() 

   try: 
      pid = os.fork() 
      if pid > 0:
          sys.exit(0)   # Exit second parent.
   except OSError, e: 
      sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
      sys.exit(1)

   
   # Redirect standard file descriptors.
   si = open(stdin, 'r')
   so = open(stdout, 'a+')
   se = open(stderr, 'a+', 0)
   os.dup2(si.fileno(), sys.stdin.fileno())
   os.dup2(so.fileno(), sys.stdout.fileno())
   os.dup2(se.fileno(), sys.stderr.fileno())

def main():

   # 1. controlla che nessuno abbia inserito nuovi file (eventuali sono spostati)
   for i in os.listdir(AUTOSHAREDIR):
      if pattern.match(i):
         if os.path.exists("%s/%s" % (AUTODIR, i)) :
            os.unlink("%s/%s" % (AUTODIR, i))
         shutil.move("%s/%s" % (AUTOSHAREDIR, i), AUTODIR)
   # 2. carica la lista di esecuzione automatica
   now = datetime.datetime.now()
   for i in os.listdir(AUTODIR):
      if pattern.match(i) and datetime.datetime.strptime(i[:16], "%Y-%m-%d_%H-%M") >= now:
         timedict[i[:16]] = "%s/%s" % (AUTODIR, i)

   # 3. crea e avvia il thread Pusher
   pusher = Pusher("localhost")
   pusher.start()

   # crea e avvia il ThreadedNotifier
   wm_drop = WatchManager()
   dropboxmask = IN_MOVED_TO
   notifier_drop = ThreadedNotifier(wm_drop, Dropboxer())
   notifier_drop.start()

   wm_auto = WatchManager()
   autodirmask = IN_CLOSE_WRITE | IN_DELETE
   notifier_auto = ThreadedNotifier(wm_auto, Autodir())
   notifier_auto.start()

   wdd_dropbox = wm_drop.add_watch(AUTOSHAREDIR, dropboxmask, rec=True)
   wdd_autodir = wm_auto.add_watch(AUTODIR, autodirmask, rec=True)

   
if __name__ == "__main__":

   daemonize('/dev/null','/tmp/auto.log','/tmp/auto.log')
   main()
