from cgitb import text  # to center task!
import svgwrite
import os
import json
from pathlib import Path
import sys
from collections import deque, defaultdict

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
print(sys.path)

from YMLParser import parser
from VSMWizard import menu_gui

CONST_STROKE_WIDTH = 1
CONST_PIPELINE_WIDTH = 300
CONST_PIPELINE_HEIGHT = 100

CONST_ICON_MARGIN = 5
CONST_ICON_WIDTH = 30
CONST_ICON_HEIGHT = 30

CONST_ARROW_HEIGHT = 25

CONST_LANG_MARGIN = 68
CONST_LANG_WIDTH = 5
CONST_LANG_HEIGHT = 5

CONST_ARROW_X = 9
CONST_ARROW_Y = 12

ICON_PATH_MAP = {
    "python": "resources\\python.png",
    "java": "resources\\java.png",
    "c++": "resources\\c++.png",
    "javascript": "resources\\javascript.png",
    "artifact": "resources\\artifact.png",
    "dotnet": "resources\\dotnet.png",
    "node": "resources\\node.png",
    "powershell": "resources\\powershell.png",
    "npm": "resources\\npm.png",
}

CONST_GRADIENTS = {
    "dummyGradientTop": "#f0f0f0",
    "dummyGradientBottom": "#c0c0c0",
    "mainGradientTop": "#d8f3ff",
    "mainGradientBottom": "#89baff",
}

dummyPipelinesDict = {}


def insertIcon(canvas, href, x, y, width, height, description=None):
    # draw logic here - only puts it onto canvis
    # TODO Figure out how to place them into the Rectangle from drawRect
    img = svgwrite.image.Image(
        href, insert=(x, y), size=(width, height), class_="draggable"
    )

    if description != None:
        img.set_desc(description)

    return canvas.add(img)

# insert icon with rotation
def insertIconRotation(canvas, href, x, y, width, height, rotation, description=None):
    rotate = "rotate(" + str(rotation) + ' ' + str(x) + ' ' + str(y) + ')'
    img = svgwrite.image.Image(
        href, insert=(x, y), size=(width, height), class_="draggable", transform=rotate
    )

    img.set_desc(None)

    return canvas.add(img)


def drawLine(canvas, start, end, id=None):
    line = canvas.line(
        start=start, end=end, stroke="black", stroke_width=CONST_STROKE_WIDTH, id=id
    )
    canvas.add(line) 
    return line


def drawText(canvas, container, x, y, text, color="black"):
    return container.add(
        canvas.text(
            text,
            insert=(x, y),
            fill=color,
            class_="draggable",
            style="font-family:Helvetica;",
        )
    )


def drawRect(canvas, container, x, y, width, height, gradient):
    rect = canvas.rect(
        class_="draggable",
        insert=(x, y),
        size=(width, height),
        fill=gradient.get_paint_server(default="currentColor"),
        # stroke="blue",
        rx=10,
        ry=10,
        stroke_width=CONST_STROKE_WIDTH,
    )

    return container.add(rect)


def drawCircle(canvas, container, centerX, centerY, radius, fillColor):
    c = canvas.circle(
        center=(centerX, centerY),
        r=radius,
        fill=fillColor,
        class_="draggable",
    )

    container.add(c)
    return c


def drawHyperlink(canvas, x, y, text, url):
    # TODO figure out something better here?
    if url == None:
        return
    link = canvas.add(svgwrite.container.Hyperlink(url, class_="draggable"))
    link.add(
        svgwrite.text.Text(
            text,
            insert=(x, y),
            fill="black",
            style="text-decoration: underline;font-family:Helvetica;",
            class_="draggable",
        )
    )
    return link


def getIconPath(taskIcon):
    # Normalize inputs
    taskIcon = taskIcon.lower()

    # Return the icon path if it exists, otherwise return the default icon
    return ICON_PATH_MAP.get(taskIcon, "resources\\defaulttech.png")


def drawOSIcon(canvas, osString, x, y):
    # TODO: Replace with check for attribute includes 'windows' to account for
    #       specific OS versions
    if osString == "windows-latest":
        insertIcon(
            canvas,
            "resources\\windows.png",
            x + (CONST_PIPELINE_WIDTH - CONST_ICON_WIDTH - CONST_ICON_MARGIN),
            y + CONST_ICON_MARGIN,
            CONST_ICON_WIDTH,
            CONST_ICON_HEIGHT,
            osString,
        )
    elif osString == "ubuntu-latest":
        insertIcon(
            canvas,
            "resources\\ubuntu.png",
            x + (CONST_PIPELINE_WIDTH - CONST_ICON_WIDTH - CONST_ICON_MARGIN),
            y + CONST_ICON_MARGIN,
            CONST_ICON_WIDTH,
            CONST_ICON_HEIGHT,
            osString,
        )
    elif osString == "macOS-latest":
        insertIcon(
            canvas,
            "resources\\macOS.png",
            x + (CONST_PIPELINE_WIDTH - CONST_ICON_WIDTH - CONST_ICON_MARGIN),
            y + CONST_ICON_MARGIN,
            CONST_ICON_WIDTH,
            CONST_ICON_HEIGHT,
            osString,
        )


def handleDummyPipelineTrigger(canvas, container, text, x, y):
    # Split the text into three lines, after pipeline, before 'not found', not found third line
    textSegments = text.split("pipeline")
    textSegments[0] = textSegments[0] + "pipeline"
    textSegments[1] = textSegments[1].split("not found")[0]
    textSegments.append("not found")

    # calculate the X-coordinate to center the text
    for textSegmentIndex in range(len(textSegments)):
        estimated_text_width = len(textSegments[textSegmentIndex]) * 8
        x_centered = x + (CONST_PIPELINE_WIDTH - estimated_text_width) / 2
        drawText(
            canvas,
            container,
            x_centered,
            y + 35 + (textSegmentIndex * 20),
            textSegments[textSegmentIndex],
        )


def handleFileErrorTrigger(canvas, container, text, x, y):
    # Split the text into two lines, before 'File Error', and the error message
    textSegments = text.split("File Error")
    textSegments[0] = textSegments[0] + "File Error"
    badPath = textSegments[1].split("for:")[1]
    textSegments[1] = textSegments[1].split("for:")[0] + "for:"
    textSegments.append(badPath)

    # calculate the X-coordinate to center the text
    for textSegmentIndex in range(len(textSegments)):
        estimated_text_width = len(textSegments[textSegmentIndex]) * 8
        x_centered = x + (CONST_PIPELINE_WIDTH - estimated_text_width) / 2
        drawText(
            canvas,
            container,
            x_centered,
            y + 35 + (textSegmentIndex * 20),
            textSegments[textSegmentIndex],
        )


def drawTrigger(canvas, container, triggerString, x, y):
    if triggerString != None:
        text = triggerString

        # estimate the text width based on the length of the text
        estimated_text_width = len(text) * 8  # adjust the factor for the font

        # If width > 40, split the text into two lines
        if estimated_text_width > 300:
            # Handle dummy pipeline trigger drawing
            if "not found" in text:
                handleDummyPipelineTrigger(canvas, container, text, x, y)

            # Handle filepath error trigger drawing
            elif "File Error" in text:
                handleFileErrorTrigger(canvas, container, text, x, y)
        else:
            # calculate the X-coordinate to center the text
            x_centered = x + (CONST_PIPELINE_WIDTH - estimated_text_width) / 2

            # Pass the calculated X-coordinate to the drawText functon
            drawText(canvas, container, x_centered, y + 50, text)

    else:
        print("No trigger found")


def drawHiddenContainer(canvas, parentContainer, rect_id, x, y):
    # Draw gradients for hidden container
    hiddenContainerYellowGradient = canvas.linearGradient((0, 0), (0, 1))
    canvas.defs.add(hiddenContainerYellowGradient)
    hiddenContainerYellowGradient.add_stop_color(0, "#fffecd")
    hiddenContainerYellowGradient.add_stop_color(0.7, "#ffe8a4")

    hiddenContainer = svgwrite.container.Group()

    hiddenRect = drawRect(
        canvas,
        hiddenContainer,
        x + CONST_ICON_WIDTH,
        y + CONST_ICON_WIDTH,
        CONST_PIPELINE_WIDTH,
        CONST_PIPELINE_HEIGHT,
        hiddenContainerYellowGradient,
    )

    hiddenContainer["visibility"] = "hidden"
    hiddenRect_id = rect_id + "_hover"
    hiddenContainer["id"] = hiddenRect_id
    hiddenContainer["class"] = "draggable"

    hiddenContainer.add(
        svgwrite.animate.Animate(
            attributeName="visibility",
            values="visible",
            dur="3.0s",
            begin=f"{rect_id}.mousedown",
            # end=f"{rect_id}.mouseup",
            repeatCount="1",
            fill="freeze",
        )
    )

    hiddenContainer.add(
        svgwrite.animate.Animate(
            attributeName="visibility",
            values="hidden",
            dur="0.0s",
            begin=f"{hiddenRect_id}.mousedown",
            end=f"{rect_id}.mousedown",
            repeatCount="1",
            fill="freeze",
        )
    )

    hiddenContainer.add(hiddenRect)

    # TODO: This is a POC for drawing inside the hidden container, needs to be
    #       replaced with logic to parse useful info from the YML and populate the
    #       hidden container
    drawOSIcon(
        hiddenContainer, "windows-latest", x + CONST_ICON_WIDTH, y + CONST_ICON_WIDTH
    )

    # Add the hidden container group to the visible container group
    # This is so the hidden container is a child of the visible container,
    # allowing it to follow when dragged
    parentContainer.add(hiddenContainer)

    canvas.add(hiddenContainer)


def handleDuplicateTasks(canvas, visibleContainer, Pipeline, x, y):
    drawIndex = 0
    dupeCount = 2
    additionalTaskCount = 0
    for index in range(len(Pipeline.getTasks())):
        taskIcon = Pipeline.getTasks()[index]

        taskIconPath = getIconPath(taskIcon)
        # Checking to see if there are tasks in the IconPath
        if taskIconPath is not None:
            # if the pipeline is to generate an artifact
            if taskIcon == "artifact":
                insertIcon(
                    visibleContainer,
                    taskIconPath,
                    x + (CONST_PIPELINE_WIDTH - CONST_ICON_WIDTH - CONST_ICON_MARGIN),
                    y + CONST_LANG_MARGIN,
                    CONST_ICON_WIDTH,
                    CONST_ICON_HEIGHT,
                )
            # for all the other icons in the pipeline
            else:
                # If icon is a duplicate of previously drawn icon, add a counter to the icon
                if (
                    getIconPath(Pipeline.getTasks()[index])
                    == getIconPath(Pipeline.getTasks()[index - 1])
                    and index != 0
                ):
                    drawCircle(
                        canvas,
                        visibleContainer,
                        x + 10 + 30 + (CONST_LANG_WIDTH) * (10 * (drawIndex - 1)),
                        y + CONST_LANG_MARGIN,
                        10,
                        "red",
                    )
                    drawText(
                        canvas,
                        visibleContainer,
                        x + 10 + 26 + (CONST_LANG_WIDTH) * (10 * (drawIndex - 1)),
                        y + CONST_LANG_MARGIN + 5,
                        dupeCount,
                        "white",
                    )
                    dupeCount += 1
                else:
                    # If at the end of the box's bounds, put an additional tasks counter instead
                    if drawIndex < 5 or (additionalTaskCount == 0 and index == len(Pipeline.getTasks()) - 1):
                        dupeCount = 2
                        insertIcon(
                            visibleContainer,
                            taskIconPath,
                            x + 10 + (CONST_LANG_WIDTH) * (10 * drawIndex),
                            y + CONST_LANG_MARGIN,
                            CONST_ICON_WIDTH,
                            CONST_ICON_HEIGHT,
                            taskIcon,
                        )
                        drawIndex += 1
                    else:
                        additionalTaskCount += 1
                        drawCircle(
                        canvas,
                        visibleContainer,
                        x + 10 + 15 + (CONST_LANG_WIDTH) * (10 * (drawIndex)),
                        y + 15 + CONST_LANG_MARGIN,
                        15,
                        "red",
                        )
                        drawText(
                            canvas,
                            visibleContainer,
                            x + 10 + 5 + (CONST_LANG_WIDTH) * (10 * (drawIndex)),
                            y + 15 + CONST_LANG_MARGIN + 5,
                            '+' + str(additionalTaskCount),
                            "white",
                        )


def drawPipeline(canvas, x, y, Pipeline):
    # If pipeline is a dummy, color it gray 
    if isDummy(Pipeline):
        mainContainerGradient = canvas.linearGradient((0, 0), (0, 1))
        canvas.defs.add(mainContainerGradient)
        mainContainerGradient.add_stop_color(0, CONST_GRADIENTS["dummyGradientTop"])
        mainContainerGradient.add_stop_color(
            0.7, CONST_GRADIENTS["dummyGradientBottom"]
        )
    # else, color it blue
    else:
        # Draw gradients for main container
        mainContainerGradient = canvas.linearGradient((0, 0), (0, 1))
        canvas.defs.add(mainContainerGradient)
        mainContainerGradient.add_stop_color(0, CONST_GRADIENTS["mainGradientTop"])
        mainContainerGradient.add_stop_color(0.7, CONST_GRADIENTS["mainGradientBottom"])

    # Draw rectangle
    # create new container
    visibleContainer = svgwrite.container.Group()

    rect = drawRect(
        canvas,
        visibleContainer,
        x,
        y,
        CONST_PIPELINE_WIDTH,
        CONST_PIPELINE_HEIGHT,
        mainContainerGradient,
    )

    # Draw text
    drawHyperlink(
        visibleContainer,
        x + 10,
        y + 20,
        Pipeline.getName(),
        Pipeline.getOrigin(),
    )

    # Draw OS icon
    drawOSIcon(visibleContainer, Pipeline.getOS(), x, y)

    # Draw trigger
    drawTrigger(canvas, visibleContainer, Pipeline.getTrigger(), x, y)

    # Draw tasks
    handleDuplicateTasks(canvas, visibleContainer, Pipeline, x, y)

    # Adding a unique ID to the rectangle we create
    rect_id = f"rect_{x}_{y}"
    rect["id"] = rect_id

    # TODO: If you'd like to add a hidden container that displays on click,
    #       uncomment the line below
    # drawHiddenContainer(canvas, visibleContainer, rect_id, x, y)

    # Add the container to the canvas
    canvas.add(visibleContainer)

    return visibleContainer


def syncDependencyCoordinates(pipelines):
    for pipeline in pipelines:
        for dep in pipeline.getDependencies():
            for otherPipeline in pipelines:
                if dep.getName() is not None and otherPipeline.getName() is not None:
                    if dep.getName().lower() == otherPipeline.getName().lower():
                        dep.setX(otherPipeline.getX())
                        dep.setY(otherPipeline.getY())


def willCollide(plToDraw, pipelines):
    for p in pipelines:
        # Don't check exact coordinates, check if the width and height overlap
        if (plToDraw.getX() < p.getX() + CONST_PIPELINE_WIDTH) and (
            plToDraw.getY() < p.getY() + CONST_PIPELINE_HEIGHT
        ):
            if p.getX() == 0 and p.getY() == 0:
                continue
            return True
    return False


def isDummy(pipeline):
    # Easiest way to check if a pipeline is a dummy is the origin is None
    return pipeline.getOrigin() is None


def consolidateDummies(vsm, pipelines):
    """
    Consolidates dummy pipelines into real pipelines

    Args:
        vsm (svgwrite.Drawing): The VSM to add the pipelines to
        pipelines (Array(Pipeline)): A list of Pipeline objects to add to the VSM

    Returns:
        None

    Raises:
        None
    """

    dummyCoords = []

    print("Cleaning up dummy pipelines...")

    # Check if the pipeline name is in the dictionary
    # If it is, replace the pipeline with the real pipeline
    for pipeline in pipelines:
        # Only delete dummy pipelines if we're replacing with a drawn pipeline
        if isDummy(pipeline):
            continue
        # Only check after confirming the pipeline has a dummy drawn
        elif pipeline.getName() in dummyPipelinesDict:

            # Find the drawn rectangle with the same name as dummy
            for pipelineContainer in vsm.elements:
                # Quick skips when we can
                if pipelineContainer.elements is None:
                    continue
                if pipelineContainer.attribs.get("id") is None:
                    continue
                # Check the container is a dummy pipeline
                if "dummy" in pipelineContainer.attribs.get("id"):
                    # Check text element matches dummy pipeline name
                    for element in pipelineContainer.elements:
                        if element.elementname == "text":
                            # If text shows we're at a correct dummy,
                            # save the coordinates to the rectangle
                            if pipeline.getName() in element.text:
                                # Rect are drawn before text, index 0 is the rect
                                dummy_x = pipelineContainer.elements[0].attribs.get("x")
                                dummy_y = pipelineContainer.elements[0].attribs.get("y")
                                dummyCoords.append((dummy_x, dummy_y))
                                # Kill this dummy
                                # TODO kinda nasty fix that later
                                pipelineContainer.attribs["visibility"] = "hidden"

        if len(dummyCoords) > 0:
            for element in vsm.elements:
                if element.elementname == "line":
                    for coords in dummyCoords:
                        # If line ID contains "post_rect_xcoord_ycoord"
                        if f"post_rect_{coords[0]}_{coords[1]}_" in element.attribs.get(
                            "id"
                        ) and "SegmentA" in element.attribs.get("id"):
                            # Replace x1,y1 of lines with real pipeline coordinates
                            oldID = element.attribs.get("id")
                            id_chunks = oldID.split("pre")
                            # ID Chunks now contains ["post_rect_xcoord_ycoord", "_xcoord_ycoord-SegmentA"]
                            newID = (
                                f"post_rect_{pipeline.getX()}_{pipeline.getY()}_"
                                + "pre"
                                + id_chunks[1]
                            )
                            element.attribs["id"] = newID

                            element.attribs["x1"] = (
                                pipeline.getX() + CONST_PIPELINE_WIDTH
                            )
                            element.attribs["y1"] = pipeline.getY() + (
                                CONST_PIPELINE_HEIGHT / 2
                            )
                            break


def drawDummyPipeline(vsm, pipelines, dependency, x_coord, y_coord):
    print("Dependency not drawn")
    dummyPipeline = parser.createPipeline("")
    dummyPipeline.setName(dependency.getName())
    dummyPipeline.setTrigger(f"Dependent pipeline {dependency.getName()} not found")
    dummyPipeline.setX(x_coord)
    dummyPipeline.setY(y_coord)
    # Offset dummy pipeline so it's not colliding with another
    while willCollide(dummyPipeline, pipelines):
        y_coord += CONST_PIPELINE_HEIGHT + 50
        dummyPipeline.setY(y_coord)

    dependency.setX(x_coord)
    dependency.setY(y_coord)
    container = drawPipeline(vsm, x_coord, y_coord, dummyPipeline)
    # Set id of container to "dummy" + pipeline name for easy identification
    container.attribs["id"] = "dummy_" + dummyPipeline.getName()

    # Sync coordinates after drawing dummy pipeline
    syncDependencyCoordinates(pipelines)
    print("Dummy dep drawn:" + dummyPipeline.getName())
    # Add name of dummy pipeline to dictionary
    dummyPipelinesDict[dummyPipeline.getName()] = dummyPipeline
    print("At coords: " + str(x_coord) + ", " + str(y_coord))
    pipelines.append(dummyPipeline)
    return x_coord, y_coord


def checkDepenciesDrawn(vsm, pipelines, newPipelineIndex):
    x_coord, y_coord = 50, 50
    #a_coord, b_coord = 

    # Find the x coordinate of the dependency
    for d in pipelines[newPipelineIndex].getDependencies():
        depDrawn = False

        # Check if the dependency is already drawn in list of existing pipelines.
        # Loop through all pipelines from zero up to new index to check the pipelines that have already been drawn
        for otherPipelinesIndex in range(newPipelineIndex):
            if (
                d.getName() is not None
                and pipelines[otherPipelinesIndex].getName() is not None
            ):
                if (
                    d.getName().lower()
                    == pipelines[otherPipelinesIndex].getName().lower()
                ):
                    # Dependency is already drawn, update coordinates
                    x_coord = pipelines[otherPipelinesIndex].getX()
                    x_coord += CONST_PIPELINE_WIDTH + 50
                    depDrawn = True

        # If dependency not found, draw dummy rect and offset from that
        if not depDrawn:
            print(
                "\nDrawing dummy pipeline for dependency: "
                + d.getName()
                + " at "
                + str(x_coord)
                + ", "
                + str(y_coord)
                + "\n"
            )
            x_coord, y_coord = drawDummyPipeline(vsm, pipelines, d, x_coord, y_coord)
            depDrawn = True

    # If there are sibling dependencies, draw below the sibling
    # find max y for sibling dependencies
    maxX = 0
    maxY = 0
    for p in pipelines:
        for d in p.getDependencies():
            if (
                d.getName()
                == pipelines[newPipelineIndex].getDependencies()[0].getName()
            ):
                if p.getX() > maxX:
                    maxX = p.getX()
                    maxY = p.getY()
                    # offset new pipeline below sibling
                    y_coord = CONST_PIPELINE_WIDTH + 5

    return x_coord, y_coord


def animateLine(line, rectID):
    """
    This function animates the given line by changing its stroke color when the associated box is hovered over.

    Args:
    - line: The line to be animated.
    - rectID: The ID of the associated box.


    Returns:
        None

    Raises:
        None
    """

    line.add(
        svgwrite.animate.Animate(
            attributeName="stroke",
            values="black;white;black",
            dur="1.0s",
            begin=f"{rectID}.mouseover",
            end=f"{rectID}.mouseout",
            repeatCount="500",
            fill="freeze",
        )
    )

    line.add(
        svgwrite.animate.Animate(
            attributeName="stroke",
            values="white;black",
            dur="0.5s",
            begin=f"{rectID}.mouseout",
            end=f"{rectID}.mouseover",
            fill="freeze",
        )
    )


def connectDependencies(vsm, container, pipelines, newPipelineIndex):
    """
    Connects dependencies to the new pipeline by drawing lines between them

    Args:
        vsm (svgwrite.Drawing): The VSM to add the pipelines to
        container (svgwrite.container.Group): The container to add the lines to
        pipelines (Array(Pipeline)): A list of Pipeline objects to add to the VSM
        newPipelineIndex (int): The index of the pipeline to connect dependencies to

    Returns:
        None

    Raises:
        None
    """
    dep = pipelines[newPipelineIndex].getDependencies()
    for d in dep:
        print(
            f"(connectingDependencies) Drawing lines from:  {str(d.getName())} ({d.getX()}, {d.getY()}) to {str(pipelines[newPipelineIndex].getName())}  ({pipelines[newPipelineIndex].getX()}, {pipelines[newPipelineIndex].getY()}"
        )

        # Line begins at the right edge of the dependency
        start = (
            d.getX() + CONST_PIPELINE_WIDTH,
            d.getY() + (CONST_PIPELINE_HEIGHT / 2),
        )
        # Line may begin from the top middle of another pipeline
        top = (
            d.getX() + (CONST_PIPELINE_WIDTH / 2),
            d.getY(),
        )
        # Line may begin from the bottom middle of another pipeline
        bottom = (
            d.getX() + (CONST_PIPELINE_WIDTH / 2),
            d.getY() + CONST_PIPELINE_HEIGHT,
        )

        # Line ends at the left edge of the new pipeline
        end = (
            pipelines[newPipelineIndex].getX() - 30,
            pipelines[newPipelineIndex].getY() + (CONST_PIPELINE_HEIGHT / 2),
        )

        # Line ends at the top edge of the new pipeline
        end_top = (
            pipelines[newPipelineIndex].getX() + (CONST_PIPELINE_WIDTH / 2),
            pipelines[newPipelineIndex].getY() - 30,
        )

        # Line ends at the bottom edge of the new pipeline
        end_bottom = (
            pipelines[newPipelineIndex].getX() + (CONST_PIPELINE_WIDTH / 2),
            pipelines[newPipelineIndex].getY() + CONST_PIPELINE_HEIGHT + 30,
        )

        # Arrow line ends at the left edge of the new pipeline
        end_arrow = (
                pipelines[newPipelineIndex].getX(),
                pipelines[newPipelineIndex].getY() + (CONST_PIPELINE_HEIGHT / 2)
        )

        # Arrow line ends at the top edge of the new pipeline
        end_arrow_top = (
            pipelines[newPipelineIndex].getX() + (CONST_PIPELINE_WIDTH / 2),
            pipelines[newPipelineIndex].getY(),
        )

        # Arrow line ends at the bottom edge of the new pipeline
        end_arrow_bottom = (
            pipelines[newPipelineIndex].getX() + (CONST_PIPELINE_WIDTH / 2),
            pipelines[newPipelineIndex].getY() + CONST_PIPELINE_HEIGHT,
        )

        # default arrowhead position and rotation (point to the right)
        arrowhead_x = end[0] + CONST_ARROW_X
        arrowhead_y = end[1] - CONST_ARROW_Y
        arrowhead_rotation = 0

        # Line ID is formatted as
        # "post_0_0_pre_400_150"
        # Read as "Line between (0,0) and (400,150)"
        lineID = f"post_rect_{d.getX()}_{d.getY()}_pre_rect_{pipelines[newPipelineIndex].getX()}_{pipelines[newPipelineIndex].getY()}"

        #Depending on where the second box is, it will detect if it is not to the right then below or above the previous pipeline box
        if (pipelines[newPipelineIndex].getX() - 30 < d.getX() + CONST_PIPELINE_WIDTH):
            if pipelines[newPipelineIndex].getY() > d.getY():
                start = bottom
            else:
                start = top 
        #If it is to the right, its placed to the right of the prev pipeline

        # If the middle of the second box is to the left of the right edge of the first box, it will connect to the top or bottom
        if (pipelines[newPipelineIndex].getX() + (CONST_PIPELINE_WIDTH / 2) < d.getX() + CONST_PIPELINE_WIDTH):
            if pipelines[newPipelineIndex].getY() > d.getY():
                end = end_top
                end_arrow = end_arrow_top
                arrowhead_x = end[0] + CONST_ARROW_Y
                arrowhead_y = end[1] + CONST_ARROW_X
                arrowhead_rotation = 90
            else:
                end = end_bottom 
                end_arrow = end_arrow_bottom
                arrowhead_x = end[0] + CONST_ARROW_Y
                arrowhead_y = end[1] - CONST_ARROW_X
                arrowhead_rotation = 270
        # otherwise it will connect to the left

        
        # Draw first line segment
        lineA = drawLine(
            vsm,
            start,
            end,
            id=f"{lineID}-SegmentA",
        )
        # Draw second line segment (arrow)
        lineB = drawLine(
            vsm,
            end,
            end_arrow,
            id=f"{lineID}-SegmentB",
        )

        # Add animations for line segments
        animateLine(
            lineA,
            f"rect_{pipelines[newPipelineIndex].getX()}_{pipelines[newPipelineIndex].getY()}",
        )
        animateLine(
            lineB,
            f"rect_{pipelines[newPipelineIndex].getX()}_{pipelines[newPipelineIndex].getY()}",
        )

        arrow = insertIconRotation(
            container,
            "resources\\arrowhead.png",
            arrowhead_x,
            arrowhead_y,
            CONST_ARROW_HEIGHT,
            CONST_ARROW_HEIGHT,
            arrowhead_rotation
        )

        arrow["id"] = lineID + "-arrow"

        # checking the current pipelines
        print("IN ConnectDependencies(): ")
        for i in range(len(pipelines)):
            print(
                "Pipeline "
                + str(i)
                + " on our canvas: "
                + str(pipelines[i].getName())
                + " X: "
                + str(pipelines[i].getX())
                + " Y: "
                + str(pipelines[i].getY())
            )

def alignPipelineChain(y_coord, maxSiblings, chain):
    if maxSiblings > 0:
        new_y_offset = maxSiblings * 150 + 50
    else:
        new_y_offset = 150

    for siblings in chain:
        i = 1
        for pipeline in siblings:
            offset = new_y_offset / (len(siblings) + 1)
            y_pos = y_coord + (offset * i) - 50
            pipeline.setY(int(y_pos))
            i = i + 1

    return int(new_y_offset)


def addPipelinesToVSM(vsm, pipelines):
    """Adds a list of multiple pipelines to the VSM

    Args:
        vsm (svgwrite.Drawing): The VSM to add the pipelines to
        pipelines (Array(Pipeline)):       A list of Pipeline objects to add to the VSM

    Returns:
        None

    Raises:
        None
    """

    # As it goes through the pipelines, it will append each to an array. If the next pipeline is a sibling of another depedent pipeline,
    # it will pair it with the previous one and increase the sibling count and check if the max sibling count needs to change.
    # Once it gets to a pipeline that is not dependent on anything, it will first go through that array and center all the pipelines y coords
    # based on the max sibling count. Then the array is cleared and the new line y coord is adjusted to be under that chain.

    maxSiblings = 0
    chain = []
    y_offset = 0

    # For each pipeline in pipelines
    for newPipelineIndex in range(len(pipelines)):
        # Minimum x, y is 50,50
        # These coords use to track where to draw the next pipeline
        x_coord = 50
        y_coord = 50 + y_offset

        # If pipeline depends on another pipeline, draw to the right of dependency
        if len(pipelines[newPipelineIndex].getDependencies()) > 0:
            x_coord, y_coord = checkDepenciesDrawn(vsm, pipelines, newPipelineIndex)
            y_coord += y_offset

            # If sibling of the last pipeline, append to the last chain element, otherwise append to the end of the chain
            if newPipelineIndex - 1 >= 0 and newPipelineIndex - 1 < len(pipelines):
                if len(chain) > 0 and pipelines[newPipelineIndex - 1].getX() == x_coord:
                    chain[-1].append(pipelines[newPipelineIndex])
                    if len(chain[-1]) > maxSiblings:
                        maxSiblings = len(chain[-1])
                else:
                    chain.append([pipelines[newPipelineIndex]])
        
        # Update coords to new values at the right of their dependencies
        pipelines[newPipelineIndex].setX(x_coord)
        pipelines[newPipelineIndex].setY(y_coord)

        if len(pipelines[newPipelineIndex].getDependencies()) <= 0 or newPipelineIndex == len(pipelines) - 1:
            # align pipelines in the chain to be centered and clear the chain for the next row
            y_offset += alignPipelineChain(y_coord, maxSiblings, chain)
            y_coord += y_offset
            chain.clear()
            maxSiblings = 0
            chain.append([pipelines[newPipelineIndex]])

    for pipelineIndex in range(len(pipelines)):
        x_coord = pipelines[pipelineIndex].getX()
        y_coord = pipelines[pipelineIndex].getY()

        # Sync coordinates before checking collisions
        # Ensure pipeline dependency objects reflect what is actually drawn on screen
        syncDependencyCoordinates(pipelines)

        # Check incoming pipeline for collisions with existing pipelines
        #while willCollide(
        #    pipelines[pipelineIndex],
        #    # Black magic to remove the incoming pipeline from the list of pipelines
        #    # Because the incoming pipeline will always collide with itself
        #    list(filter(lambda x: x != pipelines[pipelineIndex], pipelines)),
        #):
            # Continue to offset pipeline coordinates by pipeline height + 50
            # until the new pipeline does not collide with any existing pipelines
        #    y_coord += CONST_PIPELINE_HEIGHT + 50

        #    pipelines[pipelineIndex].setY(y_coord)

        while any(
            i != pipelineIndex and 
            pipelines[i].getX() == x_coord and 
            pipelines[i].getY() == y_coord
            for i in range(len(pipelines))
        ):
            y_coord += 1

        pipelines[pipelineIndex].setX(x_coord)
        pipelines[pipelineIndex].setY(y_coord)
        print(
            f"Drawing {pipelines[pipelineIndex].getName()} at {x_coord}, {y_coord}"
        )
        # Draw the pipeline, save the container object returned
        pipelineContainer = drawPipeline(
            vsm, x_coord, y_coord, pipelines[pipelineIndex]
        )

        # Draw line from dependencies to new pipeline
        print("CONNECTING LINES - message inside addPipelineToVSM")
        connectDependencies(vsm, pipelineContainer, pipelines, pipelineIndex)


def resizeSVG(vsm):
    """
    Resize the SVG by setting the width and height of the canvas based on the elements' positions.

    Args:
        vsm (dict): The SVG data represented as a dictionary.

    Returns:
        dict: The updated SVG data with the width and height adjusted.
    """
    # Set the width and height of the canvas
    max_x, max_y = 3000 - CONST_PIPELINE_WIDTH, 3000 - CONST_PIPELINE_HEIGHT

    for group in vsm.elements:
        for e in group.elements:
            if e.attribs.get("x") is not None:
                x = int(float(e.attribs.get("x")))
                y = int(float(e.attribs.get("y")))
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    vsm["width"] = max_x + CONST_PIPELINE_WIDTH
    vsm["height"] = max_y + CONST_PIPELINE_HEIGHT
    return vsm


def sortPipelines(pipelines):
    # Step 1: Build dependencies list
    dependencies = []
    for pipeline in pipelines:
        for dep in pipeline.getDependencies():
            dependencies.append((dep.getName(), pipeline.getName()))

    # Step 2: Build adjacency list and in-degree dictionary
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    for parent, child in dependencies:
        graph[parent].append(child)
        in_degree[child] += 1
        if parent not in in_degree:
            in_degree[parent] = 0

    # Step 3: Identify independent pipelines (no dependencies)
    queue = deque(sorted([node for node in in_degree if in_degree[node] == 0]))

    # Step 4: Process chains of dependent pipelines
    sorted_list = []  # Maintain full dependency chains
    visited = set()

    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        chain = []  # Store full dependency chain
        chain_queue = deque([node])

        while chain_queue:
            current = chain_queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            chain.append(current)
            for neighbor in sorted(graph[current]):  # Process dependencies
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    chain_queue.append(neighbor)

        sorted_list.append(chain)  # Add full chain to sorted list

    # Flatten the chains into a single sorted order
    ordered_names = [name for chain in sorted_list for name in chain]

    # Step 5: Sort pipelines based on dependency chain order
    name_index_map = {name: i for i, name in enumerate(ordered_names)}
    pipelines.sort(key=lambda pipeline: name_index_map.get(pipeline.getName(), float('inf')))


def addSaveButton(canvas):
    button_group = canvas.g(id="saveButtonGroup")
    
    rect = canvas.rect(insert=(10, 10), size=(130, 30), fill="lightgray", rx=5, ry=5, id="saveButton")
    button_group.add(rect)
    
    text = canvas.text("Save Positions", insert=(20, 30), fill="black", style="font-family:Helvetica;cursor:pointer;", id="saveButtonText")
    button_group.add(text)

    canvas.add(button_group)

def generate(vsm_name):
    config_data = None

    try:
        # Build OS-agnostic path to configuration file
        path_to_config_file = os.path.join(os.getcwd(), "config", "yml_url_config.json")

        # Read the JSON configuration file
        with open(path_to_config_file, "r") as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        message = "Error: File not found. Confirm path is `$config\\yml_url_config.json`."
        print(message)
        return message
    except json.JSONDecodeError:
        message = "Error: Failed to decode JSON configuration file. Check trailing commas, hanging brackets, etc."
        print(message)
        return message
    except Exception as e:
        message = "Unexpected error:", str(e)
        print(message)
        return message

    pipelines = []

    # Create a pipeline object for every yml file read
    for spec in config_data["yml_filepath"]:
        # Load in YML file as object
        ymlObject = parser.parse_yml_file(spec)

        # Create pipeline object from YML file
        pl = None
        if ymlObject is None:
            # We still want to create a pipeline to display an error to the user
            pl = parser.createPipeline("")
            pl.setTrigger(f"File Error check config file path for: {spec[1]}")
        else:
            pl = parser.createPipeline(ymlObject)

        pipelines.append(pl)

    if(vsm_name == ""):
        fileName = pipelines[len(pipelines) - 1].getName() + "_VSM.svg"
    else:
        fileName = vsm_name + ".svg"

    vsm = svgwrite.Drawing(fileName, profile="full", onload="makeDraggable(evt)")

    sortPipelines(pipelines)

    for p in pipelines:
        print("order ", p.getName())

    # Draw pipeline with parameters on SVG file
    addPipelinesToVSM(vsm, pipelines)

    # Check for any dummy pipelines that need to be replaced.
    # This is done after all pipelines are drawn, and handles the scenario
    # where the config file is out of order.
    consolidateDummies(vsm, pipelines)

    # Add the save button to the SVG
    addSaveButton(vsm)

    vsm.add(svgwrite.container.Script(href=".\\index.js"))

    # Resize the SVG to fit all elements if necessary
    vsm = resizeSVG(vsm)

    # Save the vsm to the canvas.
    vsm.save()

    # Try to delete the existing symlink if it exists
    if os.path.islink("latest.svg"):
        try:
            os.remove("latest.svg")  # Remove the old symlink
        except OSError as e:
            print(f"Error deleting existing symlink: {e}")
            sys.exit(1)

    # Create symlink to vsm so it can be viewed in browser
    try:
        os.symlink(fileName, "latest.svg")
    except OSError:
        print(
            "The VSM was created successfully, but failed to alias and create symlink for %s. Try running as admin."
            % fileName
        )
    except:
        print("Unexpected error: ", sys.exc_info()[0])
        raise

def main():
    gui = menu_gui.MenuGUI()
    gui.run()

if __name__ == "__main__":
    main()
