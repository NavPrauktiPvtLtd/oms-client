## Install instruction

```bash
  cd scripts
  chmod +x install.sh
  sudo ./install.sh
```

## Scripts

- run.sh : To run the application
- install.sh : To install the application with autostart enabled
- update.sh : To check for update using github (gets added to cron job while installing )
- action.sh : script to do additional tasks while updating
- cron : scipt to add cron jobs
- delete-log : script to delete logs

## Notes

1. User account must be created as "pi"

- create cron jobs

  - _/30 _ \* \* \* /home/pi/oms-client/update.sh

- install unclutter to hide mouse cursor

  - sudo apt install unclutter

- add unclutter to autostart

  - path: /etc/xdg/lxsession/LXDE/autostart
  - @unclutter -idle 0

- git error fix
  - git config --global --add safe.directory /home/pi/oms-client

## Misc

- tail log file

```bash
  sudo tail -f /home/pi/oms-client/logs/err.log
  sudo tail -f /home/pi/oms-client/logs/out.log
```
