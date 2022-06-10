# TODO

Normal state of this file is empty.

However it is useful to track your local TODOs
when your work is on hold.

Please keep them under the line.

---

refactor setup-python:

```
python is configured := python version = req version
python version := python exists? --version | ""

python not configured -> pyenv exists? - install req
                                  no   - ø
```

document that this works on mac os only for now
add this ^ check into script: uname / darwin
