# pixelplacer
Reddit Place (2022) automation. Uses multiple reddit accounts to draw an image on reddit place 2022.

## Installation and setup
* All major versions of Python 3 should work(untested). Don't use Python 2. It's 2022 as of this commit, why would you do still do that?
* Create a virtualenv and install the requirements in `requirements.txt`.
* For each reddit account you want to use, create a reddit OAuth2 app at https://www.reddit.com/prefs/apps. More instructions at https://github.com/reddit-archive/reddit/wiki/OAuth2
* Write down the credentials of the reddit accounts you want to use in a csv file in this format, one account per line:
```
username,password,oauth_app_id,oauth_secret
```
* Get an image for the bot to draw. Common formats like JPG and PNG will work. More exotic formats are untested, refer to the docs for the Pillow python package for info. No vector graphics, probably. The image will be drawn pixel by pixel, by approximating colors to the nearest one in Place's limited palette.


## Usage
Having activated the virtualenv, run:
```
python pixel_placer.py CREDENTIALS_FILE_PATH IMAGE_PATH TOP_LEFT_PIXEL_X TOP_LEFT_PIXEL_Y
```

## Caveats

**I make no promises reagrding whether this is compatible with the reddit ToS. Use at your own risk.**

This is still random junk hacked together. No guarantees that it will be stable.

`square.png` is a small 4x4 pixel test pattern.
`5x5.png` is a 5x5 test pattern.