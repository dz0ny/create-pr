from main import Event
from main import File
from main import GitHub
from pathlib import Path
import json


def test_json_release():
    ev: Event = Event.fromPath("fixtures/release.json")
    assert ev.repository.name == "Hello-World"
    assert ev.is_release
    assert ev.base == "https://api.github.com/repos/Codertocat/Hello-World"


def test_json_push():
    ev: Event = Event.fromPath("fixtures/push.json")
    assert ev.repository.name == "Hello-World"
    assert not ev.is_release
    assert ev.base == "https://api.github.com/repos/Codertocat/Hello-World"


def test_file_decode():
    text = Path("fixtures/get_file.json").read_text()
    data = json.loads(text)
    ev: File = File.fromJSON(data)
    assert ev.text == "my updated file contents"


def test_file_encode():
    text = Path("fixtures/get_file.json").read_text()
    data = json.loads(text)
    ev: File = File.fromJSON(data)
    ev.text = "my new file contents"
    assert ev.content == b"bXkgbmV3IGZpbGUgY29udGVudHM="
