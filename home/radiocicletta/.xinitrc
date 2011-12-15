#!/bin/sh
source /etc/X11/Xsession
export ERRFILE=$HOME/.xsession-errors

export GTK2_RC_FILES=$HOME/.gtkrc-2.0
exec /usr/bin/awesome -c $HOME/.config/awesome/rc.lua 2>&1 >> $HOME/.xsession-errors
