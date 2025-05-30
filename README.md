# Dependency Detection

The process works as follows:
It creates a JSON file containing information about the package releases. Then, for each release, it loops through and performs the following steps:

1. Creates a new environment.

2. Installs the specified package.

3. Retrieves the details of the installed package from the environment.

4. Deletes the environment after collecting the information.

This process is repeated for each release in the list.

# Create Venv for a project

Create `.venv` for the project and activate and use that project using the below commands

```
python -m venv .venv
```
for windows
```
.venv/scripts/activate
```

# Run

```
python main.py --package-name langchain-google-genai --prime-package google-auth,tenacity,typing-extensions
```