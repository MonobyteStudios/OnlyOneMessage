<img src="https://cdn.monobyte.studio/projects/onlyonemessage.png" width="250"/>

# OnlyOneMessage

### Command Every Message.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Discord.py](https://img.shields.io/badge/discord.py-latest-blue)](https://github.com/Rapptz/discord.py)


## ❓ Overview

OnlyOneMessage is a feature-rich Discord bot that provides server admins **complete control** over text channel behavior.
Set slowmodes **surpassing Discord's limit**, log **individual member cooldowns**, and **fine-tune** settings for **each individual channel**;
all through a straightfoward interface using Discord's slash commands.

v2.0a [Build 2026.7.5]

📎 Visit the website: [onlyonemessage.monobyte.studio](https://onlyonemessage.monobyte.studio)

❓ Documentation: [onlyonemessage.monobyte.studio/docs](https://onlyonemessage.monobyte.studio/docs)


## ⚡ Features

- **⏳ Advanced Slowmode Control** - Set channel slowmodes lasting hours, days, **or even indefinitely**; surpassing Discord's limitations.
- **💬 Smart Message Management** - Allow members to **chat again** once they delete their message, providing complete flexibility in message flow.
- **📝 Detailed Logging** - Automatically log when members enter slowmode **and when they expire**, including other essential options
- **📊 Analytics** - Built-in Prometheus tracking for reliability 
- **🐬 Docker Supported** - Containerized deployment with Docker for easy usage


## 🖥️ Installation

OnlyOneMessage is fully supported **and** hosted by Monobyte Studios, [invite the bot here.](https://onlyonemessage.monobyte.studio/invite)
If you would like to self-host this bot, follow the instructions below:

### Prerequisites

- Python (**3.10+** recommended)
- Docker
- Discord bot token (Get one from the Discord Developer Portal)

> [!NOTE]
> OnlyOneMessage uses `MongoDB` for its database; a self-hosted setup has already been provided in `docker-compose.yml`. Edit if needed.

### Instructions

1. Clone the repository:
```bash
git clone https://github.com/MonobyteStudios/OnlyOneMessage.git
cd OnlyOneMessage
```

If you'd like to use the nightly branch:
```bash
git clone -b nightly https://github.com/MonobyteStudios/OnlyOneMessage.git
cd OnlyOneMessage
```

> [!WARNING]
> The `nightly` branch of OnlyOneMessage is a **beta build of a later version**, expect bugs when using it.

2. Configure environment variables

Create the file `.env` inside `/data` with the following:

```bash
TOKEN= # Put your Discord bot token here

# MongoDB (Set <CHANGEME> to a secure password)
MONGO_URI=mongodb://admin:<CHANGEME>@mongodb:27017
MONGO_DB=onlyonemessage 

MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=<CHANGEME>

# Integrations, these may be removed if you dont require it
TOPGG_TOKEN=<CHANGEME>
```

> [!TIP]
> There's a `.env.example` file inside the `data` folder. Use it as a reference!

3. Configure metadata

The metadata file for OnlyOneMessage can be found in `/data/json/metadata.json`;
update the provided fields in the file to your liking:

```bash
{
    "metrics_support": false, # Whether to collect metrics or not (If enabled, port 9200 will be opened)
    "api_support": false, # Whether the API is enabled or not (If enabled, port 9300 will be opened)

    "admins": [
        # Discord user ID's who have access to development commands
    ],
    "internalguilds": [
        # Discord guild ID's where admins can execute development commands
    ]
}
```

Additionally, edit the file `/data/json/channels.json` to match your setup.
You do not need to touch this file if `metrics_support` is set to `false`.


4. Run the bot:
```bash
docker compose up -d
```

The bot will automatically install dependencies and start the container with automatic restart enabled. To view the container's logs:
```bash
docker logs -f onlyonemessage
```

### Uninstallation

Simply run this in the root directory:
```bash
docker compose down -v
```

> [!WARNING]
> `-v` will clear all volumes related to OnlyOneMessage, **including it's database.** If you wish to keep it's database, leave `-v` out.


## 📁 Project Structure

```
OnlyOneMessage/
├── .github/workflows/
│   └── deploy.yml           # CI/CD, builds + deploys on push to main
├── build/
│   ├── essential/           # Essential functions & variables to be used in modules, such as logmsg
│   ├── modules/
│   │   ├── commands/        # Slash commands, grouped by purpose
│   │   │   ├── dev/           # Development-only commands, accessible to "admins" in metadata.json
│   │   │   ├── essential/     # /config & /configchannel commands
│   │   │   ├── main/          # Primary commands (/addchannel, /removechannel)
│   │   │   └── misc/          # Everything else
│   │   ├── core/            # Required modules (MongoDB, error handler)
│   │   ├── events/          # Event listeners (on_message, on_member_update, etc.)
│   │   ├── integration/     # Integrations for services (top.gg, API)
│   │   └── loops/           # Background tasks
│   └── main.py               # Entry point (Run this to start the bot)
├── data/
│   ├── backups/               # MongoDB backups (mongo-backup service)
│   ├── json/                  # Configurations
│   │   ├── channels.json       # Channels reference (applicable if metrics_support in metadata is set to true)
│   │   └── metadata.json       # Bot-wide configuration (see Installation)
│   ├── .env                   # Your local environment config
│   ├── .env.example           # Reference for .env, may be removed
│   └── log.log
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
```


## 🛠️ Contributing to OnlyOneMessage

We welcome contributions to OnlyOneMessage from the community! 
Your help is appreciated, whether you're adding features, fixing bugs, or adding documentation.

> [!NOTE]
> If you are going to make major changes to OnlyOneMessage, **open an issue first** to discuss before investing time in it.

### Contributions We Welcome

- **Bug Fixes** - Issues and their solutions
- **Features** - Command improvements/new functions
- **Documentation** - README improvements, code comments, documentation under [OnlyOneMessageWeb](https://github.com/MonobyteStudios/OnlyOneMessageWeb)
- **Refactoring** - Quality of life changes, code quality improvements

### Getting Started

1. Fork this repository

2. Clone your fork:
```bash
git clone https://github.com/<YOUR_USERNAME>/OnlyOneMessage.git
cd OnlyOneMessage
```

3. Create a branch on your fork:
```bash
git checkout -b <BRANCH>/<YOUR_CHANGE>
```

4. Continue setting up the bot through the `Installation` section

### Making Changes

Here's a checklist on what your changes should follow:

- Keep commits clean; each commit should be logical
- Follow the existing style with the codebase unless necessary to change it
- Add comments for logic that isnt obvious

### Before making a Pull Request

- Verify your changes work in a **testing server**
- Submit **one** change per pull request (exceptions apply)
- Update documentation if your changes affect this README or comments

### Submitting your Changes

1. Push to your fork, if you haven't

2. Open a **Pull Request** on this repository with the following:
    - A clear title describing your changes
    - A detailed description on what you've done
    - Reference related issues if needed
    - Screenshots/logs if necessary

4. Respond and edit to changes if requested

### Questions?

If you have any questions regarding this, see our `Support` section, open a new issue, or check our documentation for further details.

Thank you for contributing! 💖


## 📰 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**, see the `LICENSE.txt` file for more information.

### What this means:

- ✅ **Free to Use** - You can freely use the bot by inviting it to your own server
- ✅ **Free to Study** - You can inspect & learn from it's source code
- ✅ **Free to Modify** - You can create modified versions for personal or community use

- ⚠️ If you host your own instance of this bot as a service, you must:
    - Provide access to your complete source code, including modifications
    - Release all source code under **APGL-3.0** ***OR*** [contact Monobyte Studios](mailto:legal@monobyte.studio) for a commercial license

### Why this license?

Monobyte Studios provides and maintains OnlyOneMessage as a hosted service;
AGPL-3.0 ensures the community will benefit from improvements while protecting against unfair exploitation of our work.


## ❓ Support
You can receive support by [joining our support server](https://onlyonemessage.monobyte.studio/support), creating an issue on this repository, or by [emailing us.](mailto:support@monobyte.studio)

---

**Made with ❤️ by [Monobyte Studios](https://monobyte.studio)**