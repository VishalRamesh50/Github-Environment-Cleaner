# Github Environment Cleaner

Github does not have a way to delete environments from their UI so this script does it for you via their API. It can delete specific environments or all of your deployments interactively!

All you need to do is provide the repository name, the owner's username, and an access token when prompted. You can get the access token by following [these instructions](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). Make sure you give it `repo_deployment` permissions.

## Getting Started

1. Clone repository

```sh
git clone https://github.com/VishalRamesh50/Github-Environment-Cleaner.git
cd Github-Environment-Cleaner
```

2. Install dependencies

```sh
pip install -r requirements.txt
```

3. Run the interactive script!

```sh
python3 delete_environment.py
```

If you would prefer _not_ to be prompted for an owner, repo name, or access token follow these steps

1. Copy the `.env` template to an actual `.env` file

    ```sh
    cp .env.example .env
    ```

2. Enter whatever values you want inside this file to not be prompted for like this
    ```sh
    OWNER=
    REPO=
    TOKEN=your-github-token
    ```
