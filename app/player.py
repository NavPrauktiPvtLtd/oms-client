# import mpv

# class Player:
#     def __init__(self):
#         self.media_player = mpv.MPV()

#     def play(self, playlist,loop):
#         # self.media_player.fullscreen = True
#         if loop:
#             self.media_player.loop_playlist = True
#         else:
#             self.media_player.loop_playlist = False

#         for i in playlist:
#             if not i :
#                 continue
#             self.media_player.playlist_append(i)
#         self.media_player.playlist_pos = 0
    
#     def teminate(self):
#         if self.media_player:
#             self.media_player.stop()


import vlc
import time
from threading import Thread


class Player:
    def __init__(self,):
        self.media_player = vlc.MediaListPlayer(vlc.Instance("--play-and-exit"))
        self.player =self.media_player.get_instance()
        _player = self.media_player.get_media_player()
        _player.set_fullscreen(True)

    def play(self,playlist:list,loop:bool):
        self.terminate()
        media_list = self.player.media_list_new()

        for item in playlist:
            print(item)
            list_item = self.player.media_new(item)
            media_list.add_media(list_item)

        self.media_player.set_media_list(media_list)

        if loop:
            self.media_player.set_playback_mode(vlc.PlaybackMode.loop)
        self.media_player.play()

        def cb(event):
            print('inside cb')
            self.media_player.stop()

        event_manager = self.media_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaListPlayerStopped, cb)

    def terminate(self):
        try:
            self.media_player.stop()
        except Exception as e:
            print(e)






     