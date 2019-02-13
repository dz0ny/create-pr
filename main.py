import requests
from os import environ as env
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import json
from dacite import from_dict
import typing as t
from base64 import b64encode, b64decode


@dataclass(frozen=True)
class Sender:
    type: str  # "User"
    login: str  # "Codertocat"
    id: int  # 21031067
    url: str  # "https://api.github.com/users/Codertocat"


@dataclass(frozen=True)
class Release:
    url: str  # "https://api.github.com/repos/Codertocat/Hello-World/releases/11248810"
    html_url: str  # "https://github.com/Codertocat/Hello-World/releases/tag/0.0.1"
    id: int  # 11248810
    node_id: str  # "MDc6UmVsZWFzZTExMjQ4ODEw"
    tag_name: str  # "0.0.1"
    target_commitish: str  # "master"
    created_at: str  # "2018-05-30T20:18:05Z"
    published_at: str  # "2018-05-30T20:18:44Z"


@dataclass(frozen=True)
class Repository:
    id: int
    name: str  # "Hello-World"
    full_name: str  # "Codertocat/Hello-World"
    private: bool  # false
    description: t.Optional[str]  # "Hello-World Repo"
    fork: bool  # false
    url: str  # "https://api.github.com/repos/Codertocat/Hello-World"
    default_branch: str  # "master"


@dataclass(frozen=True)
class Event:
    repository: Repository
    sender: Sender
    release: t.Optional[Release]

    @classmethod
    def fromPath(cls, event_path: str) -> "Event":
        text = Path(event_path).read_text()
        data = json.loads(text)
        return from_dict(cls, data)

    @property
    def is_release(self) -> bool:
        return bool(self.release)

    @property
    def base(self) -> str:
        return self.repository.url


@dataclass
class File:
    type: str  # "file"
    encoding: str  # "base64"
    size: int  # 5362
    name: str  # "README.md"
    path: str  # "README.md"
    content: str  # "encoded content ..."
    sha: str  # "3d21ec53a331a6f037a91c368710b99387d012c1"
    url: str  # "https://api.github.com/repos/octokit/octokit.rb/contents/README.md"

    def patch(self, message: str, branch: str) -> dict:
        return {
            "message": message,
            "content": self.content.decode("utf8"),
            "sha": self.sha,
            "branch": branch,
        }

    @property
    def text(self) -> str:
        return b64decode(self.content).decode("utf8")

    @text.setter
    def text(self, data: str):
        self.content = b64encode(data.encode("utf8"))

    @classmethod
    def fromJSON(cls, data: dict) -> "File":
        return from_dict(cls, data)


class GitHub:

    http: requests.Session
    api = "https://api.github.com"

    def __init__(self, repo: str, branch: str, github_token: str):
        self.http = requests.Session()
        self.http.headers["Authorization"] = f"Token {github_token}"
        self.http.headers["Accept"] = "application/vnd.github.v3+json"
        self.branch = branch
        self.repo = repo

    def get(self, path: str) -> File:
        res = self.http.get(f"{self.api}/repos/{self.repo}/contents/{path}")
        res.raise_for_status()
        return File.fromJSON(res.json())

    def create_pr(self, title: str, body: str):
        res = self.http.post(
            f"{self.api}/repos/{self.repo}/pulls",
            json={"title": title, "body": body, "head": self.branch, "base": "master"},
        )
        res.raise_for_status()
        return res.json()

    def create_branch(self):
        res = self.http.get(f"{self.api}/repos/{self.repo}/git/refs/heads/master")
        res.raise_for_status()
        master = res.json()
        res = self.http.post(
            f"{self.api}/repos/{self.repo}/git/refs",
            json={"ref": f"refs/heads/{self.branch}", "sha": master["object"]["sha"]},
        )
        res.raise_for_status()
        return res.json()

    def add(self, file: File, message: str):
        res = self.http.put(
            f"{self.api}/repos/{self.repo}/contents/{file.path}",
            json=file.patch(message, self.branch),
        )
        res.raise_for_status()
        return res.json()


@contextmanager
def commit(repo: str, new_branch: str, token: str) -> "GitHub":
    gh: GitHub = GitHub(repo, new_branch, token)
    gh.create_branch()
    yield gh


# Example

"""
if __name__ == "__main__":
    event = Event.fromPath(env["GITHUB_EVENT_PATH"])
    if not event.is_release:
        raise Exception("This event is not from release")

    with commit("gh/repo", f"update_{event.release.tag_name}", env["PTA_TOKEN"]) as gh:
        versions = gh.get("bin/runtime/versions")
        versions.text: str = versions.text.replace("foo.bar", "def.bar")
        gh.add(versions, "Update image to latest version")
        gh.create_pr(
            "Update image to latest version",
            "This updates web image to the latest released version",
        )
"""
