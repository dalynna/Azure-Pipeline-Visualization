# 2025 CSUSM SE Capstone Team 2

## Required

- [VS Code](https://code.visualstudio.com/download)
  - Requires installing Python Extension
- [Python (v3.12.0)](https://www.python.org/downloads/)
- [Visual Studio Build Tools (Desktop Development for C++)](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) ![alt](https://code.visualstudio.com/assets/docs/cpp/msvc/desktop_development_with_cpp-2022.png)

## Installation Steps

1. `git clone https://github.com/uhhrace/2023-capstone.git`
2. `cd ./2023-capstone`
3. `pip install -r requirements.txt`

## Launch Configurations

There are currently a handful of launch configurations setup, we'll mostly be using `Build SVG` and `Debug all tests` for the first stage.

## User Guide

1. Open the project in VS Code

2. Modify `config\yml_url_config.json` to fit your project:

3. `yml_filepath` is a list of filepaths to the yml files that will be included in the VSM. Either absolute filepaths or relative filepaths can be used.

4. The order of the yml files is important. The system will attempt to compensate for any errors in the order, but it is best to have the yml files in the correct order. If a pipeline is dependent on another pipeline, put the parent pipeline above the child pipeline.

5. If you see a gray box where a pipeline isn't found, check to make sure that the pipeline name matches the first element 
    in the config file array (yml_filepath)

6. `template_dictionary` is a list of filepaths to template files required by the various yml files. The order of the template files is not important. Either absolute filepaths or relative filepaths can be used.

7. The system will generate a single SVG file including all pipelines and their connections. 

8. The SVG file will be named after the final pipeline in the list of yml files.
