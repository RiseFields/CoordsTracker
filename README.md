# CoordsTracker

A simple discord.py bot used to track coordinates. Users can claim coordinates ranging from (0,0) up to (999,999). Claims expire after 24h but can be extend during this 24h period. 

## Instalation

Clone the repository and move in the directory:
```bash
git clone https://github.com/RiseFields/CoordsTracker
cd CoordsTracker
```

Run the setup script
```bash
chmod +x setup.sh 
./setup.sh
```

And finally run the bot!
```bash
source .venv/bin/activate
python3 CoordsTraker.py
```

## Features

Quick overview of the features:
- claiming coordinates
- extending claims
- releasing claims
- live updated overview
- notifications about expiring claims

### Claiming

Command: `!claim [coordinate]`

Claim the coordinate (x,y) for the next 24h. 
The bot is forgiving and accepts multiple formates of coordinates such as:
- 123,123
- 123;123
- 123 123
- 123x123
- (123,123)
- [123,123]
- ...

The user will be notified if they somehow managed to provide a wrong format of coordinates, as well as when the coordinate is already claimed by another user.

### Extending

Command: `!extend [coordinate]`

Extend the claim on a coordinate.

A message will be sent when the user has not claimed the coordinate.

### Releasing

Command: `!delete [coordinate]`

Releases the claim on a coordinate.

A message will be sent when the user has not claimed the coordinate.

### Setup

Command: `!setup`

There is a bare minimum of setup required for the bot. Before using any of the commands run the setup command to properly configure the database.

### Overview

Command: `!overview_channel <channel>`

The bot keeps a live updated overview message when channel_id is specified. Mentioning the wanted channel (typing #channel) is sufficient as argument. Otherwise the channel_id is needed.
To disable the overview message, leave out the channel argument: `!overview_channel`.

After each update to the database, such as people claiming, extending or releasing coordinates as well as claims expiring, updates the overview message.

An overview of the current claimed coordinates can always be viewed by using `!view`. This is irrelevant of the overview channel/message.

### Notifications

Command: `!notify <channel>`

The bot can automatically mention users who's claims will expire in an hour, and when their claims have expired. These notifications will be send to the channel specified in the command. This works the same as the overview channel. Omit the channel to disable notifications.
