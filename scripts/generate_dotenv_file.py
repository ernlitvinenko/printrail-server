import importlib.util
from collections import defaultdict
from pathlib import Path

environment_core_module_path = Path(__file__).parent.parent / Path(
    "core/environment/environment.py"
)
module_name = environment_core_module_path.stem

spec = importlib.util.spec_from_file_location(module_name, environment_core_module_path)

if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {environment_core_module_path}")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ENV_FILE = module.ENV_FILE
_Settings = module._Settings


DOTENV_SAMPLE_FILE = Path(ENV_FILE.name + ".sample")

fields = defaultdict(dict)

if ENV_FILE.exists():
    with ENV_FILE.open() as f:
        for line in f:
            key, value = line.strip().split("=")
            fields[key]["val"] = value

for key, val in _Settings.model_fields.items():
    fields[key]["example"] = val.examples[0]


for idx, file in enumerate([DOTENV_SAMPLE_FILE, ENV_FILE]):
    with open(file, "w") as f:
        for key, val in fields.items():
            value = val.get("val", None)
            if idx == 0 or value is None:
                f.write(f"{key}={val['example']}\n")
                continue
            f.write(f"{key}={value}\n")
