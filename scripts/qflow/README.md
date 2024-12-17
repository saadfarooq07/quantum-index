# Quandex Core Workflows 🛠️

A collection of powerful tools to maintain and organize your Quandex repositories.

## Tools Available 🧰

### 1. qcheck 🔍
Repository health check tool. Analyzes and reports on:
- File organization
- Code structure
- Repository size
- Potential issues

```bash
# Run a health check
python qcheck.py --repo /path/to/repo

# Use custom config
python qcheck.py --repo /path/to/repo --config custom_config.yml
```

### 2. qclean 🧹
Repository cleaning tool. Helps maintain a clean and organized codebase:
- Removes unnecessary files
- Organizes files into proper directories
- Maintains consistent structure

```bash
# Dry run (see what would be cleaned)
python qclean.py --repo /path/to/repo

# Actually clean the repository
python qclean.py --repo /path/to/repo --apply
```

### 3. qnap 📸
Repository snapshot tool. Manages repository states:
- Creates snapshots
- Restores previous states
- Lists available snapshots

```bash
# Create a snapshot
python qnap.py --repo /path/to/repo create

# List snapshots
python qnap.py --repo /path/to/repo list

# Restore a snapshot
python qnap.py --repo /path/to/repo restore snapshot_name
```

## Configuration 📝

Each tool can be configured using YAML files. Example configuration:

```yaml
# config.yml
ignore_patterns:
  - .git
  - node_modules
  - __pycache__
  - *.pyc
  - .DS_Store
  - venv*
  - volumes

clean_patterns:
  - Miniconda*
  - conda_init*.sh
  - tmp_*
  - *.tmp

organize_dirs:
  services/cortex/models:
    - *.model
    - *.gguf
  services/cortex/metal:
    - *metal*.py
    - *gpu*.py
  services/cortex/api:
    - *api*.py
    - *server*.py
```

## Installation 📦

1. Clone the repository:
```bash
git clone https://github.com/saadfarooq07/quantum-index.git
cd quantum-index
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add to your PATH:
```bash
export PATH=$PATH:/path/to/quantum-index/scripts/qflow
```

## Usage Tips 💡

1. **Regular Maintenance**:
   ```bash
   # Weekly maintenance workflow
   qcheck && qclean --apply && qnap create
   ```

2. **Before Big Changes**:
   ```bash
   # Create a snapshot before major changes
   qnap create --name "before_feature_x"
   ```

3. **After Pulling Updates**:
   ```bash
   # Clean and organize after pulling
   qcheck && qclean --apply
   ```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Submit a pull request

## License

Copyright 2024 Saad Farooq (saad.farooq07@gmail.com)
All rights reserved.
