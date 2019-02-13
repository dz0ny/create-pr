# GitHub action to automatically create PRs

## Installation

To configure the action simply add the following lines to your `.github/main.workflow` workflow file:

```
workflow "Automatic PR" {
  on = "release"
  resolves = "Create PR"
}

action "Create PR" {
  uses = "dz0ny/create-pr:master"
  args = "path/to/my/patch_recipe.py"
  secrets = ["GITHUB_TOKEN"]
}
```

Contents of `path/to/my/patch_recipe.py:

```python
if __name__ == "__main__":
    event = Event.fromPath(env["GITHUB_EVENT_PATH"])
    if not event.is_release:
        raise Exception("This event is not from release")

    with commit(event, f"update_{event.release.tag_name}", env["PTA_TOKEN"]) as gh:
        versions = gh.get("bin/runtime/versions")
        versions.text: str = versions.text.replace("foo.bar", "def.bar")
        gh.add(versions, "Update image to latest version")
        gh.create_pr(
            "Update image to latest version",
            "This updates web image to the latest released version",
        )
 ```

check api in [main.py](main.py).
