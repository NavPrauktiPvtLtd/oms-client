# first delete the log file

sudo truncate -s 0 /home/pi/oms-client/logs/cron.log
sudo truncate -s 0 /home/pi/oms-client/logs/out.log
sudo truncate -s 0 /home/pi/oms-client/logs/err.log

echo "Log files cleared"

