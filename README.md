# half_light

![half_light](/screenshots/screenshot.png)

control a colour field using reactive sliders, either RGB or HSV

use separate Processes for GUI and output

prototype to run on an embedded system where the operator can use
physical knobs to change the colour of an LCD panel, hence swappable
`GUIColourControls`

## installation

```shell
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## running

```shell
. .venv/bin/activate
python app.py
```
