# AUMS Assignment Maker — Multi-file version

## Run

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```

## Structure

```text
main.py
config.py

aums/
  browser.py
  login.py
  portal.py
  courses.py
  assignments.py
  attachments.py

storage/
  aums_session.json

utils/
  console.py
  urls.py

assignment_files/
```

The project is intentionally split so AUMS navigation, assignment extraction,
file downloading, browser handling, and session handling can be developed
independently.
