# Lara
Your virtual project manager

![Logo](img/lara_logo.png)

## Setup
* Configration

	Before running the application, you should create a file named **config.py** in directory **instance** and configure it. You can do the configuration by referring to **config.py.example**.

* RUN
```
pip install -r requirements.txt
FLASK_APP=__init__.py flask run --host <host> --port <port>
```


### GitHub App
Lara will be distributed as a [GitHub App](https://developer.github.com/apps/building-github-apps/) that can be installed on organization or user accounts. Unfortunately this feature is very new and not yet supported by PyGithub, so we have to implement this by by ourselves.
- GitHub App API: https://developer.github.com/v3/apps/
- GitHub App Installation API: https://developer.github.com/v3/apps/installations/