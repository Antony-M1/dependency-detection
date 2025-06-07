import argparse
import subprocess
import os
import time
import json
import shutil
import pandas as pd
from logger import get_logger

logger = get_logger('main', 'main.log')

ENV_NAME = 'temp_venv'


def get_start():
    get_all_the_versions()
    package_info = read_json_file(package_info_path)
    releases = get_releases(package_info)
    prime_packages = list(set(cli_arg.prime_package.split(',')))
    global DATA
    DATA = {
        f'{cli_arg.package_name}_version': []
    }
    for prime_package in prime_packages:
        DATA[prime_package.lower()] = []

    for release in releases:
        try:
            freeze_list = install_package_in_env(release)
            for prime_package in prime_packages:
                is_update = False
                for package in freeze_list:
                    _package_name, _version = package.split('==')
                    if prime_package.lower() == _package_name.lower():
                        package_name = prime_package.lower()
                        version = _version
                        DATA[package_name].append(version)
                        is_update = True
                        break
                if not is_update:
                    DATA[prime_package.lower()].append(None)
            DATA[f'{cli_arg.package_name}_version'].append(release)

        except subprocess.CalledProcessError as e:
            logger.error(f"Issue in Subprocess {cli_arg.package_name}=={release}: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
        except Exception as e:
            logger.critical(f"An unexpected error occurred while installing {cli_arg.package_name}=={release}: {e}")

    df = pd.DataFrame(DATA)
    df.to_csv(f'temp/{cli_arg.package_name}/{cli_arg.package_name}_versions.csv', index=False)
    logger.info(f"Data saved to temp/{cli_arg.package_name}/{cli_arg.package_name}_versions.csv")


def delete_virtual_env_v2():
    """Delete the virtual environment folder if it exists."""
    if os.path.exists(ENV_NAME) and os.path.isdir(ENV_NAME):
        shutil.rmtree(ENV_NAME)
        logger.info(f"Virtual environment '{ENV_NAME}' deleted successfully.")
    else:
        logger.warning(f"Virtual environment '{ENV_NAME}' does not exist or is not a directory.")


def delete_virtual_env():
    """Delete the virtual environment if it exists."""
    if os.path.exists(ENV_NAME):
        cmd = ['rm', '-rf', ENV_NAME] if os.name != 'nt' else ['rmdir', '/S', '/Q', ENV_NAME]
        subprocess.run(cmd, check=True)
        logger.info(f"Virtual environment '{ENV_NAME}' deleted successfully.")
    else:
        logger.warning(f"Virtual environment '{ENV_NAME}' does not exist.")


def install_package_in_env(release):
    delete_virtual_env_v2()
    time.sleep(1)
    create_virtual_env()
    time.sleep(1)
    # Get platform-specific Python path inside venv
    global PYTHON_PATH
    PYTHON_PATH = (
        f"{ENV_NAME}/Scripts/python.exe" if os.name == "nt"
        else f"{ENV_NAME}/bin/python"
    )

    package_name = f"{cli_arg.package_name}=={release}"
    cmd = [
        PYTHON_PATH,
        '-m', 'pip', 'install', "--no-cache-dir", package_name
    ]
    subprocess.run(cmd, check=True)
    logger.info(f"Package {package_name} installed successfully in the virtual environment.")
    logger.info(f"Available releases: {', '.join(get_releases(read_json_file(package_info_path)))}")

    freeze_file_name = f"temp/{cli_arg.package_name}/{cli_arg.package_name}_{release}.txt"
    os.makedirs(os.path.dirname(freeze_file_name), exist_ok=True)

    with open(freeze_file_name, "w") as f:
        subprocess.run([PYTHON_PATH, "-m", "pip", "freeze"], stdout=f, check=True)

    if os.path.exists(freeze_file_name):
        logger.info(f"Freeze file {freeze_file_name} created successfully.")
    else:
        raise FileNotFoundError(f"Freeze file {freeze_file_name} was not created.")

    lines = read_lines_from_file(freeze_file_name)
    return lines


def read_lines_from_file(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]


def create_virtual_env():
    cmd = [
        'python3',
        '-m', 'venv',
        ENV_NAME
    ]
    subprocess.run(cmd, check=True)
    logger.info(f"Virtual environment '{ENV_NAME}' created successfully.")


def get_releases(package_info: dict) -> list:
    release = list(package_info.get('releases', {}).keys())
    if not release:
        raise ValueError("No releases found for the specified package.")
    return release


def read_json_file(filepath: str) -> dict:
    """Read a JSON file and return it as a dictionary."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def get_all_the_versions():
    os.makedirs(f"temp/{cli_arg.package_name}", exist_ok=True)
    global package_info_path
    package_info_path = f'temp/{cli_arg.package_name}/{cli_arg.package_name}.json'
    cmd = [
        "curl",
        "-s",
        f"https://pypi.org/pypi/{cli_arg.package_name}/json",
        "-o",
        package_info_path
    ]
    subprocess.run(cmd, check=True)


def set_args():
    global cli_arg
    parser = argparse.ArgumentParser()

    parser.add_argument("--package-name", dest='package_name', type=str, required=True, help="Python Package name like pandas")
    parser.add_argument("--prime-package", dest='prime_package', type=str, required=True, help="Prime Package means we are looking for a package that that matches for the our package seperated by comma, like pandas, numpy")

    cli_arg = parser.parse_args()


def main():
    try:
        set_args()
        get_start()
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while executing the command: {e}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except ValueError as e:
        logger.error(f"Value error: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    logger.info('Starting the application...')
    main()