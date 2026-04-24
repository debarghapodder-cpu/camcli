# CLI Tool Template
This is a template for a modular CLI tool in Python using `argparse`. It's designed to be easily extensible, allowing you to add new commands without major restructuring.

## Structure
- `main.py`: The main entry point that sets up the argument parser and dispatches to command functions.


## Running the Tool

```bash
# Show help
python main.py
```

## Extending Further
For larger projects, consider:
- Moving commands to separate modules (e.g., `commands/` directory)
- Using a more advanced CLI library like `click` or `typer`
- Adding configuration files, logging, etc.