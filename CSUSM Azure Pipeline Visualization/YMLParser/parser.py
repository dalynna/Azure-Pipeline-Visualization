import json
import re
import yaml
import requests
from dotenv import load_dotenv
from functools import singledispatch
import os
import pprint
from cron_descriptor import (
    Options,
    CasingTypeEnum,
    DescriptionTypeEnum,
    ExpressionDescriptor,
)  # for cron decrypting

TASK_NAMES_IGNORE_CASE = [
    "Python",
    "python",
    "Java",
    "java",
    "C++",
    "c++",
    "JavaScript",
    "javascript",
    "Node",
    "node",
    "DotNet",
    "dotnet",
    "PowerShell",
    "powershell",
    "npm",
]


TASK_ALIAS_MAP = {
    "Python": "Python",
    "python": "Python",
    "Java": "Java",
    "java": "Java",
    "C++": "C++",
    "c++": "C++",
    "cpp": "C++",
    "JavaScript": "JavaScript",
    "javascript": "JavaScript",
    "Node": "Node",
    "node": "Node",
    "DotNet": ".NET",
    "dotnet": ".NET",
    "PowerShell": "Powershell",
    "powershell": "Powershell",
    "npm": "npm",
}


def is_URL(string):
    """Checks if a string is a URL.
    
    Args:
        string: The string to check
        
    Returns:
        bool: True if the string appears to be a URL, False otherwise
    """
    if not string:
        return False
    return string.startswith(("http://", "https://"))


def parse_yml_file(input):
    """Parses a YML file from a given path.
    If the path is a URL, it will use the Azure DevOps API to fetch the YML file.
    Otherwise, it will pull from the local file system.
    """

    if len(input) != 2:
        print("Error: Missing parameter. Check formatting of yml_url_config.json")
        return None
    pipeline_name = input[0]
    file_path = input[1]

    if is_URL(file_path):
        return apiParser.parse_yml(pipeline_name, file_path)
    else:
        return localParser.parse_yml(pipeline_name, file_path)


class ymlParserInterface:
    """Generic interface for parsing YML files.
    This is the interface for the proxy pattern.

    Attributes:
        None
    """

    @staticmethod
    def parse_yml(pipeline_name: str, file_path: str):
        """
        This is the method that will be called to parse the YML file.

        Args:
            file_path (str): The path to the YML file.
            repo_name (str): The name of the repository, if any.
        """
        pass


class apiParser(ymlParserInterface):
    """YML Parser that implements the generic parser interface. Made to parse a
    YML file through the Azure dev ops API given a name of a repo and a path to
    a YML file.
    """

    @staticmethod
    def parse_yml(pipeline_name: str, file_path: str):
        """
        Parse YML file from Azure DevOps API.

        Args:
            pipeline_name (str): Name of the pipeline
            file_path (str): URL path to the YML file
        """
        try:
            load_dotenv()
            pat = os.getenv("PAT")
            organization_url = os.getenv("ORG_URL")
        except:
            print("Error: .env file not found. Create a .env file with PAT and ORG_URL")
            return None

        if not file_path or not pipeline_name:
            print("Error: Missing parameter")
            return None

        try:
            # Basic validation of URL format
            if not file_path.startswith(("http://", "https://")):
                print("Error: Invalid URL format")
                return None

            response = requests.get(file_path, auth=("", pat))
            if response.status_code == 200:
                yml_content = response.content.decode("utf-8")
                yml_data = yaml.safe_load(yml_content)
                yml_data["origin"] = file_path
                if "name" not in yml_data:
                    yml_data["name"] = pipeline_name
                return yml_data
            else:
                print(f"Failed to fetch YML file from URL: {file_path}")
                return None
        except Exception as e:
            print(f"Error parsing YML file: {str(e)}")
            return None


class localParser(ymlParserInterface):
    """Parser that implements the generic parser interface. Made to parse a
    YML file from a local file system given a path to a YML file.

    Attributes:
        None
    """

    @staticmethod
    def parse_yml(pipeline_name: str, file_path: str):
        """Called by the parser class to parse the YML file.

        Args:
            file_path (str): The path to the YML file.
            pipeline_name (str): The name of the pipeline.
        """
        try:
            with open(file_path) as file:
                content = file.read()
                yml_data = None
                
                # First try safe_load
                try:
                    yml_data = yaml.safe_load(content)
                except (yaml.YAMLError, Exception) as e:
                    print(f"Warning: safe_load failed ({str(e)}). Attempting unsafe_load.")
                    try:
                        yml_data = yaml.unsafe_load(content)
                    except Exception as e:
                        print(f"Warning: unsafe_load also failed ({str(e)}). Creating basic structure.")
                
                # Ensure we always return a dictionary with required fields
                if yml_data is None:
                    yml_data = {}
                elif not isinstance(yml_data, dict):
                    yml_data = {"content": yml_data}
                
                yml_data["origin"] = file_path
                yml_data["name"] = pipeline_name
                return yml_data

        except FileNotFoundError:
            print("Error: File not found. Check file path?")
            return None
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None


class Pipeline:
    """A DevOps pipeline parsed from a YAML config file.

    Attributes:
        name: The name of the pipeline.
        os: The operating system the pipeline is running on.
        trigger: The trigger for the pipeline.
        languages: The languages used in the pipeline.
        jobs: The jobs in the pipeline.
        origin: The repository of where the YML file came from!
    """

    def __init__(self):
        """Initializes a Pipeline object with just a name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._name = None
        self._os = None
        self._trigger = None
        self._languages = []
        self._tasks = []
        self._jobs = []
        self._artifacts = []
        self._origin = None
        self.dependencies = []
        self._x = 0
        self._y = 0

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def setOS(self, os):
        self._os = os

    def getOS(self):
        return self._os

    def addLanguage(self, language):
        self._languages.append(language)

    def getLanguages(self):
        return self._languages

    def addJob(self, job):
        self._jobs.append(job)

    def getJobs(self):
        return self._jobs

    def addTask(self, task):
        self._tasks.append(task)

    def getTasks(self):
        return self._tasks

    def setTrigger(self, trigger):
        self._trigger = trigger

    def getTrigger(self):
        return self._trigger

    def addArtifact(self, artifact):
        self._artifacts.append(artifact)

    def getArtifacts(self):
        return self._artifacts

    def setOrigin(self, origin):
        self._origin = origin

    def getOrigin(self):
        return self._origin

    def addDependency(self, dependency):
        self.dependencies.append(dependency)

    def getDependencies(self):
        return self.dependencies

    def setX(self, x):
        self._x = x

    def getX(self):
        return self._x

    def setY(self, y):
        self._y = y

    def getY(self):
        return self._y

    def applyTemplate(self, templateParams):
        self.setOS(parse_os(templateParams))

        for task in deep_search_multi(templateParams, TASK_NAMES_IGNORE_CASE):
            self.addTask(TASK_ALIAS_MAP.get(task, "Default"))


def parse_name(params):
    if "name" in params:
        print("\nName:\t\t" + str(params["name"]))
        return str(params["name"])
    else:
        return None


def parse_os(params):
    os = deep_search_single(params, "pool")

    if os is not None:
        if "vmImage" in os:
            os = os["vmImage"]
            print("OS:\t\t" + os)
    return os


def parse_trigger(params):

    if "schedules" in params:
        # When looking for cron, decode the encrypted cron message.
        if "cron" in params["schedules"][0]:
            cron_encrypted = str(params["schedules"][0]["cron"])

            # call the cron descriptor function, with cron argument and display the new message to the console.
            cron_decrypted = cron_descriptor(cron_encrypted)

            # Update the trigger with the new message.
            return cron_decrypted

    elif "trigger" in params:
        if "branches" in params["trigger"]:
            if "include" in params["trigger"]["branches"]:
                trigger = str(params["trigger"]["branches"]["include"][0])
                print("Trigger after\ncommit to:\t" + trigger)
                return trigger
            elif "exclude" in params["trigger"]["branches"]:
                trigger = str(params["trigger"]["branches"]["exclude"][0])
                print("Trigger after\ncommit to anything but:\t" + trigger)
                return "- not " + trigger
        else:
            trigger = str(params["trigger"])
            print("Trigger after\ncommit to:\t" + trigger)
            return trigger
    else:
        return None


def cron_descriptor(cron_expression):
    """
    This function converts a cron expression into a human-readable expression.

    Params:
        c_expression (String) : The encrypted cron message passed from the YAML file info.

    Returns:
        newDescription is the new message created by the imported package.

    Example of descrypted message(5 parts needed to be considered a cron message):
    The cron expression "0 15 * * Fri" breaks down as follows:

    0 minutes past the hour
    15 indicates the 15th hour of the day (which is 3 PM in 24-hour time)
    The first * signifies every day of the month
    The second * signifies every month
    Fri indicates Friday

    What user now sees on console:
    Cron encrypted:          0 15 * * Fri
    Cron decrypted:          At 03:00 PM, only on Friday
    """
    # I want to decrypt the string value into something more meaningful for the user to see

    # If there is no message we let user know.
    if not cron_expression:
        return "No cron expression provided"

    # error handling if an issue generating the human readable message
    try:
        # configure options for the description
        options = Options()
        options.casing_type = (
            CasingTypeEnum.Sentence
        )  # setting the casing to sentence case
        options.description_type = DescriptionTypeEnum.FULL  # Get full ddescription

        # Generalte the description
        descriptor = ExpressionDescriptor(cron_expression, options)
        newDescription = descriptor.get_description()

        # I want to display the message to the user on the console.
        return newDescription
    except Exception as e:
        return f"Error generating description: {str(e)}"


class Job:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.artifacts = []

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def addTask(self, task):
        self.tasks.append(task)

    def getTasks(self):
        return self.tasks

    def addArtifact(self, artifact):
        self.artifacts.append(artifact)

    def getArtifacts(self):
        return self.artifacts


def parseTemplate(filePath, repoName):
    return parse_yml_file([repoName, filePath])


def parse_jobs(params):
    jobs = []
    
    if "jobs" not in params or not params["jobs"]:
        return jobs

    for job in params["jobs"]:
        jobToAppend = Job("Untitled Job")
        
        if "displayName" in job:
            jobToAppend.setName(str(job["displayName"]))
            
        if "steps" in job:
            for step in job["steps"]:
                if "publish" in step:
                    jobToAppend.addArtifact(str(step["publish"]))
                elif "task" in step:
                    tasks = parse_job_tasks({"steps": [step]})
                    for task in tasks:
                        jobToAppend.addTask(task)
                        
        if "tasks" in job:
            tasks = parse_job_tasks({"tasks": job["tasks"]})
            for task in tasks:
                jobToAppend.addTask(task)
                
        jobs.append(jobToAppend)
        
    return jobs


def parse_resources(params):
    dependencies = []
    if "resources" in params:
        if "pipelines" in params["resources"]:
            for pipeline in params["resources"]["pipelines"]:
                # Rename pipeline if name specified
                dependent = Pipeline()
                dependent.setName(pipeline["source"])
                print("Depends on:\t" + str(dependent.getName()))
                if dependent is not None:
                    dependencies.append(dependent)
    return dependencies


def parse_origin(params):
    if ("origin") in params:
        origin = str(params["origin"])
        # Remove square brackets if they exist
        origin = origin.strip("[]").replace("'", "")
        return origin
    else:
        return None


def deep_search_multi(params, keys):
    """
    Deep search for multiple keys in a dictionary. Preserves order of keys as they appear.

    Args:
        params (dict): A dictionary of parameters from the YAML config file.
        keys (list): A list of keys to search for in the dictionary.

    Returns:
        list: A list of results from the deep search.
    """
    if not params or not isinstance(params, dict) or not keys:
        return []

    results = []

    # Helper function to check script content
    def check_script(script_content, key):
        if isinstance(script_content, str) and key.lower() in script_content.lower():
            results.append(key)
            print("Appending " + key + " to results")

    # Iterate through stages
    if "stages" in params:
        for stage in params["stages"]:
            for key in keys:
                if key in stage:
                    results.append(key)
                    print("Appending " + key + " to results")
            
            # Check stage script
            if "script" in stage:
                for key in keys:
                    check_script(stage["script"], key)

            # Process stage tasks
            if "task" in stage:
                for key in keys:
                    if key in stage["task"]:
                        results.append(key)
                        print("Appending " + key + " to results")

            # Process stage jobs
            if "jobs" in stage:
                for job in stage["jobs"]:
                    for key in keys:
                        if key in job:
                            results.append(key)
                            print("Appending " + key + " to results")
                    
                    if "steps" in job:
                        for step in job["steps"]:
                            for key in keys:
                                if key in step:
                                    results.append(key)
                                    print("Appending " + key + " to results")
                                if "task" in step and key in step["task"]:
                                    results.append(key)
                                    print("Appending " + key + " to results")
                                elif "script" in step:
                                    check_script(step["script"], key)

            # Process stage steps
            if "steps" in stage:
                for step in stage["steps"]:
                    for key in keys:
                        if key in step:
                            results.append(key)
                            print("Appending " + key + " to results")
                        if "task" in step and key in step["task"]:
                            results.append(key)
                            print("Appending " + key + " to results")
                        elif "script" in step:
                            check_script(step["script"], key)

    # Process root level jobs
    if "jobs" in params:
        for job in params["jobs"]:
            for key in keys:
                if key in job:
                    results.append(key)
                    print("Appending " + key + " to results")
            
            if "steps" in job:
                for step in job["steps"]:
                    for key in keys:
                        if key in step:
                            results.append(key)
                            print("Appending " + key + " to results")
                        if "task" in step and key in step["task"]:
                            results.append(key)
                            print("Appending " + key + " to results")
                        elif "script" in step:
                            check_script(step["script"], key)

    # Process root level steps
    if "steps" in params:
        for step in params["steps"]:
            for key in keys:
                if key in step:
                    results.append(key)
                    print("Appending " + key + " to results")
                if "task" in step and key in step["task"]:
                    results.append(key)
                    print("Appending " + key + " to results")
                elif "script" in step:
                    check_script(step["script"], key)

    # Process root level task
    if "task" in params:
        for key in keys:
            if key in params["task"]:
                results.append(key)
                print("Appending " + key + " to results")

    # Process root level script
    elif "script" in params:
        for key in keys:
            check_script(params["script"], key)

    return results


def deep_search_single(params, key):
    """
    Deep search for a single key in a dictionary. Returns the first result.

    Args:
        params (dict): A dictionary of parameters from the YAML config file.
        key (str): A key to search for in the dictionary.

    Returns:
        Any: The result from the deep search.
    """
    if not params or not isinstance(params, dict):
        return None

    # Iterate through stages, jobs, steps, and tasks
    if "stages" in params:
        for stage in params["stages"]:
            if key in stage:
                return stage[key]
            if "jobs" in stage:
                for job in stage["jobs"]:
                    if key in job:
                        return job[key]
                    if "steps" in job:
                        for step in job["steps"]:
                            if key in step:
                                return step[key]
                            if "task" in step and isinstance(step["task"], dict) and key in step["task"]:
                                return step["task"][key]
            if "steps" in stage:
                for step in stage["steps"]:
                    if key in step:
                        return step[key]
                    if "task" in step and isinstance(step["task"], dict) and key in step["task"]:
                        return step["task"][key]
            if "task" in stage and isinstance(stage["task"], dict) and key in stage["task"]:
                return stage["task"][key]

    if "jobs" in params:
        for job in params["jobs"]:
            if key in job:
                return job[key]
            if "steps" in job:
                for step in job["steps"]:
                    if key in step:
                        return step[key]
                    if "task" in step and isinstance(step["task"], dict) and key in step["task"]:
                        return step["task"][key]
            if "task" in job and isinstance(job["task"], dict) and key in job["task"]:
                return job["task"][key]

    if "steps" in params:
        for step in params["steps"]:
            if key in step:
                return step[key]
            if "task" in step and isinstance(step["task"], dict) and key in step["task"]:
                return step["task"][key]

    if "task" in params and isinstance(params["task"], dict) and key in params["task"]:
        return params["task"][key]

    return None


def find_template_repo(repoName, params):
    # Look for repo
    if "repositories" in params["resources"]:
        for repo in params["resources"]["repositories"]:
            if repo["repository"] == repoName:
                return repo["name"]


def get_template_path(partial):
    """
    Finds the full template path from a partial path in the template dictionary.
    
    Args:
        partial (str): Partial path to search for
        
    Returns:
        str: Full normalized path if found, None if not found
        
    Raises:
        FileNotFoundError: If config file cannot be found
        json.JSONDecodeError: If config file contains invalid JSON
        KeyError: If template_dictionary key is missing from config
    """
    # Build OS-agnostic path to configuration file
    path_to_config_file = os.path.join(os.getcwd(), "config", "yml_url_config.json")

    # Read the JSON configuration file
    with open(path_to_config_file, "r") as f:
        config_data = json.load(f)
        templateDict = config_data["template_dictionary"]  # May raise KeyError

    # Search for partial path in template dictionary, OS-agnostic
    partial_norm = os.path.normpath(partial)
    for path in templateDict:
        if partial_norm in os.path.normpath(path):
            return os.path.normpath(path)
            
    return None


def find_and_parse_template(params):
    t = deep_search_single(params, "template")

    if t is None:
        return None
    else:
        print("\nTemplate detected. Parsing...")
        # Split template into repo name and file path
        # If @, it is remote, we go to a different folder (template stored in diff repo)
        if "@" in t:
            pair = str(t).split("@")

            # Get name of repository
            filePath = get_template_path(pair[0])
            repoName = pair[1]

            repoID = find_template_repo(repoName, params)
            print(f"Parsing template {repoName} at: {filePath}")
        # if no @, template is in th same folder that the yml file is in
        else:
            filePath = t
            repoID = ""

        if filePath is not None and repoID is not None:
            return parseTemplate(filePath, repoID)
        # If we fail to find template, return none
        else:
            print("Error: Please fix your template dictionary :) <3")
            return None


def parse_job_tasks(job):
    tasks = []
    if "steps" in job:
        for step in job["steps"]:
            # Check for artifacts
            if "publish" in step:
                print("Artifact:\t" + str(step["publish"]))
            # Grab task languages
            elif "task" in step:
                # Add task to list of tasks if it exists, otherwise add default task
                tasks.append(TASK_ALIAS_MAP.get(str(step["task"]), "Default"))
    elif "tasks" in job:
        for task in job["tasks"]:
            if "task" in task:
                tasks.append(TASK_ALIAS_MAP.get(str(task["task"]), "Default"))
    return tasks


def createPipeline(params):
    """Creates a Pipeline object from a YAML config file.

    Args:
        params (dict): A dictionary of parameters from the YAML config file.

    Returns:
        Pipeline: A Pipeline object.

    Raises:
        None
    """
    # TODO: Figure out how to extract name of pipeline from YML file
    newPipeline = None

    newPipeline = Pipeline()

    if params is None:
        # TODO: Throw error here when we have a GUI
        print("Error: YAML file is empty")
    else:
        # Check for name
        name = parse_name(params)

        if name == "None":
            newPipeline.setName("Unknown")
        else:
            newPipeline.setName(name)
        # Check for OS spec
        newPipeline.setOS(parse_os(params))
        # Check for schedules
        newPipeline.setTrigger(parse_trigger(params))
        # Check for repo URL
        newPipeline.setOrigin(parse_origin(params))
        # Check for connections to other pipelines
        template = find_and_parse_template(params)
        if template is not None:
            newPipeline.applyTemplate(template)

        for dependency in parse_resources(params):
            newPipeline.addDependency(dependency)

        # Check for jobs, tasks, artifacts
        for task in deep_search_multi(params, TASK_NAMES_IGNORE_CASE):
            newPipeline.addTask(TASK_ALIAS_MAP.get(task, "Default"))
        newPipeline.addArtifact(deep_search_single(params, "publish"))

    return newPipeline


def createPipelineDependencies(ymlFile):
    # I want to now create the child yml file into a pipeline object.
    # print("tests\\\input\\\\" + ymlFile)
    childPipeline = parse_yml_file("tests\\input\\" + ymlFile)
    # params = parse_yml_file("tests\\input\\testC.yml")

    # I want to call the function to create a pipeline since we have to make the dependent pipelines.
    createPipeline(childPipeline)
    # I want to attach the pipelines I have created to the parent pipeline.

    # I want to call the function to actually make the animation of fanning out from the parent pipeline.


def parseTemp(tempName, allTemplateDictionary):
    # given tempName

    # iterate thru dict

    # if name matches
    # return parser.parse(template)
    pass
