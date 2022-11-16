import mpv

class Player:
    def __init__(self):
        self.media_player = mpv.MPV()

    def play(self, playlist,loop):
        # self.media_player.fullscreen = True
        if loop:
            self.media_player.loop_playlist = True
        else:
            self.media_player.loop_playlist = False

        for i in playlist:
            if not i :
                continue
            self.media_player.playlist_append(i)
        self.media_player.playlist_pos = 0
        # self.media_player.wait_for_playback()
        
        return self.media_player
    
    def teminate(self):
        if self.media_player:
            self.media_player.stop()

# media_player = vlc.MediaListPlayer()
# player = vlc.Instance()
# media_list = player.media_list_new()
# media = player.media_new("CV1.mp4")
# media_list.add_media(media)
# media = player.media_new("CV2.mp4")
# media_list.add_media(media)
# media_player.set_media_list(media_list)
# media_player.play_item_at_index(0)
# time.sleep(5)


# class VLCMediaPlayer():
#     def __init__(self):
#         self.media_player = vlc.MediaListPlayer()
#         self.player = vlc.Instance()
        

#         # self.player.audio_output_set('alsa')

#     def set_asset(self, uri):
#         self.media_list = self.player.media_list_new()
#         media = self.player.media_new(uri)
#         self.media_list.add_media(media)
#         self.media_player.set_media_list(self.media_list)

#     def play(self):
#         self.media_player.play_item_at_index(0)

#     def stop(self):
#         self.player.stop()

#     def is_playing(self):
#         return self.player.get_state() in [vlc.State.Playing, vlc.State.Buffering, vlc.State.Opening]

# player = VLCMediaPlayer()

# player.set_asset("/home/binoy638/Documents/beach.mp4")


# player.play()


     