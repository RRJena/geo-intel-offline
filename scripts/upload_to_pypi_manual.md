# Upload to PyPI - Manual Instructions

Twine is now installed. You need to run the upload command manually in your terminal to enter credentials.

## Quick Upload

Run this command in your terminal:

```bash
cd /home/king/myWorkspace/geoIntelLib
python3 -m twine upload build/*.whl build/*.tar.gz
```

## When Prompted

### Option 1: Using API Token (Recommended)

**Username:** `__token__`  
**Password:** `pypi-AgEI...` (your PyPI API token)

**Get API Token:**
1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it (e.g., "geo-intel-offline")
4. Copy the token (starts with `pypi-`)
5. Use `__token__` as username and the token as password

### Option 2: Using Username/Password

**Username:** Your PyPI username  
**Password:** Your PyPI password

## Test Upload First (Optional)

Test on Test PyPI first:

```bash
python3 -m twine upload --repository testpypi build/*.whl build/*.tar.gz
```

Then test install:
```bash
pip install -i https://test.pypi.org/simple/ geo-intel-offline
```

## After Upload

Once uploaded, your package will be available at:
- https://pypi.org/project/geo-intel-offline/

Install with:
```bash
pip install geo-intel-offline
```
