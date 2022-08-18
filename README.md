# Stable Diffusion Scraper

## Requirements

- [Python>=3.7](https://www.python.org/downloads/)
- [Chrome Browser](https://www.google.com/chrome/)
- [Chrome Driver](https://chromedriver.chromium.org/downloads)

## Getting Started

- Clone this repository, then install required packages.

```sh
git clone git@github.com:Alyetama/stable-diffusion-scraper.git
cd stable-diffusion-scraper
pip install -r requirements.txt
```

- To get your Discord user token, open the console in your browser, then run:

```js
location.reload();
window.stop();
var i = document.createElement('iframe');
document.body.appendChild(i);
console.log(i.contentWindow.localStorage.token);
```

The page will refresh and your token will appear at the top of the console output.

- Rename and edit `.env` to add the user token you just copied.

```sh
mv .env.example .env
nano .env  # or your favorite editor
```

## ⌨️ Usage

```sh
python scraper.py
```

You can edit `scraper.py` to integrate any backend database. The JSON file is just an example and is not meant to be used as a permanent option.
