# usmobile-lifeguard
Minds your USMobile pool so you don't have to

**WARNING!!! Use at your own risk!!!**

I've been using this script for a few months. It works for me.
That said, it uses undocumented APIs, and **makes purchases** for you.

**It can potentially run amok and purchase many gigabytes of data**. I built in a few safeguards but I make no promises.

**WARNING!!! Use at your own risk!!!**

# Installation
Still reading?

You've been warned.

Well ok then. Go ahead and clone this repo or just copy the config.yaml-template file and docker-compose.yaml file to a local directory.

1. Rename the config template file to config.yaml: `cp config.yaml-template config.yaml`
    1. Make an extra hard link to the config file: `ln config.yaml config.yaml-dont-move-me-vim`. You can ignore this link and it can be named whatever you want. It's just there to keep certain editors from changing the inode number when you edit the file.
    2. By the way, you can also configure any setting via an environment variable upper-cased & prefaced with `LIFEGUARD_`. Any setting specified in the environment will override the corresponding setting in the config file.
2. Invite a new user to your account that will only be used for scripting. It only needs `contributor` privileges. Do not enable 2FA for this user but do give it a really long complex password. Set the `username` and `password` fields in either config.yaml or your environment.
3. Edit the rest of the values in the file to suit your preferences. There are comments in there that should be self-explanatory.
4. To run the app, use the command: `docker compose up --build`.
5. Keep an eye on the output. If it does anything unexpected kill it and check your configuration.
6. It will give you a 10 second warning before performing a top up. That gives you a chance to kill it if you're watching.
7. The config file can be changed while the application is running. The changes take affect on the next cycle - no need to restart.
8. If you want to run the script on a cron schedule or some cloud scheduler and have it exit after one check, set `check_interval_minutes` to `0` or less.
