# uAPI - A micropython API framework

This project is meant to make programming APIs on micropython supported microcontrollers easier. The general design is inspired by [tiangolo/fastapi](https://github.com/tiangolo/fastapi), one of my favorite python frameworks which I personally use a lot.

If you have any questions, it is recommended to check the [examples directory](/examples) first.

## Usage

Generally there are two possibilities to use this framework in your project:

### prebuild

You can go to the releases page and check for the latest .mpy file. You can simply add this file on your controller and it will be used just as the package itself. This is the most efficient version to use uAPI, since it is precompiled bytecode.

### upip

If your use-case allows it you can use uAPI with upip (only when the device has internet connection).

```python3
import upip
upip.install("micropython-uAPI")
```

For your local port of micropython you can also call:

```
micropython -m upip install micropython-uAPI
```

### with code

You can also add the entire `uAPI/` subdirectory on your controller and develop with it as with any other local module. This is only recommended if you want to experiment on something or contribute to the project.

## Features

- Safe typing for headers

## Building

The two sections below describe how to build the framework either manually or with Docker.

### Manually

First of all make sure you have the latest version of the mpy-cross, the open source micropython cross compiler. For that visit the offical [micropython github page](https://github.com/micropython/micropython).

Then you can simple aggregate all the python files in the `uAPI/` subdirectory to a single `uAPI.py` file which will be stored in `build/`, using the provided script `create_single_file.py`.

This file can already be used as your module. It is recommended to use the precompiled version though, reducing the space and also the runtime. Therefore simply use the mpy-cross command after merging the files:
```bash
mpy-cross -O[3] ./build/uAPI.py
```

`-O[3]` will indicate mpy-cross to use the highest level of compression, read more about these in the mpy-cross documentation.

### Docker(-Compose)
To build using the docker compose simply use, (don't forget to add `--build` if running the first time):
```bash
docker-compose up uapi-build
```

If you do not want to run with docker-compose but still want to use docker, you can do so by mounting the directories into the image on run:
```
docker build . -t uapi-build
docker run \
    -v $(pwd)/uAPI:/uAPI \
    -v $(pwd)/build:/build \
    uapi-build
```

## Contributing

Thank you for your interest in contributing to this project!

### Compiling and Testing
To validate whether your changes would compile you can call the [micropython unix port](https://github.com/micropython/micropython#the-unix-version) from the offical repository.

You can check your compile by:
```
micropython -X compile-only <your changed file>
```

#### TODO TESTING

### Formatting
We use [black](https://pypi.org/project/black/) to check our formatting, to use it you can simply install it by (you may need an sudo install to get it as an recognized command in your shell):
```
(sudo) pip3 install black
```

You can simply use it as `black .` to automatically format the whole project or with the `--check --diff` flags to see if black would require you to do any changes without actually writing on your files.


### Hooks
You should setup a pre-commit hook on your machine, that handles the format and syntax checks automatically and helps you to keep your worktree clean. Note that not well formatted code (and of course unfunctional one) will not be accepted to the codebase.
```
git config --local core.hooksPath ./.githooks/
```

## License
This project is licensed under the terms of the MIT license.