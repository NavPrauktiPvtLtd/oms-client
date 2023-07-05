# first delete the log file
cd "$(dirname "$0")/../logs"

sudo truncate -s 0 cron.log
sudo truncate -s 0 out.log
sudo truncate -s 0 err.log

echo "Log files cleared"

