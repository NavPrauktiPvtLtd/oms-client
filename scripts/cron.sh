# cron job to run update script

script_dir=/home/pi/oms-client/scripts

log_dir=/home/pi/oms-client/scripts/logs

chmod +x "/home/pi/oms-client/update.sh"

# this will run every 30 minutes
(crontab -l | grep -v update.sh ; echo "*/30 * * * * /home/pi/oms-client/update.sh >> ${log_dir}/cron.log 2>&1") | crontab -

# cron job to delete log files

chmod +x "${script_dir}/delete-log.sh"

# this will run every month
(crontab -l | grep -v delete-log ; echo "0 0 1 * * ${script_dir}/delete-log.sh >> ${log_dir}/cron.log 2>&1") | crontab -