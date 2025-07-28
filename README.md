# n8n Documentation Cleaned for AI Training

This repository contains cleaned n8n documentation optimized for training AI language models.

## Files

- **`extract_docs_improved.py`** - Python script for cleaning Markdown documentation
- **`n8n_documentation_cleaned_improved.json`** - Cleaned dataset ready for AI training (1.9MB, documents)

## What the cleaning script does

The script processes n8n's Markdown documentation and removes:

- ✅ **Frontmatter metadata** (title, description, contentType, tags, etc.)
- ✅ **Code blocks** (```language...```)
- ✅ **All URLs and links** (including Notion URLs)
- ✅ **MkDocs macros and directives** ([[ templatesWidget(...) ]], /// info ///, etc.)
- ✅ **HTML comments** (<!-- -->)
- ✅ **Inline code formatting** (preserving content)
- ✅ **Reference-style links**

The script preserves:

- ✅ **Markdown tables** in readable format
- ✅ **Natural language content**
- ✅ **Document structure**

## How to reproduce

1. **Clone the original n8n documentation:**
   ```bash
   git clone https://github.com/n8n-io/n8n-docs.git
   cd n8n-docs
   ```

2. **Download the cleaning script:**
   ```bash
   wget https://raw.githubusercontent.com/msavich/n8n_documentation_cleaned/master/extract_docs_improved.py
   ```

3. **Install required Python packages:**
   ```bash
   pip install markdown beautifulsoup4 pyyaml
   ```

4. **Run the cleaning script:**
   ```bash
   python extract_docs_improved.py
   ```

5. **Output will be generated as:**
   - `n8n_documentation_cleaned_improved.json`

## Usage

```python
import json

# Load the cleaned documentation
with open('n8n_documentation_cleaned_improved.json', 'r', encoding='utf-8') as f:
    docs = json.load(f)

# Each document has:
# - file_path: relative path to original file
# - content: cleaned text content
for doc in docs:
    print(f"File: {doc['file_path']}")
    print(f"Content: {doc['content'][:200]}...")
```

## Dataset Statistics

- **Source files**: ~650 Markdown files from n8n documentation
- **Output size**: ~1.9 MB JSON file
- **Documents**: 500+ cleaned entries
- **Average document length**: ~2,000 characters
- **Language**: English
- **Format**: JSON with file_path and content fields

## License

This cleaned dataset is derived from [n8n documentation](https://github.com/n8n-io/n8n-docs) which is licensed under the [Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md).

---

*Generated with Claude Code by [@msavich](https://github.com/msavich)*
