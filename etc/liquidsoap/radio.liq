#!/usr/bin/liquidsoap

#message =
#  "Radiocicletta! Web Radio" 

set("harbor.bind_addr", "0.0.0.0")
set("harbor.port", 8002)
set("harbor.password", "")
set("server.telnet",true)

# Then we setup our icecast output function.
# Possible options and values are bitrate=64, samplerate=11025, ...
def output.icecast.lame(
  ~id="output.icecast.lame",~start=true,
  ~restart=false,~restart_delay=3,
  ~host="localhost",~port=8000,
  ~user="source",~password="hackme",
  ~genre="Misc",~url="http://savonet.sf.net/",
  ~description="OCaml Radio!",~public=true,
  ~dumpfile="",~mount="Use [name]",
  ~name="Use [mount]",~protocol="http",
  ~lame="lame",~bitrate=128,~swap=false,
  ~fallible=false,~on_start={()},~on_stop={()},
  ~restart_on_crash=false,~restart_on_new_track=false,
  ~restart_encoder_delay=3600,~headers=[],s)
  output.icecast(%external(channels=2,
    samplerate=44100,
    header=true,
    process="/usr/bin/lame --vbr-new -b 128 --silent --flush -r --bitwidth 16 --signed -m j -q=1 -t - - "
    ),format="audio/mpeg",
    id=id,
    restart=restart,restart_delay=restart_delay,
    host=host,port=port,user=user,password=password,
    genre=genre,url=url,description=description,
    public=public,dumpfile=dumpfile,    name=name,mount=mount,protocol=protocol,
    fallible=fallible,on_start=on_start,on_stop=on_stop,
    s)

end

def aacenc(_) = "aacplusenc - - 94 48000" end
def neroaacenc(_) = "/tmp/linux/neroAacEnc -lc -ignorelength -if - -of /dev/stdout" end
def fapg() = "fapg -f m3u /media/archivio/lastfm" end

def cfade(a, b)
  add(normalize = true, [ fade.initial(duration = 1., b),
			   fade.final(duration = 1., a) ])
end


#jingles metadata
def jingles_meta(j) 
   rewrite_metadata([("artist", "Radiocicletta"),
                     ("title", "Jingle 4 you <3!"),
                     ("comment", "http://www.radiocicletta.it")], j)
end

freelastfm = nrj(smart_crossfade(skip_blank(playlist(mode="random", reload=18000, "/media/archivio/playlists/lastfm.m3u")))) #ogni cinque ore
netlabels = nrj(smart_crossfade(skip_blank(playlist(mode="random", reload=18000,"/media/archivio/playlists/netlabels.m3u")))) #ogni cinque ore
jingles = nrj(skip_blank(jingles_meta(playlist(reload=86400, "/media/archivio/playlists/jingles.m3u")))) #ogni 24 ore
esterni = nrj(input.harbor("live", port=8002, password="mipuzzanoipiedi23"))
pushed = nrj(request.queue(id="request"))

dawn =      nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/dawn.m3u"     , mode="normal", conservative=true)))
morning =   nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/morning.m3u"  , mode="normal", conservative=true)))
noon =      nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/noon.m3u"     , mode="normal", conservative=true)))
afternoon = nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/afternoon.m3u", mode="normal", conservative=true)))
dusk =      nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/dusk.m3u"     , mode="normal", conservative=true)))
night =     nrj(smart_crossfade(playlist(reload=18000, "/media/archivio/playlists/night.m3u"    , mode="normal", conservative=true)))

smart = switch([
                ({5h-8h}, dawn),
                ({8h-12h}, morning),
                ({12h-14h}, noon),
                ({14h-18h}, afternoon),
                ({18h-20h}, dusk),
                ({20h-3h}, night)
               ])

radio = fallback(track_sensitive = false, 
                 transitions = [cfade, cfade, cfade, cfade],
                 [  esterni,
                    pushed,
                    smart,
                    random(weights = [1,10,50], [jingles, freelastfm, netlabels])])

out = output.icecast.lame( host = "213.92.118.70", #,
                    port = 8000,
                    password = "",
                    mount = "studio",
                    description = "Radiocicletta!",
                    url = "http://www.radiocicletta.it",
                    name = "Radiocicletta!",
                    bitrate = 128,
                    restart = true,
                    restart_delay = 10,
                    restart_on_crash = true,
                    restart_on_new_track = true,
                    radio, 
                    fallible = true)
