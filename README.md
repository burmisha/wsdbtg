# wsdbtg

Playground for website, database, telegram bot.

## Telegram bot

Simple echo-bot on Python 3.12+. Responds to `/start`, `/help`, and echoes any text message.

### Local development

Requirements: [pyenv](https://github.com/pyenv/pyenv), [uv](https://docs.astral.sh/uv/)

```bash
# Install pyenv (macOS/Linux)
curl https://pyenv.run | bash

# Install uv
curl --location --silent --show-error --fail https://astral.sh/uv/install.sh | sh

# Install Python 3.12 via pyenv
pyenv install 3.12

# Install dependencies (uv.lock committed to repo)
uv sync

# Configure secrets
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN

# Run
uv run python -m bot.main
```

Get a bot token from [@BotFather](https://t.me/BotFather).

---

## Deploy to Digital Ocean via Docker

### 1. Create a Droplet

- Ubuntu 24.04 LTS, Basic plan.
- Add your SSH key during setup. `ssh-keygen -t ed25519 -C "deploy@digitalocean" -f ~/.ssh/digital_ocean`

### 2. Install Docker on the Droplet

```bash
ssh -i ~/.ssh/digital_ocean root@<droplet-ip>

curl --fail --silent --show-error --location https://get.docker.com | sh

adduser deploy
usermod -aG docker deploy
su - deploy
```

### 3. Clone the repo

```bash
git clone https://github.com/burmisha/wsdbtg.git
cd wsdbtg
```

### 4. Configure secrets

```bash
cp .env.example .env
vim .env  
```

### 5. Start the bot

```bash
docker compose up --detach --build
```

### 6. Useful commands

```bash
# View logs
docker compose logs --follow

# Stop
docker compose down

# Restart after code update
git pull && docker compose up --detach --build
```
