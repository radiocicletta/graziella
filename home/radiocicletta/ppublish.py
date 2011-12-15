#!/usr/bin/env python
#
#
# podcast publisher

import datetime
import re
import shutil
import os
import sys

AUTOSHAREDIR = "/media/archivio/.dropbox/podcast"

if __name__ == "__main__":

   if not sys.argv:
      path = "."
   else:
      path = sys.argv[1]

   if not os.path.isdir(path):
      sys.exit(0)

   today = datetime.date.today()
   pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}.*mp[34]")

   # 1. rimuovi il link ai podcast piu' vecchi di tre giorni
   for i in os.listdir(AUTOSHAREDIR):
      if pattern.match(i):
         datefile = datetime.datetime.strptime(i[:10], "%Y-%m-%d").date()
         if (today - datefile).days > 3:
            os.unlink("%s/%s" % (AUTOSHAREDIR, i))

   # 2. link simbolico ai podcast non piu' vecchi di tre giorni
   for i in os.listdir(path):
      if pattern.match(i):
         datefile = datetime.datetime.strptime(i[:10], "%Y-%m-%d").date()
         if (today - datefile).days <= 3 and not os.path.exists("%s/%s" % (AUTOSHAREDIR, i)):
            os.symlink("%s/%s" % (path, i), "%s/%s" % (AUTOSHAREDIR, i))
