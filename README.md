# usmobile-lifeguard
Minds your USMobile pool so you don't have to

**WARNING!!! Use at your own risk!!!**

This script is new, uses undocumented APIs, and **makes purchases** for you.

**It can potentially run amok and purchase many gigabytes of data**. I built in a few safeguards but I make no promises.

**WARNING!!! Use at your own risk!!!**

# Installation
Still reading?

You've been warned.

Well ok then. Go ahead and clone this repo or just copy the config.yaml-template file and docker-compose.yaml file to a local directory.

1. Rename the config template file to config.yaml: `cp config.yaml-template config.yaml`
    1. Make an extra hard link to the config file: `ln config.yaml config.yaml-dont-move-me-vim`. You can ignore this link and it can be named whatever you want. It's just there to keep certain editors from changing the inode number when you edit the file.
    2. By the way, you can also configure any setting via an environment variable upper-cased & prefaced with `LIFEGUARD_`. Any setting specified in the environment will override the corresponding setting in the config file.
2. You need to get the app an authentication token and a pool id. To accomplish this:
    1. Log into your USMobile account in a private window.
    2. Navigate to the pool detail page for the pool you want it to watch. It'll have a URL that looks something like https://app.usmobile.com/dashboard/app/pools/ffffffff.
    3. That string of hex characters (the `ffffffff` in my exmple) is your pool id. Put it in the yaml file inside the quotes next to `pool_id`.
    4. Go into web developer tools in the browser and look at the network tab. You'll probably have to refresh the page to get it to show you anything interesting.
    5. Look for a request to `api.usmobile.com`. Select it.
    6. Scroll down to the request headers and look for the `USMAuthorization` header.
    7. The value for that header should start with `Bearer ey`. Grab the whole long string starting with `ey` and copy it into the `token` field.
3. Edit the rest of the values in the file to suit your preferences. There are comments in there that should be self-explanatory.
4. To run the app, use the command: `docker compose up --build`.
5. Keep an eye on the output. If it does anything unexpected kill it and check your configuration.
6. It will give you a 10 second warning before performing a top up. That gives you a chance to kill it if you're watching.
7. The config file can be changed while the application is running. The changes take affect on the next cycle - no need to restart.
8. If you want to run the script on a cron schedule or some cloud scheduler and have it exit after one check, set `check_interval_minutes` to `0` or less.
