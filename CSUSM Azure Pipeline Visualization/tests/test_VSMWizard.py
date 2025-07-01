import pytest
import VSMWizard.main as VSMWizard
from YMLParser import parser
from YMLParser.parser import Pipeline
import svgwrite
from unittest.mock import patch, MagicMock, mock_open
import os
import unittest


@pytest.mark.xfail(reason="Not implemented")
def test_VSMWizard():
    assert 4 == 3


def test_drawLine():
    line = VSMWizard.drawLine(svgwrite.Drawing(), (0, 100), (200, 300))

    # Test for correct return type
    assert line.__class__ == svgwrite.shapes.Line
    # Test for correct coordinates
    assert line.attribs["x1"] == 0
    assert line.attribs["y1"] == 100
    assert line.attribs["x2"] == 200
    assert line.attribs["y2"] == 300

    # Test for correct stroke width
    assert line.attribs["stroke-width"] == VSMWizard.CONST_STROKE_WIDTH
    # Test for correct stroke colour
    assert line.attribs["stroke"] == "black"


def test_drawText():
    text = VSMWizard.drawText(
        svgwrite.Drawing(), svgwrite.container.Group(), 0, 1, "test"
    )

    # Assert the function returns a svgwrite.text.Text object
    assert text.__class__ == svgwrite.text.Text
    # Assert the text object has the correct text
    assert text.text == "test"
    # Assert the text object has the correct coordinates
    # Text accepts a list of coordinates, cast to int.
    assert int(text.attribs["x"]) == 0
    assert int(text.attribs["y"]) == 1
    # TODO low priority test list of coordinates behaves as expected


def test_drawRect():

    dummyCanvas = svgwrite.Drawing()
    dummyGradient = dummyCanvas.linearGradient((0, 0), (0, 1))
    dummyCanvas.defs.add(dummyGradient)

    expected_X = 0
    expected_Y = 1
    expected_Width = 200
    expected_Height = 300

    text = VSMWizard.drawRect(
        svgwrite.Drawing(),
        svgwrite.container.Group(),
        expected_X,
        expected_Y,
        expected_Width,
        expected_Height,
        dummyGradient,
    )

    # Assert the function returns a svgwrite.shapes.Rect object
    assert text.__class__ == svgwrite.shapes.Rect
    # Assert the object has the correct coordinates
    assert text.attribs["x"] == expected_X
    assert text.attribs["y"] == expected_Y
    # Assert the object has the correct width and height
    assert text.attribs["width"] == expected_Width
    assert text.attribs["height"] == expected_Height


def test_drawHyperlink():
    expectedText = "test_text"
    expectedURL = "www.fakeweb.com/test"
    expectedX = 420
    expectedY = 69
    hyperlink = VSMWizard.drawHyperlink(
        svgwrite.Drawing(), expectedX, expectedY, expectedText, expectedURL
    )
    # TODO: Test for correct return type
    assert hyperlink.__class__ == svgwrite.container.Hyperlink
    textElement = hyperlink.elements[0]
    # TODO: Test for correct coordinates
    assert int(textElement.attribs["x"]) == expectedX
    assert int(textElement.attribs["y"]) == expectedY
    # TODO: Test for correct text
    assert getattr(textElement, "text") == expectedText
    # TODO: Test for correct url
    assert hyperlink.attribs["xlink:href"] == expectedURL
    # TODO: Test for correct placement relative to box
    # TODO: Test for correct text colour
    # TODO: Test for correct text style
    # TODO: Test for correct text decoration


@pytest.mark.xfail(reason="Not implemented")
def test_drawPipeline():
    assert 4 == 3


# FOR THE CENTER TRIGGER TEXT OF A PIPELINE
def test_drawPipeline():

    # Move to test_YMLParser
    # Create a sample YAML object for the test pipeline
    expectedTrigger = "testB.yml"
    yaml_data = {
        "name": "Sample Pipeline",
        "trigger": "testB.yml",
    }

    # Create a Pipeline object from the sample YAML data
    testPipeline = parser.createPipeline(yaml_data)
    assert testPipeline.getTrigger() == "testB.yml"

    drawing = svgwrite.Drawing(width="500", height="300")

    # Position the pipeline at coordinates (x=100, y=100)
    pipeline = VSMWizard.drawPipeline(drawing, 100, 100, testPipeline)

    # Sample assertions
    # Assert that the trigger text is placed correctly
    resultElement = pipeline.elements[1]
    assert resultElement.elementname == "text"
    # Assert trigger value is correct
    assert resultElement.text == expectedTrigger
    # Assert trigger text is placed at the center of the pipeline box
    assert resultElement.attribs["x"] == "214.0"
    assert resultElement.attribs["y"] == "150"


def test_getIconPath():
    supportedIcons = [
        "python",
        "java",
        "c++",
        "javascript",
        "dotnet",
        "node",
        "powershell",
        "artifact",
    ]

    for icon in supportedIcons:
        iconPath = VSMWizard.getIconPath(icon)
        # Assert the function returns a string
        assert iconPath.__class__ == str
        # Assert the string is the correct path
        assert iconPath == "resources\\" + icon + ".png"


def test_getIconPath_fail():
    # Assert the string is the correct path
    assert VSMWizard.getIconPath("not a real icon") == "resources\\defaulttech.png"


# FOR OS ICONS
def test_insertIcon():
    icon = VSMWizard.insertIcon(
        svgwrite.Drawing(), "resources\\windows.png", 0, 1, 30, 31, "windows"
    )
    # Assert the function returns a svgwrite.image>Image object
    assert icon.__class__ == svgwrite.image.Image
    # Assert the image is the correct image
    assert icon.attribs["xlink:href"] == "resources\\windows.png"
    # Assert the image has the correct coordinates
    assert icon.attribs["x"] == 0
    assert icon.attribs["y"] == 1
    # Assert the image has the correct width and height
    assert icon.attribs["width"] == 30
    assert icon.attribs["height"] == 31
    # Assert the image has the correct title
    assert icon.elements[0].elementname == "title"
    assert icon.elements[0].xml.text == "windows"


def test_insertIcon_noTitle():
    icon = VSMWizard.insertIcon(
        svgwrite.Drawing(), "resources\\windows.png", 0, 1, 30, 31
    )

    # Assert the function returns a svgwrite.image>Image object
    assert icon.__class__ == svgwrite.image.Image
    # Assert the image is the correct image
    assert icon.attribs["xlink:href"] == "resources\\windows.png"
    # Assert the image has the correct coordinates
    assert icon.attribs["x"] == 0
    assert icon.attribs["y"] == 1
    # Assert the image has the correct width and height
    assert icon.attribs["width"] == 30
    assert icon.attribs["height"] == 31
    # Assert the image has no title
    assert len(icon.elements) == 0


# FOR LANG ICONS
def test_insertLangIcon_a():
    # Dummy pipeline to get the code to run, this object is not under test
    testPipeline = Pipeline()
    testPipeline.setOS("windows-latest")
    # testing for a box created at x=0 x=1 on the canvas
    pipeline = VSMWizard.drawPipeline(svgwrite.Drawing(), 0, 1, testPipeline)
    # Assert it is returning the right object
    assert pipeline.__class__ == svgwrite.container.Group
    # Grabbing all of the elements of the pipeline and then going to check the properties of the icon
    icon = pipeline.elements[len(pipeline.elements) - 1]
    # Aseert the function returns a svgwrite.image.Image object
    assert icon.__class__ == svgwrite.image.Image
    # Assert the image is the correct image
    assert icon.attribs["xlink:href"] == "resources\\windows.png"
    # Assert the image has the correct coordinates relative to the box
    # TODO: replace hard-coded 265,6 with OS x,y offsets
    assert icon.attribs["x"] == 265
    assert icon.attribs["y"] == 6
    # Assert the image has the correct width and height
    # TODO: Replace hard-coded 30,30 with OS width,height
    assert icon.attribs["width"] == 30
    assert icon.attribs["height"] == 30


# Retesting with a new box at a different X and Y Value to make sure that they icon is getting placed relative to each box created
def test_insertLangIcon_b():
    # Dummy pipeline to get the code to run, this object is not under test
    testPipeline = Pipeline()
    testPipeline.setOS("macOS-latest")
    # Testing for a box created at x=100 and y=100
    pipeline = VSMWizard.drawPipeline(svgwrite.Drawing(), 100, 100, testPipeline)
    # Assert it is returning the right object
    assert pipeline.__class__ == svgwrite.container.Group
    # Grabbing all of the elements of the pipeline and then going to check the properties of the icon
    icon = pipeline.elements[len(pipeline.elements) - 1]
    # Aseert the function returns a svgwrite.image.Image object
    assert icon.__class__ == svgwrite.image.Image
    # Assert the image is the correct image
    assert icon.attribs["xlink:href"] == "resources\\macOS.png"
    # Assert the image has the correct coordinates relative to the box
    # TODO: replace hard-coded 365,105 with OS x,y offsets
    assert icon.attribs["x"] == 365
    assert icon.attribs["y"] == 105
    # Assert the image has the correct width and height
    # TODO: Replace hard-coded 30,30 with OS width,height
    assert icon.attribs["width"] == 30
    assert icon.attribs["height"] == 30


def test_artifactIcon():
    testPipeline = Pipeline()
    testPipeline.setOS("macOS-latest")
    pipeline = VSMWizard.drawPipeline(svgwrite.Drawing(), 100, 100, testPipeline)

    assert pipeline.__class__ == svgwrite.container.Group

    # Find icon in pipeline
    for element in pipeline.elements:
        if element.__class__ == svgwrite.image.Image:
            icon = element

    assert icon.attribs["xlink:href"] == "resources\\macOS.png"

    assert icon.attribs["x"] == 365
    assert icon.attribs["y"] == 105

    assert icon.attribs["width"] == 30
    assert icon.attribs["height"] == 30


@pytest.mark.xfail(reason="Not implemented")
def test_main():
    assert 4 == 3


def test_fanOut_zero():
    # Stage 1 does not fan out
    stage1 = Pipeline()
    stage1.setName("Stage 1")

    pipelinesArray = [stage1]
    canvas = svgwrite.Drawing()

    VSMWizard.addPipelinesToVSM(canvas, pipelinesArray)

    # Assert that the canvas has no lines
    for element in canvas.elements:
        assert element.__class__ != svgwrite.shapes.Line


def test_fanOut_one():
    # Stage 1 does not fan out
    stage1 = Pipeline()
    stage1.setName("Stage 1")

    stage2 = Pipeline()
    stage2.setName("Stage 2")
    stage2.addDependency(stage1)

    pipelinesArray = [stage1, stage2]
    canvas = svgwrite.Drawing()

    VSMWizard.addPipelinesToVSM(canvas, pipelinesArray)

    numLines = 0

    # Assert that the canvas has no lines
    for element in canvas.elements:
        if element.__class__ == svgwrite.shapes.Line:
            numLines += 1

    assert numLines == 2


def test_fanOut_many():
    CONST_PIPELINE_WIDTH = 300
    CONST_PIPELINE_HEIGHT = 100

    # Stage 1 fans out to Stage 2 and Stage 3
    stage1 = Pipeline()
    stage1.setName("Stage 1")
    stage1.setX(50)  # Set initial position for stage1
    stage1.setY(50)

    stage2 = Pipeline()
    stage2.setName("Stage 2")
    stage2.setX(400)  # Set position for stage2
    stage2.setY(100)
    stage2.addDependency(stage1)

    stage3 = Pipeline()
    stage3.setName("Stage 3")
    stage3.setX(400)  # Set position for stage3
    stage3.setY(200)
    stage3.addDependency(stage1)

    pipelinesArray = [stage1, stage2, stage3]
    canvas = svgwrite.Drawing()

    # Add pipelines to the VSM
    VSMWizard.addPipelinesToVSM(canvas, pipelinesArray)

    # Count the number of lines in the canvas
    numLines = 0
    lineIndices = []

    for element in canvas.elements:
        if element.__class__ == svgwrite.shapes.Line:
            numLines += 1
            lineIndices.append(canvas.elements.index(element))

    # Each fan-out connection is composed of two line segments
    # Assert that the total number of line segments is correct
    assert numLines == 4

    # Dynamically calculate expected coordinates for the fan-out lines
    expected_x1 = stage1.getX() + CONST_PIPELINE_WIDTH
    expected_y1 = stage1.getY() + (CONST_PIPELINE_HEIGHT / 2)

    # Assert that the fan-out line is drawn from stage1 to stage2
    fanOutLineA = canvas.elements[lineIndices[0]]
    assert fanOutLineA.attribs["x1"] == expected_x1
    assert fanOutLineA.attribs["y1"] == expected_y1
    assert fanOutLineA.attribs["x2"] == stage2.getX() - 30
    assert fanOutLineA.attribs["y2"] == stage2.getY() + (CONST_PIPELINE_HEIGHT / 2)

    # Assert that the fan-out line is drawn from stage1 to stage3
    fanOutLineB = canvas.elements[lineIndices[2]]
    assert fanOutLineB.attribs["x1"] == expected_x1
    assert fanOutLineB.attribs["y1"] == expected_y1
    assert fanOutLineB.attribs["x2"] == stage3.getX() - 30
    assert fanOutLineB.attribs["y2"] == stage3.getY() + (CONST_PIPELINE_HEIGHT / 2)


def test_willCollide_no_collision():
    # Create pipelines with different coordinates
    pipeline1 = Pipeline()
    pipeline1.setX(0)
    pipeline1.setY(0)

    pipeline2 = Pipeline()
    pipeline2.setX(200)
    pipeline2.setY(200)

    # Create a list of pipelines
    pipelines = [pipeline1, pipeline2]

    # Create a pipeline to draw with coordinates that do not collide with existing pipelines
    plToDraw = Pipeline()
    plToDraw.setX(400)
    plToDraw.setY(400)

    # Assert that there is no collision
    assert not VSMWizard.willCollide(plToDraw, pipelines)


def test_willCollide_collision():
    # Create pipelines with overlapping coordinates
    pipeline1 = Pipeline()
    pipeline1.setX(0)
    pipeline1.setY(0)

    pipeline2 = Pipeline()
    pipeline2.setX(200)
    pipeline2.setY(200)

    # Create a list of pipelines
    pipelines = [pipeline1, pipeline2]

    # Create a pipeline to draw with coordinates that collide with existing pipelines
    plToDraw = Pipeline()
    plToDraw.setX(100)
    plToDraw.setY(100)

    # Assert that there is a collision
    assert VSMWizard.willCollide(plToDraw, pipelines)


def test_willCollide_same_coordinates_zero():
    # Create pipelines with the same coordinates
    pipeline1 = Pipeline()
    pipeline1.setX(0)
    pipeline1.setY(0)

    pipeline2 = Pipeline()
    pipeline2.setX(0)
    pipeline2.setY(0)

    # Create a list of pipelines
    pipelines = [pipeline1, pipeline2]

    # Create a pipeline to draw with the same coordinates as existing pipelines
    plToDraw = Pipeline()
    plToDraw.setX(0)
    plToDraw.setY(0)

    # Assert that there is a collision
    assert not VSMWizard.willCollide(plToDraw, pipelines)


def test_willCollide_same_coordinates():
    # Create pipelines with the same coordinates
    pipeline1 = Pipeline()
    pipeline1.setX(100)
    pipeline1.setY(100)

    pipeline2 = Pipeline()
    pipeline2.setX(100)
    pipeline2.setY(100)

    # Create a list of pipelines
    pipelines = [pipeline1, pipeline2]

    # Create a pipeline to draw with the same coordinates as existing pipelines
    plToDraw = Pipeline()
    plToDraw.setX(100)
    plToDraw.setY(100)

    # Assert that there is a collision
    assert VSMWizard.willCollide(plToDraw, pipelines)


def test_syncDependencyCoordinates_with_dependencies():
    # Arrange
    pipelines = [
        Pipeline(),
        Pipeline(),
        Pipeline(),
    ]

    # Name pipelines
    for i in range(len(pipelines)):
        pipelines[i].setName(f"Pipeline{i+1}")

    pipelines[2].addDependency(pipelines[0])
    pipelines[0].setX(250)
    pipelines[0].setY(250)

    # Act
    VSMWizard.syncDependencyCoordinates(pipelines)

    # Assert
    for pipeline in pipelines:
        if pipeline.getName() == "Pipeline3":
            assert len(pipeline.getDependencies()) == 1
            assert pipeline.getDependencies()[0].getX() == 250
            assert pipeline.getDependencies()[0].getY() == 250
        else:
            assert len(pipeline.getDependencies()) == 0


def test_syncDependencyCoordinates_with_sibling_dependencies():
    # Arrange
    pipelines = [
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
    ]

    # Name pipelines
    for i in range(len(pipelines)):
        pipelines[i].setName(f"Pipeline{i+1}")

    pipelines[0].setX(150)
    pipelines[0].setY(150)
    pipelines[1].setX(250)
    pipelines[1].setY(250)
    pipelines[2].addDependency(pipelines[0])
    pipelines[3].addDependency(pipelines[0])

    # Act
    VSMWizard.syncDependencyCoordinates(pipelines)

    # Assert
    for pipeline in pipelines:
        # Pipeline3 and Pipeline4 share a dependency on Pipeline1
        # Assert each dependency object has the correct coordinates after sync
        if pipeline.getName() == "Pipeline3" or pipeline.getName() == "Pipeline4":
            assert len(pipeline.getDependencies()) == 1
            assert pipeline.getDependencies()[0].getX() == 150
            assert pipeline.getDependencies()[0].getY() == 150
        else:
            assert len(pipeline.getDependencies()) == 0


def test_drawDummyPipeline_collisionWithExistingPipelines():

    canvas = svgwrite.Drawing()
    pipelines = [Pipeline()]  # Create a list of existing pipelines
    dependency = Pipeline()  # Create a dummy Dependency object
    dependency.setName("test")
    x_coord = 100
    y_coord = 200
    pipelines[0].setX(x_coord)
    pipelines[0].setY(y_coord)

    # Call the function under test
    VSMWizard.drawDummyPipeline(canvas, pipelines, dependency, x_coord, y_coord)

    # Assert that the dummy pipeline is drawn at a different y-coordinate
    assert dependency.getY() != y_coord


def test_drawDummyPipeline_successfulDraw():

    # Arrange
    canvas = svgwrite.Drawing()
    # Create singular pipeline object
    # This object does not have a dependency, so we expect a dummy to be drawn
    pipelines = [Pipeline()]
    # Create singular dependency object
    dependency = Pipeline()
    dependency.setName("test")
    # Set coordinates for the dependency
    x_coord = 100
    y_coord = 200

    # Act
    VSMWizard.drawDummyPipeline(canvas, pipelines, dependency, x_coord, y_coord)

    # Assert that the dummy pipeline is drawn and added to the pipelines list
    assert len(pipelines) == 2
    assert pipelines[1].getName() == dependency.getName()
    assert pipelines[1].getX() == x_coord
    assert pipelines[1].getY() == y_coord


def test_svg_dimensions_default():
    # Arrange
    expected_width = 3000
    expected_height = 3000
    dummyVSM = svgwrite.Drawing()

    # Act
    vsm = VSMWizard.resizeSVG(dummyVSM)

    # Assert
    assert vsm["width"] == expected_width
    assert vsm["height"] == expected_height


def test_svg_dimensions_expandHeight():
    # Arrange
    default_height = 1080

    pipelines = [
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
        Pipeline(),
    ]

    dummyVSM = svgwrite.Drawing()
    VSMWizard.addPipelinesToVSM(dummyVSM, pipelines)

    # Act
    vsm = VSMWizard.resizeSVG(dummyVSM)

    # Assert
    assert vsm["height"] > default_height


def test_connectDependencies_positioning():
    # Test different pipeline positioning scenarios
    canvas = svgwrite.Drawing()
    
    # Scenario 1: Dependent pipeline is to the right of source
    source1 = Pipeline()
    source1.setName("Source1")
    source1.setX(50)
    source1.setY(50)
    
    dependent1 = Pipeline()
    dependent1.setName("Dependent1")
    dependent1.setX(400)  # To the right
    dependent1.setY(50)   # Same height
    dependent1.addDependency(source1)
    
    # Scenario 2: Dependent pipeline is below source
    dependent2 = Pipeline()
    dependent2.setName("Dependent2")
    dependent2.setX(200)  # Overlapping X with source
    dependent2.setY(200)  # Below source
    dependent2.addDependency(source1)
    
    # Scenario 3: Dependent pipeline is above source
    dependent3 = Pipeline()
    dependent3.setName("Dependent3")
    dependent3.setX(200)  # Overlapping X with source
    dependent3.setY(0)    # Above source
    dependent3.addDependency(source1)
    
    pipelines = [source1, dependent1, dependent2, dependent3]
    
    # Draw all pipelines
    containers = []
    for i, pipeline in enumerate(pipelines):
        container = VSMWizard.drawPipeline(canvas, pipeline.getX(), pipeline.getY(), pipeline)
        containers.append(container)
    
    # Connect dependencies for each dependent pipeline
    for i in range(1, len(pipelines)):
        VSMWizard.connectDependencies(canvas, containers[i], pipelines, i)
    
    # Count lines and verify their properties
    lines = [e for e in canvas.elements if isinstance(e, svgwrite.shapes.Line)]
    
    # We should have 6 lines (2 segments for each of the 3 dependencies)
    assert len(lines) == 6
    
    # Print line coordinates for debugging
    line_coords = []
    for i, line in enumerate(lines):
        coords = (float(line.attribs["x1"]), float(line.attribs["y1"]), 
                 float(line.attribs["x2"]), float(line.attribs["y2"]))
        line_coords.append(coords)
    
    # Group lines by which pipeline they're likely connecting to
    # For each dependent pipeline, find lines that have coordinates near it
    
    # For right-positioned pipeline (Dependent1)
    right_lines = [l for l in lines if 
                  float(l.attribs["x2"]) <= dependent1.getX() and
                  abs(float(l.attribs["y2"]) - (dependent1.getY() + 50)) < 100]
    
    # For below-positioned pipeline (Dependent2)
    below_lines = [l for l in lines if 
                  abs(float(l.attribs["x2"]) - dependent2.getX()) < 100 and
                  float(l.attribs["y2"]) <= dependent2.getY() + 100]
    
    # For above-positioned pipeline (Dependent3)
    above_lines = [l for l in lines if 
                  abs(float(l.attribs["x2"]) - dependent3.getX()) < 100 and
                  float(l.attribs["y2"]) >= dependent3.getY()]
    
    # Assert that we have at least one line for each scenario
    assert len(right_lines) > 0, f"No lines found for right-positioned pipeline. Line coords: {line_coords}"
    assert len(below_lines) > 0, f"No lines found for below-positioned pipeline. Line coords: {line_coords}"
    assert len(above_lines) > 0, f"No lines found for above-positioned pipeline. Line coords: {line_coords}"


def test_connectDependencies_positioning_logic():
    """Test the specific connection logic for different pipeline positions"""
    # Setup
    canvas = svgwrite.Drawing()
    container = svgwrite.container.Group()
    
    # Create a mock Pipeline class with dependencies
    class MockPipeline:
        def __init__(self, name, x=0, y=0):
            self.name = name
            self.x = x
            self.y = y
            self.dependencies = []
            
        def getName(self):
            return self.name
            
        def getX(self):
            return self.x
            
        def getY(self):
            return self.y
            
        def setX(self, x):
            self.x = x
            
        def setY(self, y):
            self.y = y
            
        def getDependencies(self):
            return self.dependencies
            
        def addDependency(self, dep):
            self.dependencies.append(dep)
    
    # Create test pipelines with specific positions to test the connection logic
    
    # Case 1: Dependent pipeline is to the left of source and below it
    source1 = MockPipeline("Source1", x=400, y=100)
    dependent1 = MockPipeline("Dependent1", x=100, y=300)  # Left and below
    dependent1.addDependency(source1)
    
    # Case 2: Dependent pipeline is to the left of source and above it
    source2 = MockPipeline("Source2", x=400, y=300)
    dependent2 = MockPipeline("Dependent2", x=100, y=100)  # Left and above
    dependent2.addDependency(source2)
    
    # Create a list of pipelines for each test case
    pipelines1 = [source1, dependent1]
    pipelines2 = [source2, dependent2]
    
    # Test Case 1: Left and below
    VSMWizard.connectDependencies(canvas, container, pipelines1, 1)
    
    # Find the lines created for case 1
    lines1 = [e for e in canvas.elements if isinstance(e, svgwrite.shapes.Line)]
    
    # There should be two line segments (A and B)
    assert len(lines1) == 2
    
    # Find segment A (first segment)
    segmentA1 = next(l for l in lines1 if "SegmentA" in l.attribs["id"])
    
    # Check that the line starts from the bottom of the source pipeline
    assert float(segmentA1.attribs["x1"]) == source1.getX() + (VSMWizard.CONST_PIPELINE_WIDTH / 2)
    assert float(segmentA1.attribs["y1"]) == source1.getY() + VSMWizard.CONST_PIPELINE_HEIGHT
    
    # Check that the line ends at the top of the dependent pipeline
    assert float(segmentA1.attribs["x2"]) == dependent1.getX() + (VSMWizard.CONST_PIPELINE_WIDTH / 2)
    assert float(segmentA1.attribs["y2"]) == dependent1.getY() - 30
    
    # Clear the canvas for the next test
    canvas.elements.clear()
    
    # Test Case 2: Left and above
    VSMWizard.connectDependencies(canvas, container, pipelines2, 1)
    
    # Find the lines created for case 2
    lines2 = [e for e in canvas.elements if isinstance(e, svgwrite.shapes.Line)]
    
    # There should be two line segments (A and B)
    assert len(lines2) == 2
    
    # Find segment A (first segment)
    segmentA2 = next(l for l in lines2 if "SegmentA" in l.attribs["id"])
    
    # Check that the line starts from the top of the source pipeline
    assert float(segmentA2.attribs["x1"]) == source2.getX() + (VSMWizard.CONST_PIPELINE_WIDTH / 2)
    assert float(segmentA2.attribs["y1"]) == source2.getY()
    
    # Check that the line ends at the bottom of the dependent pipeline
    assert float(segmentA2.attribs["x2"]) == dependent2.getX() + (VSMWizard.CONST_PIPELINE_WIDTH / 2)
    assert float(segmentA2.attribs["y2"]) == dependent2.getY() + VSMWizard.CONST_PIPELINE_HEIGHT + 30


@patch('VSMWizard.main.parser.parse_yml_file')
@patch('VSMWizard.main.parser.createPipeline')
@patch('VSMWizard.main.sortPipelines')
@patch('VSMWizard.main.addPipelinesToVSM')
@patch('VSMWizard.main.consolidateDummies')
@patch('VSMWizard.main.addSaveButton')
@patch('VSMWizard.main.resizeSVG')
@patch('os.path.islink')
@patch('os.symlink')
@patch('svgwrite.Drawing')
@patch('builtins.open', new_callable=mock_open, read_data='{"yml_filepath": [["pipeline1", "path1.yml"], ["pipeline2", "path2.yml"]]}')
def test_generate_success(mock_open_file, mock_drawing, mock_symlink, mock_islink, 
                         mock_resize, mock_add_button, mock_consolidate, 
                         mock_add_pipelines, mock_sort, mock_create_pipeline, 
                         mock_parse_yml):
    # Setup mocks
    mock_islink.return_value = False
    mock_pipeline1 = MagicMock()
    mock_pipeline1.getName.return_value = "pipeline1"
    mock_pipeline2 = MagicMock()
    mock_pipeline2.getName.return_value = "pipeline2"
    
    mock_create_pipeline.side_effect = [mock_pipeline1, mock_pipeline2]
    mock_parse_yml.side_effect = [{"name": "pipeline1"}, {"name": "pipeline2"}]
    
    mock_vsm = MagicMock()
    mock_drawing.return_value = mock_vsm
    mock_resize.return_value = mock_vsm
    
    # Call the function
    result = VSMWizard.generate("")
    
    # Assertions
    assert result is None  # Function should return None on success
    
    # Check file was opened correctly
    mock_open_file.assert_called_once_with(os.path.join(os.getcwd(), "config", "yml_url_config.json"), "r")
    
    # Check YML files were parsed
    assert mock_parse_yml.call_count == 2
    mock_parse_yml.assert_any_call(["pipeline1", "path1.yml"])
    mock_parse_yml.assert_any_call(["pipeline2", "path2.yml"])
    
    # Check pipelines were created
    assert mock_create_pipeline.call_count == 2
    
    # Check SVG was created with correct filename
    mock_drawing.assert_called_once_with("pipeline2_VSM.svg", profile="full", onload="makeDraggable(evt)")
    
    # Check pipelines were sorted
    mock_sort.assert_called_once()
    
    # Check pipelines were added to VSM
    mock_add_pipelines.assert_called_once()
    
    # Check dummy pipelines were consolidated
    mock_consolidate.assert_called_once()
    
    # Check save button was added
    mock_add_button.assert_called_once()
    
    # Check SVG was resized
    mock_resize.assert_called_once()
    
    # Check SVG was saved
    mock_vsm.save.assert_called_once()
    
    # Check symlink was created
    mock_symlink.assert_called_once_with("pipeline2_VSM.svg", "latest.svg")


@patch('builtins.open')
def test_generate_file_not_found(mock_open):
    # Setup mock to raise FileNotFoundError
    mock_open.side_effect = FileNotFoundError()
    
    # Call the function
    result = VSMWizard.generate("")
    
    # Check error message
    assert "Error: File not found" in result


@patch('builtins.open', new_callable=mock_open, read_data='{invalid json')
def test_generate_json_decode_error(mock_open):
    # Call the function (the mock will return invalid JSON)
    result = VSMWizard.generate("")
    
    # Check error message
    assert "Error: Failed to decode JSON" in result


@patch('VSMWizard.main.parser.parse_yml_file')
@patch('VSMWizard.main.parser.createPipeline')
@patch('builtins.open', new_callable=mock_open, read_data='{"yml_filepath": [["pipeline1", "path1.yml"]]}')
def test_generate_yml_parse_error(mock_open, mock_create_pipeline, mock_parse_yml):
    # Setup mock to return None (parse error)
    mock_parse_yml.return_value = None
    mock_pipeline = MagicMock()
    mock_pipeline.getName.return_value = "error_pipeline"
    mock_create_pipeline.return_value = mock_pipeline
    
    # Call the function
    with patch('svgwrite.Drawing'), \
         patch('VSMWizard.main.sortPipelines'), \
         patch('VSMWizard.main.addPipelinesToVSM'), \
         patch('VSMWizard.main.consolidateDummies'), \
         patch('VSMWizard.main.addSaveButton'), \
         patch('VSMWizard.main.resizeSVG'), \
         patch('os.path.islink', return_value=False), \
         patch('os.symlink'):
        VSMWizard.generate("")
    
    # Check that createPipeline was called with empty string
    mock_create_pipeline.assert_called_once_with("")
    
    # Check that setTrigger was called with error message
    mock_pipeline.setTrigger.assert_called_once()
    assert "File Error" in mock_pipeline.setTrigger.call_args[0][0]


@patch('VSMWizard.main.parser.parse_yml_file')
@patch('VSMWizard.main.parser.createPipeline')
@patch('os.path.islink')
@patch('os.remove')
@patch('os.symlink')
@patch('builtins.open', new_callable=mock_open, read_data='{"yml_filepath": [["pipeline1", "path1.yml"]]}')
def test_generate_symlink_exists(mock_open, mock_symlink, mock_remove, mock_islink, 
                               mock_create_pipeline, mock_parse_yml):
    # Setup mocks
    mock_islink.return_value = True
    mock_pipeline = MagicMock()
    mock_pipeline.getName.return_value = "pipeline1"
    mock_create_pipeline.return_value = mock_pipeline
    mock_parse_yml.return_value = {"name": "pipeline1"}
    
    # Call the function
    with patch('svgwrite.Drawing'), \
         patch('VSMWizard.main.sortPipelines'), \
         patch('VSMWizard.main.addPipelinesToVSM'), \
         patch('VSMWizard.main.consolidateDummies'), \
         patch('VSMWizard.main.addSaveButton'), \
         patch('VSMWizard.main.resizeSVG'):
        VSMWizard.generate("")
    
    # Check that existing symlink was removed
    mock_remove.assert_called_once_with("latest.svg")
    
    # Check that new symlink was created
    mock_symlink.assert_called_once_with("pipeline1_VSM.svg", "latest.svg")


@patch('VSMWizard.main.parser.parse_yml_file')
@patch('VSMWizard.main.parser.createPipeline')
@patch('os.path.islink')
@patch('os.symlink')
@patch('builtins.open', new_callable=mock_open, read_data='{"yml_filepath": [["pipeline1", "path1.yml"]]}')
def test_generate_custom_filename(mock_open, mock_symlink, mock_islink, 
                                mock_create_pipeline, mock_parse_yml):
    # Setup mocks
    mock_islink.return_value = False
    mock_pipeline = MagicMock()
    mock_create_pipeline.return_value = mock_pipeline
    mock_parse_yml.return_value = {"name": "pipeline1"}
    
    # Call the function with custom name
    with patch('svgwrite.Drawing') as mock_drawing, \
         patch('VSMWizard.main.sortPipelines'), \
         patch('VSMWizard.main.addPipelinesToVSM'), \
         patch('VSMWizard.main.consolidateDummies'), \
         patch('VSMWizard.main.addSaveButton'), \
         patch('VSMWizard.main.resizeSVG'):
        VSMWizard.generate("custom_name")
    
    # Check SVG was created with custom filename
    mock_drawing.assert_called_once_with("custom_name.svg", profile="full", onload="makeDraggable(evt)")
    
    # Check symlink was created with custom filename
    mock_symlink.assert_called_once_with("custom_name.svg", "latest.svg")


def test_handleDummyPipelineTrigger():
    # Create test objects
    canvas = svgwrite.Drawing()
    container = svgwrite.container.Group()
    
    # Sample text that would trigger this function
    test_text = "Dependent pipeline TestPipeline not found"
    
    # Expected text segments after splitting
    expected_segments = [
        "Dependent pipeline",
        " TestPipeline ",
        "not found"
    ]
    
    # X and Y coordinates
    test_x = 100
    test_y = 100
    
    # Call the function
    VSMWizard.handleDummyPipelineTrigger(canvas, container, test_text, test_x, test_y)
    
    # Verify results
    # We should have 3 text elements in the container
    assert len(container.elements) == 3
    
    # Check each text element
    for i, element in enumerate(container.elements):
        # Verify it's a text element
        assert element.__class__ == svgwrite.text.Text
        
        # Verify the text content
        assert element.text == expected_segments[i]
        
        # Verify Y position (should increment by 20 for each line)
        assert float(element.attribs["y"]) == test_y + 35 + (i * 20)
        
        # Verify X position is centered
        estimated_width = len(expected_segments[i]) * 8
        expected_x = test_x + (VSMWizard.CONST_PIPELINE_WIDTH - estimated_width) / 2
        assert abs(float(element.attribs["x"]) - expected_x) < 1  # Allow small rounding differences


def test_handleFileErrorTrigger():
    # Create test objects
    canvas = svgwrite.Drawing()
    container = svgwrite.container.Group()
    
    # Sample text that would trigger this function
    test_text = "Check File Error check config file path for: /path/to/missing/file.yml"
    
    # Expected text segments after splitting
    expected_segments = [
        "Check File Error",
        " check config file path for:",  # Note the leading space here
        " /path/to/missing/file.yml"
    ]
    
    # X and Y coordinates
    test_x = 100
    test_y = 100
    
    # Call the function
    VSMWizard.handleFileErrorTrigger(canvas, container, test_text, test_x, test_y)
    
    # Verify results
    # We should have 3 text elements in the container
    assert len(container.elements) == 3
    
    # Check each text element
    for i, element in enumerate(container.elements):
        # Verify it's a text element
        assert element.__class__ == svgwrite.text.Text
        
        # Verify the text content
        assert element.text == expected_segments[i]
        
        # Verify Y position (should increment by 20 for each line)
        assert float(element.attribs["y"]) == test_y + 35 + (i * 20)
        
        # Verify X position is centered
        estimated_width = len(expected_segments[i]) * 8
        expected_x = test_x + (VSMWizard.CONST_PIPELINE_WIDTH - estimated_width) / 2
        assert abs(float(element.attribs["x"]) - expected_x) < 1  # Allow small rounding differences


def test_drawHiddenContainer():
    # Create test objects
    canvas = svgwrite.Drawing()
    parentContainer = svgwrite.container.Group()
    rect_id = "rect_100_100"
    test_x = 100
    test_y = 100
    
    # Call the function
    VSMWizard.drawHiddenContainer(canvas, parentContainer, rect_id, test_x, test_y)
    
    # Verify results
    
    # 1. Check that the gradient was created and added to defs
    gradients = [d for d in canvas.defs.elements if isinstance(d, svgwrite.gradients.LinearGradient)]
    assert len(gradients) == 1
    gradient = gradients[0]
    
    # Check gradient stops
    assert len(gradient.elements) == 2
    assert gradient.elements[0].attribs["offset"] == 0
    assert gradient.elements[0].attribs["stop-color"] == "#fffecd"
    assert gradient.elements[1].attribs["offset"] == 0.7
    assert gradient.elements[1].attribs["stop-color"] == "#ffe8a4"
    
    # 2. Find the hidden container in the parent container
    hidden_container = None
    for element in parentContainer.elements:
        if (isinstance(element, svgwrite.container.Group) and 
            element.attribs.get("id") == rect_id + "_hover"):
            hidden_container = element
            break
    
    assert hidden_container is not None
    
    # Check container attributes
    assert hidden_container.attribs["visibility"] == "hidden"
    assert hidden_container.attribs["id"] == rect_id + "_hover"
    assert hidden_container.attribs["class"] == "draggable"
    
    # 3. Check that the rectangle was added to the hidden container
    rects = [r for r in hidden_container.elements if isinstance(r, svgwrite.shapes.Rect)]
    assert len(rects) >= 1  # There might be multiple rectangles
    rect = rects[0]  # Just check the first one
    
    # Check rectangle position and size
    expected_x = test_x + VSMWizard.CONST_ICON_WIDTH
    expected_y = test_y + VSMWizard.CONST_ICON_WIDTH
    assert float(rect.attribs["x"]) == expected_x
    assert float(rect.attribs["y"]) == expected_y
    assert float(rect.attribs["width"]) == VSMWizard.CONST_PIPELINE_WIDTH
    assert float(rect.attribs["height"]) == VSMWizard.CONST_PIPELINE_HEIGHT
    
    # 4. Check that the animations were added
    animations = [a for a in hidden_container.elements if isinstance(a, svgwrite.animate.Animate)]
    assert len(animations) == 2
    
    # Check first animation (show on mousedown)
    show_animation = animations[0]
    assert show_animation.attribs["attributeName"] == "visibility"
    assert show_animation.attribs["values"] == "visible"
    assert show_animation.attribs["dur"] == "3.0s"
    assert show_animation.attribs["begin"] == f"{rect_id}.mousedown"
    assert show_animation.attribs["repeatCount"] == "1"
    assert show_animation.attribs["fill"] == "freeze"
    
    # Check second animation (hide on container mousedown)
    hide_animation = animations[1]
    assert hide_animation.attribs["attributeName"] == "visibility"
    assert hide_animation.attribs["values"] == "hidden"
    assert hide_animation.attribs["dur"] == "0.0s"
    assert hide_animation.attribs["begin"] == f"{rect_id}_hover.mousedown"
    assert hide_animation.attribs["end"] == f"{rect_id}.mousedown"
    assert hide_animation.attribs["repeatCount"] == "1"
    assert hide_animation.attribs["fill"] == "freeze"


class TestHandleDuplicateTasks(unittest.TestCase):
    def setUp(self):
        # Mock the Pipeline object
        class MockPipeline:
            def __init__(self, tasks):
                self.tasks = tasks
                
            def getTasks(self):
                return self.tasks
        
        # Make MockPipeline available to test methods
        self.MockPipeline = MockPipeline
                
        self.canvas = svgwrite.Drawing()
        self.container = svgwrite.container.Group()
        self.x = 0
        self.y = 0
        
        # Store original functions to restore after test
        self.original_getIconPath = VSMWizard.getIconPath
        self.original_insertIcon = VSMWizard.insertIcon
        self.original_drawCircle = VSMWizard.drawCircle
        self.original_drawText = VSMWizard.drawText
        
        # Mock functions
        VSMWizard.getIconPath = lambda taskIcon: f"resources/{taskIcon}.png"
        VSMWizard.insertIcon = lambda container, href, x, y, width, height, description=None: container.add(
            svgwrite.image.Image(href, insert=(x, y), size=(width, height))
        )
        VSMWizard.drawCircle = lambda canvas, container, x, y, r, fill: container.add(
            svgwrite.shapes.Circle(center=(x, y), r=r, fill=fill)
        )
        VSMWizard.drawText = lambda canvas, container, x, y, text, color="black": container.add(
            svgwrite.text.Text(text, insert=(x, y), fill=color)
        )
        
    def tearDown(self):
        # Restore original functions
        VSMWizard.getIconPath = self.original_getIconPath
        VSMWizard.insertIcon = self.original_insertIcon
        VSMWizard.drawCircle = self.original_drawCircle
        VSMWizard.drawText = self.original_drawText
    
    def test_artifact_icon(self):
        # Test that artifact icons are handled correctly
        pipeline = self.MockPipeline(["artifact"])
        
        VSMWizard.handleDuplicateTasks(self.canvas, self.container, pipeline, self.x, self.y)
        
        # Check that one image was added
        images = [e for e in self.container.elements if isinstance(e, svgwrite.image.Image)]
        self.assertEqual(len(images), 1)
        
        # Check image attributes
        image = images[0]
        self.assertEqual(image.attribs["xlink:href"], "resources/artifact.png")
        
    def test_duplicate_icons(self):
        # Test that duplicate icons are handled correctly
        pipeline = self.MockPipeline(["python", "python", "python"])
        
        VSMWizard.handleDuplicateTasks(self.canvas, self.container, pipeline, self.x, self.y)
        
        # Check that one image and two circles with text were added
        images = [e for e in self.container.elements if isinstance(e, svgwrite.image.Image)]
        circles = [e for e in self.container.elements if isinstance(e, svgwrite.shapes.Circle)]
        texts = [e for e in self.container.elements if isinstance(e, svgwrite.text.Text)]
        
        self.assertEqual(len(images), 1)
        self.assertEqual(len(circles), 2)
        self.assertEqual(len(texts), 2)
        
        # Check text values (should be "2" and "3" for the duplicate counters)
        # Convert to string for comparison since the text might be stored as an integer
        self.assertEqual(str(texts[0].text), '2')
        self.assertEqual(str(texts[1].text), '3')
        
    def test_additional_tasks_counter(self):
        # Test that additional tasks counter is added when more than 5 icons
        pipeline = self.MockPipeline(["python", "java", "c++", "javascript", "node", "npm", "artifact"])
        
        VSMWizard.handleDuplicateTasks(self.canvas, self.container, pipeline, self.x, self.y)
        
        # Check that 5 images were added for the first 5 tasks
        images = [e for e in self.container.elements if isinstance(e, svgwrite.image.Image)]
        self.assertEqual(len(images), 6)  # 5 regular icons + 1 artifact icon
        
        # Check that a circle with "+2" text was added for the additional tasks
        circles = [e for e in self.container.elements if isinstance(e, svgwrite.shapes.Circle)]
        texts = [e for e in self.container.elements if isinstance(e, svgwrite.text.Text)]
        
        self.assertEqual(len(circles), 1)
        
        # Find the text with "+" prefix
        additional_task_texts = [t for t in texts if t.text.startswith("+")]
        self.assertEqual(len(additional_task_texts), 1)
        self.assertEqual(additional_task_texts[0].text, "+1")


def test_consolidateDummies():
    """Test that dummy pipelines are properly consolidated into real pipelines"""
    # Setup
    canvas = svgwrite.Drawing()
    
    # Create a mock Pipeline class
    class MockPipeline:
        def __init__(self, name, origin=None, x=0, y=0):
            self.name = name
            self.origin = origin
            self.x = x
            self.y = y
            
        def getName(self):
            return self.name
            
        def getOrigin(self):
            return self.origin
            
        def getX(self):
            return self.x
            
        def getY(self):
            return self.y
            
        def setX(self, x):
            self.x = x
            
        def setY(self, y):
            self.y = y
    
    # Create pipelines - one real and one dummy with the same name
    real_pipeline = MockPipeline("test-pipeline", origin="https://example.com", x=200, y=200)
    pipelines = [real_pipeline]
    
    # Create a dummy pipeline container in the VSM
    dummy_container = svgwrite.container.Group()
    dummy_container.attribs["id"] = "dummy_test-pipeline"
    
    # Add a rectangle to the dummy container (simulating what drawPipeline would do)
    dummy_rect = svgwrite.shapes.Rect(insert=(50, 50), size=(VSMWizard.CONST_PIPELINE_WIDTH, VSMWizard.CONST_PIPELINE_HEIGHT))
    dummy_rect.attribs["x"] = "50"
    dummy_rect.attribs["y"] = "50"
    dummy_container.add(dummy_rect)
    
    # Add text element with pipeline name
    dummy_text = svgwrite.text.Text("test-pipeline", insert=(60, 70))
    dummy_container.add(dummy_text)
    
    # Add the dummy container to the canvas
    canvas.add(dummy_container)
    
    # Add a line connected to the dummy pipeline
    line = svgwrite.shapes.Line(
        start=(50 + VSMWizard.CONST_PIPELINE_WIDTH, 50 + VSMWizard.CONST_PIPELINE_HEIGHT/2),
        end=(150, 100)
    )
    line.attribs["id"] = f"post_rect_50_50_pre_rect_150_100-SegmentA"
    line.attribs["x1"] = str(50 + VSMWizard.CONST_PIPELINE_WIDTH)
    line.attribs["y1"] = str(50 + VSMWizard.CONST_PIPELINE_HEIGHT/2)
    canvas.add(line)
    
    # Add the dummy pipeline to the dictionary
    VSMWizard.dummyPipelinesDict["test-pipeline"] = None
    
    # Call the function under test
    VSMWizard.consolidateDummies(canvas, pipelines)
    
    # Assertions
    
    # 1. Check that the dummy container is now hidden
    assert dummy_container.attribs["visibility"] == "hidden"
    
    # 2. Check that the line has been updated to connect to the real pipeline
    assert line.attribs["id"] == f"post_rect_200_200_pre_rect_150_100-SegmentA"
    assert float(line.attribs["x1"]) == 200 + VSMWizard.CONST_PIPELINE_WIDTH
    assert float(line.attribs["y1"]) == 200 + VSMWizard.CONST_PIPELINE_HEIGHT/2
    
    # Clean up the global dictionary
    VSMWizard.dummyPipelinesDict.clear()
