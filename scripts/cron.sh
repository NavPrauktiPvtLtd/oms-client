# cron job to run update script

script_dir=/home/pi/oms-client/scripts

log_dir=/home/pi/oms-client/scripts/logs

chmod +x "/home/pi/oms-client/update.sh"

# this will run every 30 minutes
(sudo crontab -l | grep -v update.sh ; echo "*/30 * * * * /home/pi/oms-client/update.sh >> /home/pi/oms-client/logs/cron.log 2>&1") | crontab -

# cron job to delete log files

chmod +x "/home/pi/oms-client/scripts/delete-log.sh"

# this will run every month
(sudo crontab -l | grep -v delete-log ; echo "0 0 1 * * /home/pi/oms-client/scripts/delete-log.sh >> /home/pi/oms-client/logs/cron.log 2>&1") | crontab -