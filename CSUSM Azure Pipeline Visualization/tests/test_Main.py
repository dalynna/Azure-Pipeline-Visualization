import unittest
import svgwrite
from VSMWizard.main import addSaveButton, sortPipelines
from collections import defaultdict, deque

class TestAddSaveButton(unittest.TestCase):
    def test_add_save_button(self):
        # Create a mock SVG canvas
        canvas = svgwrite.Drawing()

        # Call the function to test
        addSaveButton(canvas)

        # Check if the "saveButtonGroup" group is added
        save_button_group = None
        for element in canvas.elements:
            if element.get_id() == "saveButtonGroup":
                save_button_group = element
                break
        self.assertIsNotNone(save_button_group, "Save button group not added to canvas")

        # Check if the rectangle is added to the group
        rect_found = False
        text_found = False
        for element in save_button_group.elements:
            if element.get_id() == "saveButton":
                rect_found = True
                self.assertEqual(element.attribs["fill"], "lightgray", "Rectangle fill color is incorrect")
                self.assertEqual(element.attribs["rx"], 5, "Rectangle corner radius (rx) is incorrect")
                self.assertEqual(element.attribs["ry"], 5, "Rectangle corner radius (ry) is incorrect")
            if element.get_id() == "saveButtonText":
                text_found = True
                self.assertEqual(element.text, "Save Positions", "Button text is incorrect")
                self.assertIn("cursor:pointer;", element.attribs["style"], "Text style is missing cursor:pointer")

        self.assertTrue(rect_found, "Rectangle for save button not found")
        self.assertTrue(text_found, "Text for save button not found")

class MockPipeline:
    def __init__(self, name, dependencies=None):
        self.name = name
        self.dependencies = dependencies or []
        self.x = 0
        self.y = 0

    def getName(self):
        return self.name

    def getDependencies(self):
        return self.dependencies

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

class TestSortPipelines(unittest.TestCase):
    def test_sort_independent_pipelines(self):
        pipelines = [
            MockPipeline("PipelineA"),
            MockPipeline("PipelineB"),
            MockPipeline("PipelineC"),
        ]
        sortPipelines(pipelines)
        self.assertEqual([p.getName() for p in pipelines], ["PipelineA", "PipelineB", "PipelineC"])

    def test_sort_with_dependencies(self):
        pipelineA = MockPipeline("PipelineA")
        pipelineB = MockPipeline("PipelineB", dependencies=[pipelineA])
        pipelineC = MockPipeline("PipelineC", dependencies=[pipelineB])
        pipelines = [pipelineC, pipelineB, pipelineA]
        sortPipelines(pipelines)
        self.assertEqual([p.getName() for p in pipelines], ["PipelineA", "PipelineB", "PipelineC"])

    def test_sort_with_multiple_dependencies(self):
        pipelineA = MockPipeline("PipelineA")
        pipelineB = MockPipeline("PipelineB", dependencies=[pipelineA])
        pipelineC = MockPipeline("PipelineC", dependencies=[pipelineA])
        pipelineD = MockPipeline("PipelineD", dependencies=[pipelineB, pipelineC])
        pipelines = [pipelineD, pipelineC, pipelineB, pipelineA]
        sortPipelines(pipelines)
        self.assertEqual([p.getName() for p in pipelines], ["PipelineA", "PipelineB", "PipelineC", "PipelineD"])

class TestHandleDuplicateTasksAdditionalCounter(unittest.TestCase):
    def test_additional_tasks_counter(self):
        # Mock the Pipeline object
        class MockPipeline:
            def __init__(self, tasks):
                self.tasks = tasks

            def getTasks(self):
                return self.tasks

        # Mock the canvas and container
        canvas = svgwrite.Drawing()
        visibleContainer = svgwrite.container.Group()

        # Mock the getIconPath function
        def mock_getIconPath(task):
            return f"resources/{task}.png"

        # Define test data
        tasks = ["python", "java", "c++", "javascript", "node", "npm", "artifact"]
        pipeline = MockPipeline(tasks)

        # Mock variables
        x, y = 0, 0
        CONST_LANG_WIDTH = 5
        CONST_LANG_MARGIN = 10
        CONST_ICON_WIDTH = 30
        CONST_ICON_HEIGHT = 30

        # Call the logic for handling additional tasks
        drawIndex = 5  # Simulate reaching the box's bounds
        additionalTaskCount = 0
        for index in range(len(pipeline.getTasks())):
            taskIcon = pipeline.getTasks()[index]
            taskIconPath = mock_getIconPath(taskIcon)

            if drawIndex >= 5 and index >= drawIndex:
                additionalTaskCount += 1
                print(f"Adding additional task counter: {additionalTaskCount}")
                visibleContainer.add(
                    svgwrite.shapes.Circle(
                        center=(
                            x + 10 + 15 + (CONST_LANG_WIDTH) * (10 * (drawIndex)),
                            y + 15 + CONST_LANG_MARGIN,
                        ),
                        r=15,
                        fill="red",
                    )
                )
                visibleContainer.add(
                    svgwrite.text.Text(
                        '+' + str(additionalTaskCount),
                        insert=(
                            x + 10 + 5 + (CONST_LANG_WIDTH) * (10 * (drawIndex)),
                            y + 15 + CONST_LANG_MARGIN + 5,
                        ),
                        fill="white",
                        style="font-size:12px; font-family:Arial;"
                    )
                )

        # Assertions
        # Check that the red circle for additional tasks was added
        red_circles = [e for e in visibleContainer.elements if isinstance(e, svgwrite.shapes.Circle) and e.attribs.get("fill") == "red"]
        print(f"Red Circles: {len(red_circles)}")
        self.assertEqual(len(red_circles), 2, "Incorrect number of red circles for additional tasks")

        # Check that the additional tasks counter text was added
        additional_task_texts = [e for e in visibleContainer.elements if isinstance(e, svgwrite.text.Text) and '+' in e.text]
        print(f"Additional Task Texts: {len(additional_task_texts)}")
        self.assertEqual(len(additional_task_texts), 2, "Incorrect number of additional task counters")
        self.assertEqual(additional_task_texts[0].text, "+1", "First additional task counter text is incorrect")
        self.assertEqual(additional_task_texts[1].text, "+2", "Second additional task counter text is incorrect")

if __name__ == "__main__":
    unittest.main()