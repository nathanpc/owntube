# OwnTube

A web service that gives back control over your YouTube library and allows you
to have local copies of all of your favorite channels.

## Requirements

This project requires at least [Python 3.8](https://www.python.org/) and
[FFmpeg](https://ffmpeg.org/) to be installed on the system.

## Setup

In order to use this project you first need to set up the environment. The
first step would be to create the database required to cache the information
about the channels and their videos:

```bash
mariadb < sql/initialize.sql
```

Next you should set up the [Python virtual environment](https://docs.python.org/3/library/venv.html)
and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Now you'll need to [get an API secrets file](https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials)
from Google in order to use the  YouTube Data API. Place the file in the root
of the project with the name `secrets.json`.

In order for the application to have access to your database and to configure
some customizable aspects of it you'll need to create a `config.yml` file in
the root of the project with the following content (customized to fit your
needs):

```yaml
---
db:
  user: 'owntube'
  password: 'somepassword'
  host: 'localhost'
  port: 3306
  database: 'owntube'
```

Now you should have your entire environment properly set up and ready to start
building up a library. In order to import all of your favorite channels and
their videos you'll need to run the following commands:

```bash
./bin/ytdump
./bin/import_dump
```

You should now have a backup of your YouTube subscriptions and the system is
now ready to start:

```bash
python3 ./owntube/__init__.py
```

## License

This library is free software; you may redistribute and/or modify it under the
terms of the [Mozilla Public License 2.0](https://www.mozilla.org/en-US/MPL/2.0/).
