# Dialectological text generator

TextGenerator downloads articles from Wikipedia and converts them to dialectological text format.

## What is a dialectological text?

Linguists at NaRFU go on dialectological expeditions to different villages of Arkhangelsk region. The dialogs with locals are transcribed into notebooks and the examples of a dialect words and an example of its usage is written on cards. The dialectological text is a text that conveys linguistic features using special symbols like acutes, apostrophes etc.

Dialectological text: `[ста̄ну́шку к‿руба́х'и пр'ишыва́л'и]`

![Example of a card](https://cdn-uploads.huggingface.co/production/uploads/66f94ad1b720048bbc98aeea/OxbyTr2krLmkYUS7I738p.png)

# Installation

1. Create an virtual environment (Optional)

```bash
python -m venv venv
# for windows:
./venv/Scripts/activate.ps1
# for linux:
source ./venv/bin/activate
```

2. Install package from GitHub

```bash
pip install git+https://github.com/DialecticalHTR/AnnotationExporter.git
```

# Usage

Create an `TextGenerator` object and call `generate_text_chunks` to generate text:

```python
import time
from text_generator import TextGenerator

g = TextGenerator()

total = 200_000
sentences = g.generate_text_chunks(total)
```
