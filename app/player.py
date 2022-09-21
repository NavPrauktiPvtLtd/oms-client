import mpv


class Player:

    def play(self, playlist):
        
        media_player = mpv.MPV()

        # media_player.fullscreen = True
        media_player.loop_playlist = True

        for i in playlist:
            if not i :
                continue
            media_player.playlist_append(i)

        media_player.playlist_pos = 0
        # media_player.wait_for_playback()

        return media_player