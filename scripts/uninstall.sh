sudo supervisorctl stop oms_client
sudo rm /etc/supervisor/conf.d/oms_client.conf
sudo supervisorctl reread
sudo supervisorctl remove oms_client
sudo crontab -r 