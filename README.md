# Hello world: Streamlit, uv, and Posit Connect

A minimal Streamlit app for a publisher to check whether `uv` is available in
the app's runtime environment. The deployment manifest also requests that
Connect use `uv` to install the Python dependencies when server policy permits.

## Deploy from Git

The repository includes `manifest.json` and `requirements.txt`; generating them
locally is only necessary after changing the app or its dependencies.

1. Sign in to <https://appshareirp.nimh.nih.gov/>.
2. Open **Content > Publish > Import from Git**.
3. Enter `https://github.com/nimh-dsst/uv-streamlit-deploy-test.git`.
4. Select branch **main** and the **repository root** (the directory containing
   `manifest.json`).
5. Name the content and deploy. Save the deployment/build logs for the installer
   check below, then open the app.

Publisher access is sufficient to import Git-backed content. The Git URL uses
HTTPS, as required by Connect. See the server's
[Git-backed publishing guide](https://appshareirp.nimh.nih.gov/__docs__/user/git-backed/).

## Read the result

There are two separate checks:

| Evidence | What it establishes |
| --- | --- |
| The app displays a successful `uv --version` result | An existing `uv` executable is available to the running app. |
| The app cannot find `uv` on its `PATH` | Runtime availability is unconfirmed. Connect may use a separate build environment or installer location. |
| Deployment/build logs show a `uv pip` installer command | Connect used `uv` for that package installation. |
| Deployment/build logs show a `pip` installer command | Connect used `pip` for that package installation. This does not establish whether `uv` is installed elsewhere. |
| The environment was reused from cache | This deployment did not perform a fresh dependency installation; inspect the original build's logs. |

The app only looks up `uv` on `PATH` and runs `uv --version` with a five-second
timeout. Its runtime dependencies do **not** include `uv`, so the app does not
install the tool it is checking. Check results describe the app's execution
environment, which may be a container rather than the Connect host.

In `manifest.json`, `python.package_manager.allow_uv` is `true`. This permits
Connect to use `uv`; it does not require its use or override administrator
settings. `package_manager.name` remains `pip` because that is the documented
manifest schema, even when `uv` is requested. See the
[manifest reference](https://docs.posit.co/connect/user/manifest/#allow_uv).

Connect added the `uv` installer option in **2024.12.0**, initially disabled by
default. Newer releases use it by default, but your server's version and policy
determine its behavior. Connect may provision its own installer during a build,
so build-time use also does not prove that `uv` was installed before deployment.
See the [release notes](https://docs.posit.co/connect/news/#2024120) and
[Python installer configuration](https://docs.posit.co/connect/admin/python/#selecting-package-installer).

## Run locally using uv

```bash
uv sync --python 3.11
uv run streamlit run app.py
```

Open the local URL printed by Streamlit. A local `uv` result describes your
computer; run the deployed app to check the Connect execution environment.

`pyproject.toml` declares Streamlit as the only application dependency.
`uv.lock` locks the development environment; `requirements.txt` exports only
application dependencies for Connect. `rsconnect-python` is a development tool.
Streamlit is restricted to versions below `1.57` because the current Connect
[release notes](https://docs.posit.co/connect/news/) document a compatibility
restriction starting at that version.

The manifest is generated with Python **3.11**. If Connect reports that no
compatible Python installation is available, use a version offered by your
server and regenerate the manifest with that interpreter. The project allows
Python 3.10 through 3.13; package availability may impose further limits.

## Update the deployment files

After editing `app.py` or changing dependencies, run from the repository root:

```bash
uv sync
uv run python write_manifest.py
git add app.py write_manifest.py pyproject.toml uv.lock .python-version requirements.txt manifest.json README.md .gitignore
git commit -m "Update Streamlit uv deployment check"
git push origin main
```

Then select **Settings > Source > Update Now** in Connect or wait for Git polling.
Keep the generated manifest committed alongside the app. Manifest generation
does not require a Connect API key. See the
[Streamlit manifest command](https://docs.posit.co/rsconnect-python/commands/write-manifest/#write-manifest-streamlit).

`write_manifest.py` exports runtime dependencies from `uv.lock`, invokes the
official manifest generator, and explicitly writes `allow_uv: true`. This last
step handles an observed issue in `rsconnect-python` 1.32.0, which accepts
`--package-installer UV` for Streamlit but omits the preference from its output.
