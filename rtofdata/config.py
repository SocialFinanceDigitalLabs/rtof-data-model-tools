from pathlib import Path
import os

root = Path(__file__).parent / '..'

data_root = os.getenv("DATA_ROOT")
if data_root:
    data_root = Path(data_root)
else:
    data_root = Path(__file__).parent / '../../rtof-data-model'

assets_dir = data_root / 'assets'

data_dir = data_root / 'data'

template_dir = root / "templates"

output_dir = root / 'output'
output_dir.mkdir(parents=True, exist_ok=True)

jekyll_dir = root / "website"

output_filename_base = "specification"
