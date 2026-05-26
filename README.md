# mpas-tutorial

_A mini tutorial for standalone MPAS-A._

## Building this site

### Setup

```bash
conda env create -f environment.yml
conda activate mpas-tutorial
```

### Build

For development (runs a local server and watches for changes):

```bash
jupyter book start
```

For deployment (generates static HTML files in `_build/html/`):

```bash
jupyter book build --html
```
