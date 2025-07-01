import os
import json
import requests
from unittest.mock import patch, MagicMock, mock_open
import pytest
from dotenv import load_dotenv
from YMLParser import parser
import YMLParser
from YMLParser.parser import (
    Pipeline,
    Job,
    localParser,
    apiParser,
    parse_trigger,
    cron_descriptor,
    find_and_parse_template,
    find_template_repo,
    get_template_path,
    parse_yml_file,
    is_URL,
    TASK_NAMES_IGNORE_CASE,
    TASK_ALIAS_MAP,
    deep_search_single,
    deep_search_multi,
    createPipeline,
    parse_jobs,
    parse_job_tasks
)

@pytest.fixture
def mock_config_file():
    return {
        "template_dictionary": [
            "templates/template1.yml",
            "templates/subfolder/template2.yml",
            "/absolute/path/template3.yml"
        ]
    }

def test_parse_yml_file_invalid_input():
    # Test with insufficient parameters
    result = parse_yml_file(["only_one_param"])
    assert result is None

def test_local_parser_valid_file():
    test_yaml_content = """
    trigger:
      - main
    pool:
      vmImage: ubuntu-latest
    """
    mock_file = mock_open(read_data=test_yaml_content)
    
    with patch("builtins.open", mock_file):
        result = localParser.parse_yml("test_pipeline", "local/path/file.yml")
    
    assert result is not None
    assert result["name"] == "test_pipeline"
    assert result["origin"] == "local/path/file.yml"

def test_local_parser_file_not_found():
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        result = localParser.parse_yml("test_pipeline", "nonexistent/file.yml")
    
    assert result is None

def test_local_parser_unsafe_load():
    test_yaml_content = """
    !!python/object:test
    attr: value
    """
    mock_file = mock_open(read_data=test_yaml_content)
    
    with patch("builtins.open", mock_file), \
         patch("yaml.safe_load", side_effect=Exception("safe_load failed")), \
         patch("yaml.unsafe_load") as mock_unsafe_load:
        
        mock_unsafe_load.return_value = {"attr": "value"}
        result = localParser.parse_yml("test_pipeline", "local/path/file.yml")
    
        assert result is not None
        assert result["name"] == "test_pipeline"
        assert result["origin"] == "local/path/file.yml"
        assert result["attr"] == "value"
        mock_unsafe_load.assert_called_once()

@patch('YMLParser.parser.requests')
@patch('YMLParser.parser.load_dotenv')
def test_parse_yml_file_url(mock_load_dotenv, mock_requests):
    # Setup mock environment
    mock_load_dotenv.return_value = None
    os.environ['PAT'] = 'fake_pat'
    os.environ['ORG_URL'] = 'https://dev.azure.com/fake-org'
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content.decode.return_value = """
    name: test_pipeline
    trigger:
      - main
    """
    mock_requests.get.return_value = mock_response

    # Test the function
    result = parse_yml_file(["test_pipeline", "https://example.com/pipeline.yml"])
    
    # Verify results
    assert result is not None
    assert result["name"] == "test_pipeline"
    mock_requests.get.assert_called_once()

@patch('YMLParser.parser.requests')
@patch('YMLParser.parser.load_dotenv')
def test_parse_yml_file_url_failure(mock_load_dotenv, mock_requests):
    # Setup mock environment
    mock_load_dotenv.return_value = None
    os.environ['PAT'] = 'fake_pat'
    os.environ['ORG_URL'] = 'https://dev.azure.com/fake-org'
    
    # Setup mock response for failure
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.get.return_value = mock_response

    # Test the function
    result = parse_yml_file(["test_pipeline", "https://example.com/pipeline.yml"])
    
    # Verify results
    assert result is None
    mock_requests.get.assert_called_once()

def test_parse_yml_file_local_file_not_found():
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        result = parse_yml_file(["test_pipeline", "nonexistent/file.yml"])
    
    assert result is None

def test_parse_yml_file_local_invalid_yaml():
    invalid_yaml = "invalid: yaml: content: - ["
    mock_file = mock_open(read_data=invalid_yaml)
    
    with patch("builtins.open", mock_file):
        result = parse_yml_file(["test_pipeline", "local/path/file.yml"])
    
    assert result is not None  # Should return a basic structure even with invalid YAML
    assert result["name"] == "test_pipeline"  # Should contain the pipeline name
    assert result["origin"] == "local/path/file.yml"  # Should contain the file path

def test_set_name():
    pipeline = Pipeline()
    pipeline.setName("New Pipeline Name")
    assert pipeline.getName() == "New Pipeline Name"


def test_set_os():
    pipeline = Pipeline()
    pipeline.setOS("Windows")
    assert pipeline.getOS() == "Windows"


def test_add_language():
    pipeline = Pipeline()
    pipeline.addLanguage("Python")
    pipeline.addLanguage("JavaScript")
    assert pipeline.getLanguages() == ["Python", "JavaScript"]


def test_add_job():
    pipeline = Pipeline()
    pipeline.addJob("Build")
    pipeline.addJob("Test")
    assert pipeline.getJobs() == ["Build", "Test"]


def test_add_task():
    pipeline = Pipeline()
    pipeline.addTask("Compile")
    pipeline.addTask("Lint")
    assert pipeline.getTasks() == ["Compile", "Lint"]


def test_set_trigger():
    pipeline = Pipeline()
    pipeline.setTrigger("Manual")
    assert pipeline.getTrigger() == "Manual"


def test_add_artifact():
    pipeline = Pipeline()
    pipeline.addArtifact("Build Artifact")
    pipeline.addArtifact("Test Artifact")
    assert pipeline.getArtifacts() == ["Build Artifact", "Test Artifact"]


def test_set_origin():
    pipeline = Pipeline()
    pipeline.setOrigin("https://github.com/user/repo")
    assert pipeline.getOrigin() == "https://github.com/user/repo"


def test_add_dependency():
    pipeline = Pipeline()
    pipeline.addDependency("Dependency 1")
    pipeline.addDependency("Dependency 2")
    assert pipeline.getDependencies() == ["Dependency 1", "Dependency 2"]


def test_set_x():
    pipeline = Pipeline()
    pipeline.setX(10)
    assert pipeline.getX() == 10


def test_set_y():
    pipeline = Pipeline()
    pipeline.setY(20)
    assert pipeline.getY() == 20


def test_Pipeline_setName():
    # Arrange
    pipeline = Pipeline()  # Use Pipeline instead of parser.Pipeline

    # Act
    pipeline.setName("New Pipeline Name")

    # Assert
    assert pipeline.getName() == "New Pipeline Name"


def test_Pipeline_getName():
    # Arrange
    pipeline = Pipeline()
    pipeline.setName("Great Pipeline!")

    # Act & Assert
    assert pipeline.getName() == "Great Pipeline!"


def test_Pipeline_setOS():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.setOS("Windows")

    # Assert
    assert pipeline.getOS() == "Windows"


def test_Pipeline_getOS():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getOS() is None


def test_Pipeline_addLanguage():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.addLanguage("Python")
    pipeline.addLanguage("JavaScript")

    # Assert
    assert pipeline.getLanguages() == ["Python", "JavaScript"]


def test_Pipeline_getLanguages():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getLanguages() == []


def test_Pipeline_addJob():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.addJob("Build")
    pipeline.addJob("Test")

    # Assert
    assert pipeline.getJobs() == ["Build", "Test"]


def test_Pipeline_getJobs():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getJobs() == []


def test_Pipeline_addTask():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.addTask("Compile")
    pipeline.addTask("Lint")

    # Assert
    assert pipeline.getTasks() == ["Compile", "Lint"]


def test_Pipeline_getTasks():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getTasks() == []


def test_Pipeline_setTrigger():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.setTrigger("testB.yml")

    # Assert
    assert pipeline.getTrigger() == "testB.yml"


def test_Pipeline_getTrigger():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getTrigger() is None


def test_Pipeline_addArtifact():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.addArtifact("Build Artifact")
    pipeline.addArtifact("Test Artifact")

    # Assert
    assert pipeline.getArtifacts() == ["Build Artifact", "Test Artifact"]


def test_Pipeline_getArtifacts():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getArtifacts() == []


def test_Pipeline_setOrigin():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.setOrigin("repository")

    # Assert
    assert pipeline.getOrigin() == "repository"


def test_Pipeline_getOrigin():
    # Arrange
    pipeline = Pipeline()
    pipeline.setOrigin("my butt")

    # Act & Assert
    assert pipeline.getOrigin() == "my butt"


def test_Pipeline_addDependency():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.addDependency("Dependency A")
    pipeline.addDependency("Dependency B")

    # Assert
    assert pipeline.getDependencies() == ["Dependency A", "Dependency B"]


def test_Pipeline_getDependencies():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getDependencies() == []


def test_Pipeline_setX():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.setX(10)

    # Assert
    assert pipeline.getX() == 10


def test_Pipeline_getX():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getX() == 0


def test_Pipeline_setY():
    # Arrange
    pipeline = Pipeline()

    # Act
    pipeline.setY(20)

    # Assert
    assert pipeline.getY() == 20


def test_Pipeline_getY():
    # Arrange
    pipeline = Pipeline()

    # Act & Assert
    assert pipeline.getY() == 0


def test_parseTrigger():
    # Create a sample YAML object for the test pipeline
    yaml_data = {
        "trigger": {
            "branches": {
                "include": ["main"]
            }
        }
    }

    # Use the directly imported createPipeline function
    testPipeline = createPipeline(yaml_data)
    assert testPipeline is not None
    assert testPipeline.getTrigger() == "main"

    # Test exclude case
    yaml_data_exclude = {
        "trigger": {
            "branches": {
                "exclude": ["master"]
            }
        }
    }
    testPipeline = createPipeline(yaml_data_exclude)
    assert testPipeline is not None
    assert testPipeline.getTrigger() == "- not master"

    # Test schedule case
    yaml_data_schedule = {
        "schedules": [{
            "cron": "0 0 * * *"
        }]
    }
    testPipeline = createPipeline(yaml_data_schedule)
    assert testPipeline is not None
    assert testPipeline.getTrigger() is not None


def test_createPipeline_happy_path():
    # Arrange
    yaml_data = {
        "name": "Sample Pipeline2",
        "trigger": "testB.yml",
        "origin": "repository",
        "children": ["testA.yml", "testB.yml"],
    }

    # Act
    testPipeline = parser.createPipeline(yaml_data)

    # Assert
    # TODO Research how to make a mock object for unit testing
    assert testPipeline.getName() == yaml_data["name"]
    assert testPipeline.getTrigger() == yaml_data["trigger"]
    assert testPipeline.getOrigin() == yaml_data["origin"]


def test_createPipeline_fanOut():
    # Arrange
    yaml_data_1 = {"name": "Stage1"}

    yaml_data_2A = {
        "name": "Stage2A",
        "resources": {
            "pipelines": [{"pipeline": "stage_1_to_stage_2A", "source": "Stage 1"}]
        },
    }

    yaml_data_2B = {
        "name": "Stage2B",
        "resources": {
            "pipelines": [{"pipeline": "stage_1_to_stage_2B", "source": "Stage 1"}]
        },
    }

    # Act
    testPipeline_1 = parser.createPipeline(yaml_data_1)
    testPipeline_2A = parser.createPipeline(yaml_data_2A)
    testPipeline_2B = parser.createPipeline(yaml_data_2B)

    # Assert
    # Test 2B and 2A are dependent on 1
    assert len(testPipeline_2A.getDependencies()) == 1
    assert len(testPipeline_2B.getDependencies()) == 1
    assert testPipeline_2A.getDependencies()[0].getName() == "Stage 1"
    assert testPipeline_2B.getDependencies()[0].getName() == "Stage 1"

    # Test 1 is not dependent on anything
    assert testPipeline_1.getDependencies() == []
    assert testPipeline_1.getDependencies() == []

    # Test 2A and 2B are not dependent on each other
    assert len(testPipeline_2A.getDependencies()) == 1
    assert len(testPipeline_2B.getDependencies()) == 1
    assert testPipeline_2A.getDependencies()[0] != "Stage 2B"
    assert testPipeline_2B.getDependencies()[0] != "Stage 2A"


def test_createPipeline_fanIn():
    # Arrange
    YAMLData_2 = {"name": "Stage2"}

    YAMLData_3 = {"name": "Stage3"}

    YAMLData_4 = {
        "name": "Stage4",
        "resources": {
            "pipelines": [
                {"pipeline": "Stage_2_to_Stage_4", "source": ["Stage_2"]},
                {"pipeline": "Stage_3_to_Stage_4", "source": ["Stage_3"]},
            ]
        },
    }

    # Creating pipelines from YAML data above to show fanning back in
    test_Pipeline2 = parser.createPipeline(YAMLData_2)
    test_Pipeline3 = parser.createPipeline(YAMLData_3)
    test_Pipeline4 = parser.createPipeline(YAMLData_4)

    # Assert
    # Checking the pipeline names
    assert test_Pipeline2.getName() == "Stage2"
    assert test_Pipeline3.getName() == "Stage3"
    assert test_Pipeline4.getName() == "Stage4"

    # checking the pipeline Dependencies for stage 4 pipeline
    assert len(test_Pipeline4.getDependencies()) == 2
    assert test_Pipeline4.getDependencies()[0].getName() == ["Stage_2"]
    assert test_Pipeline4.getDependencies()[1].getName() == ["Stage_3"]


def test_createPipeline_fanInNOutMany():
    # TODO Arrange the pipelines with fanning in and out as shown below.

    # 2         #4A          #5A     #6
    # 1       #4    #4B     #5           #7
    # 3         #4C
    # 4D          #5B     #8

    yaml_data_1 = {"name": "Stage_1"}

    yaml_data_2 = {
        "name": "Stage_2",
        "resources": {
            "pipelines": [{"pipeline": "stage_1_to_stage_2", "source": "Stage_1"}]
        },
    }

    yaml_data_3 = {
        "name": "Stage_3",
        "resources": {
            "pipelines": [{"pipeline": "stage_1_to_stage_3", "source": "Stage_1"}]
        },
    }

    yaml_data_4 = {
        "name": "Stage_4",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4_from_2", "source": ["Stage_2"]},
                {"pipeline": "Stage_4_from_3", "source": ["Stage_3"]},
            ]
        },
    }

    yaml_data_4A = {
        "name": "Stage_4A",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4_to_Stage4A", "source": ["Stage_4"]}
            ]
        },
    }

    yaml_data_4B = {
        "name": "Stage_4B",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4_to_Stage4B", "source": ["Stage_4"]}
            ]
        },
    }

    yaml_data_4C = {
        "name": "Stage_4C",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4_to_Stage4C", "source": ["Stage_4"]}
            ]
        },
    }

    yaml_data_4D = {
        "name": "Stage_4D",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4_to_Stage4D", "source": ["Stage_4"]}
            ]
        },
    }

    yaml_data_5 = {
        "name": "Stage_5",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_4A_to_5", "source": ["Stage_4A"]},
                {"pipeline": "Stage_4B_to_5", "source": ["Stage_4B"]},
                {"pipeline": "Stage_4C_to_5", "source": ["Stage_4C"]},
                {"pipeline": "Stage_4D_to_5", "source": ["Stage_4D"]},
            ]
        },
    }

    yaml_data_5A = {
        "name": "Stage_5A",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_5A_from Stage5", "source": ["Stage_5"]}
            ]
        },
    }

    yaml_data_5B = {
        "name": "Stage_5B",
        "resources": {
            "pipelines": [  # this is the name of the pipeline
                {"pipeline": "Stage_5_to_Stage5A", "source": ["Stage_5"]}
            ]
        },
    }

    yaml_data_6 = {
        "name": "Stage_6",
        "resources": {
            "pipelines": [{"pipeline": "Stage_5A_to_Stage_6", "source": "Stage_5A"}]
        },
    }

    yaml_data_7 = {
        "name": "Stage_7",
        "resources": {
            "pipelines": [{"pipeline": "Stage_5A_to_Stage_7", "source": "Stage_5A"}]
        },
    }

    yaml_data_8 = {
        "name": "Stage_8",
        "resources": {
            "pipelines": [{"pipeline": "Stage_5B_to_Stage_8", "source": "Stage_5B"}]
        },
    }

    # Creating pipelines from YAML data above to show fanning in and out
    test_Pipeline1 = parser.createPipeline(yaml_data_1)
    test_Pipeline2 = parser.createPipeline(yaml_data_2)
    test_Pipeline3 = parser.createPipeline(yaml_data_3)
    test_Pipeline4 = parser.createPipeline(yaml_data_4)
    test_Pipeline4A = parser.createPipeline(yaml_data_4A)
    test_Pipeline4B = parser.createPipeline(yaml_data_4B)
    test_Pipeline4C = parser.createPipeline(yaml_data_4C)
    test_Pipeline4D = parser.createPipeline(yaml_data_4D)
    test_Pipeline5 = parser.createPipeline(yaml_data_5)
    test_Pipeline5A = parser.createPipeline(yaml_data_5A)
    test_Pipeline5B = parser.createPipeline(yaml_data_5B)
    test_Pipeline6 = parser.createPipeline(yaml_data_6)
    test_Pipeline7 = parser.createPipeline(yaml_data_7)
    test_Pipeline8 = parser.createPipeline(yaml_data_8)

    # Assert the name and number of dependencies of each fan out
    assert test_Pipeline4.getName() == "Stage_4"
    assert len(test_Pipeline4.getDependencies()) == 2
    assert test_Pipeline4.getDependencies()[0].getName() == ["Stage_2"]
    assert test_Pipeline4.getDependencies()[1].getName() == ["Stage_3"]

    assert test_Pipeline5.getName() == "Stage_5"
    assert len(test_Pipeline5.getDependencies()) == 4
    assert test_Pipeline5.getDependencies()[0].getName() == ["Stage_4A"]
    assert test_Pipeline5.getDependencies()[1].getName() == ["Stage_4B"]
    assert test_Pipeline5.getDependencies()[2].getName() == ["Stage_4C"]
    assert test_Pipeline5.getDependencies()[3].getName() == ["Stage_4D"]

    assert test_Pipeline5A.getName() == "Stage_5A"
    assert len(test_Pipeline5A.getDependencies()) == 1
    assert test_Pipeline5A.getDependencies()[0].getName() == ["Stage_5"]

    assert test_Pipeline5B.getName() == "Stage_5B"
    assert len(test_Pipeline5B.getDependencies()) == 1
    assert test_Pipeline5B.getDependencies()[0].getName() == ["Stage_5"]

    assert test_Pipeline6.getName() == "Stage_6"
    assert len(test_Pipeline6.getDependencies()) == 1
    assert test_Pipeline6.getDependencies()[0].getName() == "Stage_5A"

    assert test_Pipeline7.getName() == "Stage_7"
    assert len(test_Pipeline7.getDependencies()) == 1
    assert test_Pipeline7.getDependencies()[0].getName() == "Stage_5A"

    assert test_Pipeline8.getName() == "Stage_8"
    assert len(test_Pipeline8.getDependencies()) == 1
    assert test_Pipeline8.getDependencies()[0].getName() == "Stage_5B"


def test_is_URL():
    # Arrange
    url = "https://www.example.com"
    non_url = "C:\\example\\file.txt"

    # Act & Assert
    assert parser.is_URL(url) == True
    assert parser.is_URL(non_url) == False


# TODO Implement test for parsing a template file
@pytest.mark.xfail(reason="Draft for templates")
# Testing for template files
def test_single_template():
    # This test will be parsing a template file.

    # Arrange;

    yaml_data_template = {"name": "Stage_1", "job": "template_job"}

    yaml_data_2 = {
        "name": "Stage_2",
        "resources": {
            "pipelines": [{"pipeline": "Stage_1_to_Stage_2", "source": "Stage_1"}]
        },
    }

    # Assert  that func was called
    # https://stackoverflow.com/questions/3829742/assert-that-a-method-was-called-in-a-python-unit-test

    # Act
    # pipeline = YMLParser.createPipeline(yaml_data_2)

    with patch.object(YMLParser, "parseTemp") as mock:
        pipeline = YMLParser.createPipeline(yaml_data_2)

    mock.assert_called_with("Stage_1")

    # Assert; whatever is inside the teemplate file is inside the parent template file.


def test_parse_trigger():

    # Create YAML data with No cron section
    YML_data = {
        "name": "Stage_1",
        "schedules": [{"cron": "0 15 * * Fri", "displayName": "Friday 8am PT Trigger"}],
    }

    # call parse_trigger function by itself, no need to make a pipeline object.
    result = parse_trigger(YML_data)

    # Asserting the displayName of this pipeline.
    assert result == "At 03:00 PM, only on Friday"


def test_cron_Expression_found():

    # Arrange: Create expression
    cron_expression = "0 29 * * 7"

    # Act: call the function
    result = cron_descriptor(cron_expression)

    # Assert: the result
    assert result == "At 17:00 PM, only on Sunday"


def test_incomplete_cron_message_found():

    # Arrange: Create expression of 5 parts, need 5 to work!
    cron_expression = "0 * * 2 "

    # Act: call the function
    result = cron_descriptor(cron_expression)

    # Assert: the result
    assert (
        result
        == "Error generating description: Error: Expression only has 4 parts.  At least 5 part are required."
    )


def test_no_Cron_message_found():

    # Arrange: Create expression
    cron_expression = ""

    # Act: call the function
    result = cron_descriptor(cron_expression)

    # Assert: the result
    assert result == "No cron expression provided"


def test_find_and_parse_template_local():

    # Arrange
    expectedPath = "pathToTemplate.yml"
    expectedRepo = ""

    params = {
        "steps": [
            # No @ symbol in path
            {"template": expectedPath}
        ]
    }

    # Act
    # Mock parseTemplate and spy on the parameters
    with patch("YMLParser.parser.parseTemplate") as mock:
        find_and_parse_template(params)

    # Assert that the function was called with the correct parameters
    assert "@" not in expectedPath
    mock.assert_called_with(expectedPath, expectedRepo)


def test_and_parse_template_remote():
    # Arrange
    expectedPath = "expectedPathToTemplate.yml"
    expectedRepo = "testRepoName"
    expectedCombo = "@".join([expectedRepo, expectedPath])

    params = {
        "steps": [
            # @ symbol in path, represents a remote template
            {"template": expectedCombo}
        ]
    }

    # Mock the functions we're not testing
    with patch('YMLParser.parser.get_template_path') as mock_get_path, \
         patch('YMLParser.parser.find_template_repo') as mock_find_repo, \
         patch('YMLParser.parser.parseTemplate') as mock_parse_template:
        
        # Setup mock returns
        mock_get_path.return_value = expectedPath
        mock_find_repo.return_value = expectedRepo
        
        # Act
        find_and_parse_template(params)

        # Assert
        mock_parse_template.assert_called_once_with(expectedPath, expectedRepo)


def test_and_parse_template_not_found():
    # Arrange
    expectedPath = "expectedPathToTemplate.yml"
    expectedRepo = "testRepoName"

    params = {
        "steps": [
            # @ symbol in path, represents a remote template
            {"template": "@".join([expectedRepo, expectedPath])}
        ]
    }

    # Mock the functions we're not testing
    with patch('YMLParser.parser.get_template_path', return_value=None), \
         patch('YMLParser.parser.find_template_repo', return_value=None), \
         patch('YMLParser.parser.parseTemplate') as mock_parse_template:
        
        # Act
        template = find_and_parse_template(params)

        # Assert
        mock_parse_template.assert_not_called()
        assert template is None


def test_find_template_repo_existing_repo():
    # Arrange
    repoName = "repo1"
    params = {
        "resources": {
            "repositories": [
                {"repository": "repo1", "name": "Repo 1"},
                {"repository": "repo2", "name": "Repo 2"},
            ]
        }
    }

    # Act
    result = find_template_repo(repoName, params)

    # Assert
    assert result == "Repo 1"


def test_find_template_repo_non_existing_repo():
    # Arrange
    repoName = "repo3"
    params = {
        "resources": {
            "repositories": [
                {"repository": "repo1", "name": "Repo 1"},
                {"repository": "repo2", "name": "Repo 2"},
            ]
        }
    }

    # Act
    result = find_template_repo(repoName, params)

    # Assert
    assert result is None


def test_find_template_repo_no_repositories():
    # Arrange
    repoName = "repo1"
    params = {"resources": {}}

    # Act
    result = find_template_repo(repoName, params)

    # Assert
    assert result is None

def test_api_parser_missing_env_vars():
    with patch('dotenv.load_dotenv', side_effect=Exception):
        result = apiParser.parse_yml("test_pipeline", "https://example.com/pipeline.yml")
        assert result is None

def test_api_parser_invalid_url():
    result = apiParser.parse_yml("test_pipeline", "not_a_url")
    assert result is None

def test_parse_yml_file_empty_input():
    result = parse_yml_file([])
    assert result is None

def test_parse_yml_file_single_input():
    result = parse_yml_file(["only_one_parameter"])
    assert result is None

def test_local_parser_empty_file():
    mock_file = mock_open(read_data="")
    with patch("builtins.open", mock_file):
        result = localParser.parse_yml("test_pipeline", "local/path/file.yml")
        assert result is not None
        assert result["name"] == "test_pipeline"
        assert result["origin"] == "local/path/file.yml"

def test_local_parser_non_dict_yaml():
    # Test handling of YAML that parses to a non-dictionary value
    mock_file = mock_open(read_data="- item1\n- item2")
    with patch("builtins.open", mock_file):
        result = localParser.parse_yml("test_pipeline", "local/path/file.yml")
        assert result is not None
        assert isinstance(result, dict)
        assert "content" in result
        assert result["name"] == "test_pipeline"

def test_api_parser_network_error():
    with patch('requests.get', side_effect=requests.exceptions.RequestException):
        result = apiParser.parse_yml("test_pipeline", "https://example.com/pipeline.yml")
        assert result is None

def test_local_parser_complex_yaml():
    complex_yaml = """
    name: complex_pipeline
    trigger:
      branches:
        include:
          - main
          - develop
    stages:
      - stage: Build
        jobs:
          - job: BuildJob
            steps:
              - script: echo "Building"
    """
    mock_file = mock_open(read_data=complex_yaml)
    with patch("builtins.open", mock_file):
        result = localParser.parse_yml("test_pipeline", "local/path/file.yml")
        assert result is not None
        assert "stages" in result
        assert result["trigger"]["branches"]["include"] == ["main", "develop"]

def test_is_url_function():
    assert is_URL("https://example.com") is True
    assert is_URL("http://example.com") is True
    assert is_URL("local/path/file.yml") is False
    assert is_URL("") is False
    assert is_URL(None) is False

def test_task_alias_mapping():
    # Test that task names are properly mapped
    assert "Python" in TASK_NAMES_IGNORE_CASE
    assert "python" in TASK_NAMES_IGNORE_CASE
    assert TASK_ALIAS_MAP["python"] == "Python"
    assert TASK_ALIAS_MAP["dotnet"] == ".NET"

def test_deep_search_single_task():
    yaml_with_task = {
        "stages": [{
            "jobs": [{
                "steps": [{
                    "task": "PowerShell@1",
                    "searchkey": "value_in_task_step"
                }]
            }]
        }]
    }
    
    assert deep_search_single(yaml_with_task, "searchkey") == "value_in_task_step"

def test_deep_search_single_with_task():
    test_data = {
        "stages": [{
            "steps": [{
                "task": "PowerShell@1"
            }]
        }]
    }
    
    result = deep_search_single(test_data, "task")
    assert result == "PowerShell@1"

def test_deep_search_single_comprehensive():
    # Test case 1: Key in stage
    yaml_data = {
        "stages": [{
            "target_key": "stage_value"
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "stage_value"

    # Test case 2: Key in stage->jobs
    yaml_data = {
        "stages": [{
            "jobs": [{
                "target_key": "job_value"
            }]
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "job_value"

    # Test case 3: Key in stage->steps
    yaml_data = {
        "stages": [{
            "steps": [{
                "target_key": "step_value"
            }]
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "step_value"

    # Test case 4: Key in stage->task
    yaml_data = {
        "stages": [{
            "task": {
                "target_key": "task_value"
            }
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "task_value"

    # Test case 5: Key in root jobs
    yaml_data = {
        "jobs": [{
            "target_key": "root_job_value"
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "root_job_value"

    # Test case 6: Key in root steps
    yaml_data = {
        "steps": [{
            "target_key": "root_step_value"
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "root_step_value"

    # Test case 7: Key in root task
    yaml_data = {
        "task": {
            "target_key": "root_task_value"
        }
    }
    assert deep_search_single(yaml_data, "target_key") == "root_task_value"

    # Test case 8: Key not found
    yaml_data = {
        "unrelated": "value"
    }
    assert deep_search_single(yaml_data, "target_key") is None

    # Test case 9: Empty input
    assert deep_search_single({}, "target_key") is None

    # Test case 10: Key in job->task
    yaml_data = {
        "jobs": [{
            "task": {
                "target_key": "job_task_value"
            }
        }]
    }
    assert deep_search_single(yaml_data, "target_key") == "job_task_value"

def test_parse_jobs():
    # Test case 1: Job with displayName and steps containing publish
    yaml_data = {
        "jobs": [{
            "displayName": "Test Job",
            "steps": [{
                "publish": "artifact1"
            }]
        }]
    }
    jobs = parse_jobs(yaml_data)
    assert len(jobs) == 1
    assert jobs[0].getName() == "Test Job"
    assert jobs[0].getArtifacts() == ["artifact1"]

    # Test case 2: Job with steps containing tasks
    yaml_data = {
        "jobs": [{
            "displayName": "Test Job 2",
            "steps": [{
                "task": "PowerShell@1"
            }]
        }]
    }
    jobs = parse_jobs(yaml_data)
    assert len(jobs) == 1
    assert jobs[0].getName() == "Test Job 2"
    assert "PowerShell" in jobs[0].getTasks()[0] or "Default" in jobs[0].getTasks()[0]

    # Test case 3: Job with tasks directly
    yaml_data = {
        "jobs": [{
            "displayName": "Test Job 3",
            "tasks": [{
                "task": "DotNet@1"
            }]
        }]
    }
    jobs = parse_jobs(yaml_data)
    assert len(jobs) == 1
    assert jobs[0].getName() == "Test Job 3"
    assert "DotNet" in jobs[0].getTasks()[0] or "Default" in jobs[0].getTasks()[0]

    # Test case 4: Empty jobs section
    yaml_data = {
        "jobs": []
    }
    jobs = parse_jobs(yaml_data)
    assert len(jobs) == 0

    # Test case 5: No jobs section
    yaml_data = {}
    jobs = parse_jobs(yaml_data)
    assert len(jobs) == 0

def test_deep_search_multi():
    # Test case 1: Searching in stages
    yaml_data = {
        "stages": [{
            "stage_key": "value1",
            "jobs": [{
                "job_key": "value2",
                "steps": [{
                    "step_key": "value3",
                    "task": "task_value"
                }]
            }]
        }]
    }
    keys = ["stage_key", "job_key", "step_key", "task"]
    results = deep_search_multi(yaml_data, keys)
    assert "stage_key" in results
    assert "job_key" in results
    assert "step_key" in results
    assert "task" in results

    # Test case 2: Searching in jobs with scripts
    yaml_data = {
        "jobs": [{
            "job_key": "value1",
            "steps": [{
                "script": "some python script"
            }]
        }]
    }
    keys = ["job_key", "python"]
    results = deep_search_multi(yaml_data, keys)
    assert "job_key" in results
    assert "python" in results

    # Test case 3: Direct steps with tasks
    yaml_data = {
        "steps": [{
            "task": "PowerShell@1",
            "step_key": "value1"
        }]
    }
    keys = ["PowerShell@1", "step_key"]
    results = deep_search_multi(yaml_data, keys)
    assert "step_key" in results
    assert "PowerShell@1" in results

    # Test case 4: Direct task
    yaml_data = {
        "task": "DotNet@1"
    }
    keys = ["DotNet@1"]
    results = deep_search_multi(yaml_data, keys)
    assert "DotNet@1" in results

    # Test case 5: Script at root level
    yaml_data = {
        "script": "python test.py"
    }
    keys = ["python"]
    results = deep_search_multi(yaml_data, keys)
    assert "python" in results

    # Test case 6: Complex nested structure
    yaml_data = {
        "stages": [{
            "stage_key": "value1",
            "steps": [{
                "step_key": "value2",
                "script": "powershell command"
            }],
            "task": "task_value"
        }]
    }
    keys = ["stage_key", "step_key", "powershell", "task_value"]
    results = deep_search_multi(yaml_data, keys)
    assert "stage_key" in results
    assert "step_key" in results
    assert "powershell" in results
    assert "task_value" in results

    # Test case 7: Empty input
    yaml_data = {}
    keys = ["any_key"]
    results = deep_search_multi(yaml_data, keys)
    assert len(results) == 0

    # Test case 8: None values
    yaml_data = None
    keys = ["any_key"]
    results = deep_search_multi(yaml_data, keys)
    assert len(results) == 0

def test_deep_search_multi_job_steps_with_tasks():
    # Test data with job steps containing both direct keys and task keys
    yaml_data = {
        "jobs": [{
            "steps": [{
                "python": "some_value",  # Direct key match
                "task": {
                    "python": "another_value"  # Key in task dictionary
                }
            }]
        }]
    }
    
    results = deep_search_multi(yaml_data, ["python"])
    
    # Should find both occurrences of "python"
    assert results.count("python") == 2
    assert len(results) == 2

def test_deep_search_multi_nested_task_keys():
    # More complex test case with multiple levels and multiple matches
    yaml_data = {
        "jobs": [{
            "steps": [
                {
                    "task": {
                        "python": "value1"
                    }
                },
                {
                    "python": "value2",
                    "task": {
                        "python": "value3"
                    }
                }
            ]
        }]
    }
    
    results = deep_search_multi(yaml_data, ["python"])
    
    # Should find all three occurrences of "python"
    assert results.count("python") == 3
    assert len(results) == 3

def test_deep_search_multi_no_matches_in_tasks():
    yaml_data = {
        "jobs": [{
            "steps": [{
                "task": {
                    "not_python": "value"
                }
            }]
        }]
    }
    
    results = deep_search_multi(yaml_data, ["python"])
    assert len(results) == 0

def test_get_template_path_found(mock_config_file, tmp_path):
    # Arrange
    config_path = os.path.join(os.getcwd(), "config", "yml_url_config.json")
    
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config_file))), \
         patch('os.getcwd', return_value=str(tmp_path)):
        
        # Test case 1: Exact match
        result = get_template_path("templates/template1.yml")
        assert result == os.path.normpath("templates/template1.yml")
        
        # Test case 2: Partial match
        result = get_template_path("template2.yml")
        assert result == os.path.normpath("templates/subfolder/template2.yml")
        
        # Test case 3: Absolute path match
        result = get_template_path("/absolute/path/template3.yml")
        assert result == os.path.normpath("/absolute/path/template3.yml")

def test_get_template_path_not_found(mock_config_file, tmp_path):
    # Arrange
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config_file))), \
         patch('os.getcwd', return_value=str(tmp_path)):
        
        # Test case: Non-existent template
        result = get_template_path("non_existent_template.yml")
        assert result is None

def test_get_template_path_file_not_found():
    # Arrange
    with patch('builtins.open', side_effect=FileNotFoundError):
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            get_template_path("any_template.yml")

def test_get_template_path_invalid_json():
    # Arrange
    with patch('builtins.open', mock_open(read_data="invalid json")):
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            get_template_path("any_template.yml")

def test_get_template_path_missing_dictionary_key(tmp_path):
    # Arrange
    invalid_config = {"wrong_key": []}
    with patch('builtins.open', mock_open(read_data=json.dumps(invalid_config))), \
         patch('os.getcwd', return_value=str(tmp_path)):
        # Act & Assert
        with pytest.raises(KeyError):
            get_template_path("any_template.yml")
