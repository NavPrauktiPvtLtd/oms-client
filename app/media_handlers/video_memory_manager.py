from utils import read_json_file, write_json_file, VIDEOS_DIR
import time
import os
from logger.logger import setup_applevel_logger

logger = setup_applevel_logger(__name__)


class VideoMemoryManager:
    def __init__(self, videos_playback_history_path, max_video_storage_size):
        self.playback_history_path = videos_playback_history_path
        self.max_storage_size = max_video_storage_size
        self.videos = self.get_videos_data()

    def get_videos_data(self):
        try:
            return read_json_file(self.playback_history_path)
        except Exception as e:
            logger.error(f"Error reading video playback history: {e}")
            return {}

    def insert_new_video(self, name, size):
        try:
            self.videos[name] = {
                "size": size,
                "last_played": time.time()
            }

            logger.debug(f"new video inserted: {name} - {size}")

            write_json_file(self.playback_history_path, self.videos)
        except Exception as e:
            logger.error(f"Error inserting new video: {e}")

    def get_total_disk_space_used(self):
        try:
            total_size = 0

            for video_data in self.videos.values():
                total_size += video_data['size']

            logger.debug(f"Total used space: {total_size}")

            return total_size
        except Exception as e:
            logger.error(f"Error calculating total disk space used: {e}")
            return 0

    def file_path(self, x): return os.path.join(VIDEOS_DIR, x)

    def is_enough_space(self, new_video_size):
        try:
            used_space = self.get_total_disk_space_used()
            available_space = self.max_storage_size - used_space

            return available_space >= new_video_size
        except Exception as e:
            logger.error(f"Error checking available space: {e}")
            return False

    def delete_video(self, name):
        try:
            video_path = self.file_path(name)
            logger.debug(f"deleted video with path: {video_path}")
            if os.path.exists(video_path):
                os.remove(video_path)
            write_json_file(self.playback_history_path, self.videos)
            logger.info(f"video deleted: {name}")
            self.videos.pop(name, None)
        except Exception as e:
            logger.error(f"Error deleting video: {e}")

    def find_least_recently_used_video(self):
        try:
            if not self.videos:
                logger.debug(
                    "No videos found -> find_least_recently_used_video()")
                return None

            sorted_videos = dict(
                sorted(self.videos.items(), key=lambda x: x[1]['last_played']))

            least_recently_video_name = list(sorted_videos.keys())[0]

            try:
                video_data = sorted_videos[least_recently_video_name]
                return {
                    "name": least_recently_video_name,
                    "size": video_data["size"],
                    "last_played": video_data["last_played"]
                }
            except Exception as e:
                logger.error(e)
                return None
        except Exception as e:
            logger.error(f"Error deleting video: {e}")

    def make_space(self, size):
        try:
            logger.info("Creating space for new video.")
            used_space = self.get_total_disk_space_used()
            available_space = self.max_storage_size - used_space
            count = 0
            logger.debug(
                f"used_space: {used_space}  available_space: {available_space}  size: {size}")
            while available_space < size:
                video = self.find_least_recently_used_video()
                logger.debug(f"least recently played video: {str(video)}")
                if video:
                    self.delete_video(video["name"])
                    used_space = self.get_total_disk_space_used()
                    available_space = self.max_storage_size - used_space
                    count += 1
                else:
                    break

            if count > 0:
                logger.info(f"{count} videos deleted")
            else:
                logger.info(f"no deletion required")
        except Exception as e:
            logger.error(e)

    def update_last_played(self, name):
        try:
            video = self.videos[name]
            if video:
                updated_video = {
                    "size": video["size"],
                    "last_played": time.time()
                }
                self.videos[name] = updated_video
                write_json_file(self.playback_history_path, self.videos)
        except Exception as e:
            logger.error(e)

    def clear_all_videos(self):
        try:
            for video in self.videos.keys():
                self.delete_video(video)
        except Exception as e:
            logger.error(e)
