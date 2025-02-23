<div align="center">

### 🐰 Welcome to Grabbit! 🐰

> A Reddit saved post media and metadata downloader.

</div>

---

## 📥 Installation (recommended)

```bash
pipx install git+https://github.com/devicarus/grabbit.git
```

## ⚙️ Configuration

1. [Create a Reddit app](https://www.reddit.com/prefs/apps) with the following values:
   - name `anything, e.g. Grabbit`
   - 🔘 script
   - redirect URI `http://localhost:8080`

2. Create a `.json` file with the following structure:
    ```json
    {
      "username": "YOUR_REDDIT_USERNAME",
      "password": "YOUR_REDDIT_PASSWORD",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET"
    }
    ```

## 🚀 Usage

```bash
> grabbit --help

Usage: grabbit [OPTIONS] OUTPUT_DIR USER_CONFIG

  OUTPUT_DIR is the directory where the downloaded files will be saved
  USER_CONFIG is the path to a JSON file containing Reddit user credentials

Options:
  -d, --debug     Turn on activate debug mode.
  --csv FILENAME  Use Reddit GDPR saved posts export CSV file.
  --skip-failed   Skip previously failed downloads.
  --help          Show this message and exit.
```

## 📦 Dependencies

- [Python <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" height=14 />](https://www.python.org/downloads/) 3.12+ (tested on 3.13)
- [ffmpeg](https://ffmpeg.org/download.html) (optional, video downloads *may* not work properly without it)

## ❓ FAQ
### Grabbit is only downloading the latest ~1k saved posts
Reddit's API only allows access to the latest circa 1000 saved posts.\
To download all saved posts, you can [request your Reddit data](https://www.reddit.com/settings/data-request) and use the `--csv` option with the exported CSV file.
