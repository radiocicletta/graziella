
nz_clock = timer({ timeout = 1 })
nz_notification = widget({ type = "textbox", align = "right", visible = true })
nz_countdown = -1 

local colors =  {"#FFFFFF", "#FF0000", "#00FF00", "#0000FF"}

nz_clock:add_signal("timeout", function()
   local minutes = io.popen("date -u +%M")
   if nz_countdown > 0 then
      local nz_min = math.floor(nz_countdown / 60)
      local nz_secs = nz_countdown % 60
      if nz_min > 0 then
         nz_notification.visible = true
         nz_notification.text = "<span color='".. colors[nz_notifications % 4] .."'><b>".. nz_min .."min, ".. nz_secs .." secondi alla disconnessione</b></span>"
         if nz_secs == 0 then
            naughty.notify({ title = "<span color=\'orange\'>Disconnessione</span>", text = "<b>Disconnessione dal server nei prossimi ".. nz_countdown .." secondi</b>", timeout = 30 })
         end
      else
         nz_notification.text = "<span color='".. colors[nz_notifications % 4] .."'><b>".. nz_secs .." secondi alla disconnessione</b></span>"
      end
      nz_countdown = nz_countdown - 1
   end
   if nz_countdown == 0 then
      io.popen("idjcctrl --disconnect")
      io.popen("idjcctrl --record_stop")
      nz_notification.visible = false 
      nz_countdown = nz_countdown - 1
   end
   if nz_countdown == -1 then
      nz_notification.text = "In trasmissione. " -- .. minutes:lines()
   end
end)

nz_clock:start()
