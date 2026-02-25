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

### One-time droplet setup

Create a Droplet:

- Ubuntu 24.04 LTS, Basic plan.
- Add your SSH key during setup.

```bash
ssh-keygen -t ed25519 -C "deploy@digitalocean" -f ~/.ssh/digital_ocean

# put pub-key into /home/deploy/.ssh/authorized_keys for github
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/gh_do_deploy

# Install Docker on the Droplet

ssh -i ~/.ssh/digital_ocean root@<droplet-ip>

curl --fail --silent --show-error --location https://get.docker.com | sh

adduser deploy
usermod -aG docker deploy
su - deploy

# Configure secrets

cp .env.example ~/.env
vim ~/.env
```

---

### Auto-deploy via GitHub Actions

On every push to `main`, the workflow in `.github/workflows/deploy.yml`:
1. Builds the Docker image and pushes it to GHCR (`ghcr.io/burmisha/wsdbtg:latest`)
2. Copies `docker-compose.yml` to the droplet via SCP
3. SSHes into the droplet and runs `docker compose pull && docker compose up --detach`

`GITHUB_TOKEN` is used automatically to push to GHCR — no additional tokens needed.

Add these secrets to the repo (`Settings → Secrets and variables → Actions`):

| Secret | Value                                 |
|---|---------------------------------------|
| `DEPLOY_HOST` | Droplet IP address                    |
| `DEPLOY_USER` | `deploy`                              |
| `DEPLOY_SSH_KEY` | Contents of private key `~/.ssh/gh_do_deploy` |

> **Note:** `.env` is not managed by CI. Deliver it to the droplet manually once
> and update it when new variables are added.

```bash
scp -i ~/.ssh/gh_do_deploy .env deploy@<droplet-ip>:/home/deploy/.env
ssh -i ~/.ssh/gh_do_deploy deploy@<droplet-ip> "chmod 600 /home/deploy/.env && ls -alh /home/deploy/.env"
```

---

### Manual deploy

```bash
scp -i ~/.ssh/digital_ocean docker-compose.yml deploy@<droplet-ip>:~/
ssh -i ~/.ssh/digital_ocean deploy@<droplet-ip> \
  "docker compose --file ~/docker-compose.yml pull && docker compose --file ~/docker-compose.yml up --detach"
```

### Useful commands

```bash
# View logs
docker compose logs --follow

# Stop
docker compose down
```
