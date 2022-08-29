# Generating Figures 
This package is used to generate the figures used in the paper.
Due to compatibility issues, the rest of the system uses Python 3.6.9.
However, in order to leverage the new features in later versions of Matplotlib, the figure generation uses Python 3.10.
A new venv must be created for the figure generation.

```bash
sudo apt install python3.10-venv
python3.10 -m venv figure_venv
source figure_venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```