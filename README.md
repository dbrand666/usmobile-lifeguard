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

1. Rename the config file to config.yaml.
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
