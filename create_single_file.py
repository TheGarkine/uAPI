"""Just aggregates all files in uAPI/ together into one common uAPI.py file for compilation of the entire module.
Since we are not using any cross references during module load (for now) we do not care about the order.
"""

import os
import re

dir = "./uAPI"
files = [f for f in os.listdir(dir) if f != "__init__.py"]

document = ""
for file in files:
    with open(os.path.join(dir, file)) as f:
        document += f.read()
        document += "\n"

local_import_regex = r"(import|from) \.[0-9A-Za-z]+"
cleaned_document = "\n".join(
    [l for l in document.split("\n") if not re.match(local_import_regex, l)]
)

if not os.path.exists("build"):
    os.mkdir("build")

with open("build/uAPI.py", "w") as f:
    f.write(cleaned_document)
