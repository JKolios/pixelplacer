# pixelplacer
Reddit Place (2022) automation

## Installation
* Create a virtualenv and install the requirements in `requirements.txt`.
* Create a reddit OAuth2 app: https://github.com/reddit-archive/reddit/wiki/OAuth2

## Usage
Having activated the virtualenv, run:
```
python pixel_placer.py IMAGE_PATH TOP_LEFT_PIXEL_X TOP_LEFT_PIXEL_Y REDDIT_USERNAME REDDIT_PASSWORD OAUTH_APP_ID OAUTH_APP_SECRET
```

## Caveats
This is still random junk hacked together. No guarantees that it will be stable.

`square.png` is a small 4x4 pixel test pattern.