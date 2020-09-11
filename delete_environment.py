import os
import requests
import sys
from dotenv import load_dotenv
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

load_dotenv()

REPO = os.getenv("REPO") or input("Enter the repo name: ").strip()
OWNER = os.getenv("OWNER") or input("Enter the owner (organization/username): ").strip()
TOKEN = os.getenv("TOKEN") or input("Enter your Github token: ").strip()
headers = {"Authorization": f"token {TOKEN}"}

# Get all deployments and create a map from env name to deployment ids
print("Retrieving all deployments...")
env_map: Dict[str, List[int]] = defaultdict(list)
next_link: Optional[Dict[str, str]] = {
    "url": f"https://api.github.com/repos/{OWNER}/{REPO}/deployments?per_page=100"
}
while next_link:
    deploys = requests.get(next_link["url"], headers=headers)
    if deploys.status_code == 401:
        print("Access Token is incorrect")
    elif deploys.status_code == 403:
        print("Rate limit has been reached")
    elif deploys.status_code == 404:
        print(f'Could not find a repo named "{REPO}" owned by "{OWNER}"')
    else:
        for deploy in deploys.json():
            env_map[deploy["environment"]].append(deploy["id"])
        next_link = deploys.links.get("next")
        continue
    sys.exit(0)

if not env_map.keys():
    print("No deployments found.")
    sys.exit(0)

# As long as there are still environments that can be deleted, keep asking
while env_map.keys():
    delete_all: bool = False
    print("Which environment do you want to delete?")
    env_names: Tuple[str, ...] = tuple(env_map)
    for index, name in enumerate(env_names):
        print(f"[{index}] {name}")
    print(f"[{index + 1}] Delete All!")
    try:
        env_index: int = int(input())
        if env_index == (index + 1):
            delete_all = True
        elif env_index < 0:
            raise IndexError
        else:
            env_name: str = env_names[env_index]
    except ValueError:
        print("Please select one of the numbers")
        continue
    except IndexError:
        print("Please select a number within the shown range")
        continue

    if delete_all:
        confirmation_msg = "Are you sure you want to do this? This will delete ALL of your deployments. y/n\n"
    else:
        confirmation_msg = f"So you want to delete {env_name}. Are you sure? y/n\n"
    confirmation = input(confirmation_msg).strip().lower()
    while True:
        if confirmation == "y":
            if delete_all:
                print("Proceeding to delete all deployments...")
                envs_to_delete: Tuple[str, ...] = env_names
            else:
                print(f"Proceeding to delete {env_name}...")
                envs_to_delete = (env_name,)

            for env_name in envs_to_delete:
                print(f"Making most recent active deploys for {env_name} inactive...")
                for deploy in env_map[env_name]:
                    response = requests.get(
                        f"https://api.github.com/repos/{OWNER}/{REPO}/deployments/{deploy}/statuses",
                        headers={
                            "accept": "application/vnd.github.ant-man-preview+json",
                            **headers,
                        },
                    )
                    # If the current deploy is already inactive then stop continuing to
                    # make earlier deployments inactive. This assumes that there will
                    # not be any Active deployments before an inactive deployment.
                    if response.json()[0]["state"] == "inactive":
                        break

                    response = requests.post(
                        f"https://api.github.com/repos/{OWNER}/{REPO}/deployments/{deploy}/statuses",
                        headers={
                            "accept": "application/vnd.github.ant-man-preview+json",
                            **headers,
                        },
                        json={"state": "inactive"},
                    )

            for env_name in envs_to_delete:
                for deploy_id in env_map[env_name]:
                    result = requests.delete(
                        f"https://api.github.com/repos/{OWNER}/{REPO}/deployments/{deploy_id}",
                        headers=headers,
                    )
                del env_map[env_name]
                print(f"Deleted {env_name}")

            if env_map.keys():
                delete_more = (
                    input("Do you want to delete any more? y/n\n").strip().lower()
                )
                while True:
                    if delete_more == "y":
                        break
                    elif delete_more == "n":
                        sys.exit(0)
                    else:
                        delete_more = (
                            input("That is not a valid option. y/n\n").strip().lower()
                        )
            break
        elif confirmation == "n":
            print("Cancelling...")
            break
        else:
            confirmation = input("That is not a valid option. y/n\n").strip().lower()
