"""Hello world and a read-only uv check in the application's runtime environment."""

import platform
import shutil
import subprocess
import sys

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="Hello, Posit Connect!")
    st.title("Hello, world!")
    st.write("Streamlit is running. Let's check whether this app can run uv.")

    st.subheader("uv availability")
    uv_path = shutil.which("uv")
    if uv_path is None:
        st.warning("uv was not found on this application's PATH.")
        st.write(
            "This result is inconclusive for Connect's package installer. "
            "Connect may have uv in a separate build environment or location."
        )
    else:
        st.code(uv_path, language="text")
        try:
            result = subprocess.run(
                [uv_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            st.warning("uv was found, but the version check failed.")
            st.code(str(exc), language="text")
        else:
            if result.returncode == 0:
                st.success("uv is available to this application.")
            else:
                st.warning(f"uv --version exited with code {result.returncode}.")
            st.code(
                result.stdout.strip() or result.stderr.strip() or "No output.",
                language="text",
            )

    st.info(
        "To confirm whether Connect used uv to install Streamlit, check this "
        "content's deployment/build logs for the package installer command. "
        "An available uv executable or a successful deployment alone does not "
        "identify the installer used."
    )
    with st.expander("Runtime details"):
        st.json(
            {
                "python_version": platform.python_version(),
                "python_executable": sys.executable,
                "streamlit_version": st.__version__,
            }
        )


if __name__ == "__main__":
    main()
