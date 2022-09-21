from ctypes import util
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth 
import ctypes
from os import _exit

class SpotifyControls:
    scope = "playlist-modify-private playlist-modify-public user-library-read user-read-playback-state"
    def __create_spotify(self, confi):
        try:
            auth_manager = SpotifyOAuth(scope=self.scope, username=confi['username'], redirect_uri="http://localhost:8888/callback", client_id=confi['clientid'], client_secret=confi['clientsecret'])
            spotify = spotipy.Spotify(auth_manager=auth_manager)
            return auth_manager, spotify
        except:
            ctypes.windll.user32.MessageBoxW(0,u"Error connecting to spotify. Please check your credientials in the config file and restart the program.",u"Error",0)
            _exit(1)
    def refresh_spotify(self):
        auth_manager, spotify = self.__create_spotify(self.confi)
        self.sp = spotify
        self.auth_manager = auth_manager
    def __init__(self, confi: dict):
        self.confi = confi
        # try:
        #     self.token = util.prompt_for_user_token(self.confi['username'],scope=self.scope, client_id = self.confi['clientid'], client_secret = self.confi['clientsecret'], redirect_uri="http://localhost:8888/callback")
        #     self.sp = spotipy.Spotify(auth=self.token)
        # except:
        #     ctypes.windll.user32.MessageBoxW(0,u"Error connecting to spotify. Please check your credientials in the config file and restart the program.",u"Error",0)
        #     _exit(1)
        self.auth_manager, self.sp = self.__create_spotify(confi=self.confi)

    def CurrentTrack(self) -> str:
        try:
            currenttrack = self.sp.current_user_playing_track()
            trackname = currenttrack['item']['name']
            trackartist = currenttrack['item']['artists'][0]['name']
        except:
            return "No song playing"
        s = trackartist + ": " + trackname
        if not s.isascii():
            i = 0
            for c in s:
                if ord(c) > 128:
                    s = list(s)
                    s[i] = '*'
                    s = ''.join(s)
                i += 1
        return s

    def __CheckPlaylist(self, playlistid):
        currenttrack = self.sp.current_user_playing_track()
        id = currenttrack['item']['id']
        try:
            results = self.sp.user_playlist_tracks(self.confi['username'],playlistid)
            tracks = results['items']
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            results = tracks
            for i in range(len(results)):
                if results[i]['track']['id'] == id:
                    return True
        except spotipy.SpotifyException as ex:
            ctypes.windll.user32.MessageBoxW(0,ex.msg,u"Error",0)
            return True
        except:
            ctypes.windll.user32.MessageBoxW(0,"Unknown Error in CheckPlaylist",u"Error",0)
            return True
        return False
    
    def AddTrack(self,playlist):
        if not self.__CheckPlaylist(playlist):
            track = self.sp.current_user_playing_track()
            trackid = []
            trackid.append(track['item']['id'])
            self.sp.playlist_add_items(playlist,trackid)
