// hover.js

const OFFSET_POSTLINE_X = 330;
const OFFSET_SEGMENT_X = 30;
const OFFSET_SEGMENT_Y = 50;
const OFFSET_ARROWHEAD_X = 50;
const OFFSET_ARROWHEAD_Y = 7;
const OFFSET_BOTTOM_X = 150;
const OFFSET_BOTTOM_Y = 100;
const OFFSET_RIGHT_X = 300;

function makeDraggable(evt) {
  var svg = evt.target;

  var selectedElement, offset, childElements = [], childOffsets = [];
  var selectedElement = false;
  let saveData = [];

  svg.addEventListener('mousedown', startDrag);
  svg.addEventListener('mousemove', drag);
  svg.addEventListener('mouseup', endDrag);
  svg.addEventListener('mouseleave', endDrag);


  /**
   * @name startDrag
   * @description Start the drag event
   * @param {Event} evt 
   * @returns {void}
   */
  function startDrag(evt) {
    evt.preventDefault();
  
    if (evt.target.localName !== "rect" || !evt.target.classList.contains('draggable')) return;
  
    selectedElement = evt.target;
    let clickPosition = getMousePosition(evt);
  
    // Set offset as the difference between where we clicked and the element's position
    offset = {
      x: clickPosition.x - parseFloat(selectedElement.getAttributeNS(null, "x")),
      y: clickPosition.y - parseFloat(selectedElement.getAttributeNS(null, "y"))
    };
  
    // Populate child elements and their offsets
    childElements = [];
    childOffsets = [];
    for (let i = 0; i < selectedElement.parentNode.children.length; i++) {
      let child = selectedElement.parentNode.children[i];
      if (child.classList.contains('draggable')) {
        childElements.push(child);
  
        if (child.localName === "circle") {
          childOffsets.push({
            x: parseFloat(child.getAttributeNS(null, "cx")) - clickPosition.x,
            y: parseFloat(child.getAttributeNS(null, "cy")) - clickPosition.y
          });
        } else if (child.localName === "a") {
          childOffsets.push({
            x: parseFloat(child.children[0].getAttributeNS(null, "x")) - clickPosition.x,
            y: parseFloat(child.children[0].getAttributeNS(null, "y")) - clickPosition.y
          });
        } else if (child.localName === "g") {
          for (let j = 0; j < child.children.length; j++) {
            childOffsets.push({
              x: parseFloat(child.children[j].getAttributeNS(null, "x")) - clickPosition.x,
              y: parseFloat(child.children[j].getAttributeNS(null, "y")) - clickPosition.y
            });
          }
        } else if (child.localName === "image" && child.id === "arrow") {
          childOffsets.push({
            x: parseFloat(child.getAttributeNS(null, "x")) - clickPosition.x,
            y: parseFloat(child.getAttributeNS(null, "y")) - clickPosition.y
          });
        } else {
          childOffsets.push({
            x: parseFloat(child.getAttributeNS(null, "x")) - clickPosition.x,
            y: parseFloat(child.getAttributeNS(null, "y")) - clickPosition.y
          });
        }
      }
    }
  }

  /**
   * @name getMousePosition
   * @description Get the mouse position on the SVG canvas
   * @param {*} clickEvent 
   * @returns {Object} x, y
   */
  function getMousePosition(clickEvent) {
    var CTM = svg.getScreenCTM();
    return {
      x: (clickEvent.clientX - CTM.e) / CTM.a,
      y: (clickEvent.clientY - CTM.f) / CTM.d
    };
  }

  /**
   * @name handlePreLines
   * @description Handles the drag animations for lines connected
   *  to the left side of selectedElement
   * @param {Element} selectedElement 
   * @returns {void}
   */
  function handlePreLines(selectedElement) {
    let lines = document.getElementsByTagName('line');

    let connectedLinesA = [];
    let connectedLinesB = [];

    let sourceX = 0;
    let sourceY = 0;

    // Grab all lines connected to left side of selectedElement
    for (let i = 0; i < lines.length; i++) {
      // If line is connected to selectedElement on left side (Pre_rect_x_y)
      if (lines[i].id.includes("pre_" + selectedElement.id)) {
        // Track seg a & b
        if (lines[i].id.includes("SegmentA")) {
          connectedLinesA.push(lines[i]);
        } else if (lines[i].id.includes("SegmentB")) {
          connectedLinesB.push(lines[i]);
        }
      }
    }
    
    for (let i = 0; i < connectedLinesA.length; i++) {
      // Find source element by checking all rects and their post lines
      let sourceElement = null;
      const rects = document.getElementsByTagName('rect');
      for (let j = 0; j < rects.length; j++) {
        const rect = rects[j];
        const rectLines = document.getElementsByTagName('line');
        
        // Check each line connected to this rect's post side
        for (let k = 0; k < rectLines.length; k++) {
          if (rectLines[k].id.includes("post_" + rect.id) && rectLines[k].id.includes("SegmentA")) {
            // Compare coordinates with current line
            if (rectLines[k].getAttributeNS(null, "x1") === connectedLinesA[i].getAttributeNS(null, "x1") &&
                rectLines[k].getAttributeNS(null, "y1") === connectedLinesA[i].getAttributeNS(null, "y1")) {
              sourceElement = rect;
              break;
            }
          }
        }
        if (sourceElement) break;
      }
      sourceX = parseFloat(sourceElement.getAttributeNS(null, "x"));
      sourceY = parseFloat(sourceElement.getAttributeNS(null, "y"));

      if (sourceElement) {
        // Check if line end is to the left of source element midpoint
        if (parseFloat(connectedLinesA[i].getAttributeNS(null, "x2")) <= sourceX + OFFSET_RIGHT_X) {
          //Check if selected element is below the source element
          if (parseFloat(selectedElement.getAttributeNS(null, "y")) > sourceY) {
            // Move line start to bottom of source element
            connectedLinesA[i].setAttributeNS(null, "x1", sourceX + OFFSET_BOTTOM_X);
            connectedLinesA[i].setAttributeNS(null, "y1", sourceY + OFFSET_BOTTOM_Y);
          } else {
            // Move line start to top of source element
            connectedLinesA[i].setAttributeNS(null, "x1", sourceX + OFFSET_BOTTOM_X);
            connectedLinesA[i].setAttributeNS(null, "y1", sourceY);
          }
        } else {
          connectedLinesA[i].setAttributeNS(null, "x1", sourceX + OFFSET_RIGHT_X);
          connectedLinesA[i].setAttributeNS(null, "y1", sourceY + OFFSET_SEGMENT_Y);
        }
      }

      // Update line end position
      if (parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X > parseFloat(sourceElement.getAttributeNS(null, "x")) + OFFSET_RIGHT_X) {
        connectedLinesA[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")) - OFFSET_SEGMENT_X);
        connectedLinesA[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_SEGMENT_Y);
      } else {
        if (parseFloat(selectedElement.getAttributeNS(null, "y")) > sourceY) {
          // line ends on top of selected element
          connectedLinesA[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X);
          connectedLinesA[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")) - OFFSET_SEGMENT_X);
        } else {
          // line ends below selected element
          connectedLinesA[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X);
          connectedLinesA[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_BOTTOM_Y + OFFSET_SEGMENT_X);
        }
      }
    }

    for (let i = 0; i < connectedLinesB.length; i++) {
      let lineID = connectedLinesB[i].id;
      lineID = lineID.replace("-SegmentB", "");
      var arrow = document.getElementById(lineID + "-arrow");
      var ax;
      var ay;

      // Find source element by checking all rects and their post lines
      let sourceElement = null;
      const rects = document.getElementsByTagName('rect');
      for (let j = 0; j < rects.length; j++) {
        const rect = rects[j];
        const rectLines = document.getElementsByTagName('line');
        
        // Check each line connected to this rect's post side
        for (let k = 0; k < rectLines.length; k++) {
          if (rectLines[k].id.includes("post_" + rect.id) && rectLines[k].id.includes("SegmentA")) {
            // Compare coordinates with current line
            if (rectLines[k].getAttributeNS(null, "x1") === connectedLinesA[i].getAttributeNS(null, "x1") &&
                rectLines[k].getAttributeNS(null, "y1") === connectedLinesA[i].getAttributeNS(null, "y1")) {
              sourceElement = rect;
              break;
            }
          }
        }
        if (sourceElement) break;
      }
      sourceX = parseFloat(sourceElement.getAttributeNS(null, "x"));
      sourceY = parseFloat(sourceElement.getAttributeNS(null, "y"));

      connectedLinesB[i].setAttributeNS(null, "x1", parseFloat(connectedLinesA[i].getAttributeNS(null, "x2")))
      connectedLinesB[i].setAttributeNS(null, "y1", parseFloat(connectedLinesA[i].getAttributeNS(null, "y2")))
      if (parseFloat(connectedLinesA[i].getAttributeNS(null, "x2")) < parseFloat(selectedElement.getAttributeNS(null, "x"))) {
        // line ends left of selected element
        connectedLinesB[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")))
        connectedLinesB[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_SEGMENT_Y)

        //position and rotate arrowhead
        arrow.setAttributeNS(null, "x", parseFloat(selectedElement.getAttributeNS(null, "x")) - 21);
        arrow.setAttributeNS(null, "y", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_SEGMENT_Y - 12);
        ax = parseFloat(arrow.getAttributeNS(null, "x"));
        ay = parseFloat(arrow.getAttributeNS(null, "y"));
        arrow.setAttribute("transform", `rotate(0 ${ax} ${ay})`);
      } else if (parseFloat(selectedElement.getAttributeNS(null, "y")) > sourceY) {
        // line ends on top of selected element
        connectedLinesB[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X)
        connectedLinesB[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")))
        
        //position and rotate arrowhead
        arrow.setAttributeNS(null, "x", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X + 12);
        arrow.setAttributeNS(null, "y", parseFloat(selectedElement.getAttributeNS(null, "y")) - 21);
        ax = parseFloat(arrow.getAttributeNS(null, "x"));
        ay = parseFloat(arrow.getAttributeNS(null, "y"));
        arrow.setAttribute("transform", `rotate(90 ${ax} ${ay})`);
      } else {
        // line ends below selected element
        connectedLinesB[i].setAttributeNS(null, "x2", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X);
        connectedLinesB[i].setAttributeNS(null, "y2", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_BOTTOM_Y);

        //position and rotate arrowhead
        arrow.setAttributeNS(null, "x", parseFloat(selectedElement.getAttributeNS(null, "x")) + OFFSET_BOTTOM_X - 12);
        arrow.setAttributeNS(null, "y", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_BOTTOM_Y + 21);
        ax = parseFloat(arrow.getAttributeNS(null, "x"));
        ay = parseFloat(arrow.getAttributeNS(null, "y"));
        arrow.setAttribute("transform", `rotate(270 ${ax} ${ay})`);
      }
    }
  }

  /**
   * @name handlePostLines
   * @description Handles the drag animations for lines connected
   * to the right side of selectedElement
   * @param {Element} selectedElement 
   * @returns {void}
   */
  function handlePostLines(selectedElement) {
    let lines = document.getElementsByTagName('line');

    let connectedLinesA = [];
    let connectedLinesB = [];

    // Grab all lines connected to right side of selectedElement
    for (let i = 0; i < lines.length; i++) {
      // If line is connected to selectedElement on right side (post_rect_x_y)
      if (lines[i].id.includes("post_" + selectedElement.id)) {
        // Track seg a & b
        if (lines[i].id.includes("SegmentA")) {
          connectedLinesA.push(lines[i]);
        } else if (lines[i].id.includes("SegmentB")) {
          connectedLinesB.push(lines[i]);
        }
      }
    }

    for (let i = 0; i < connectedLinesA.length; i++) {
      // Find next element by checking all rects and their pre lines
      let nextElement = null;
      const rects = document.getElementsByTagName('rect');
      for (let j = 0; j < rects.length; j++) {
        const rect = rects[j];
        const rectLines = document.getElementsByTagName('line');
        
        // Check each line connected to this rect's pre side
        for (let k = 0; k < rectLines.length; k++) {
          if (rectLines[k].id.includes("pre_" + rect.id) && rectLines[k].id.includes("SegmentA")) {
            // Compare coordinates with current line
            if (rectLines[k].getAttributeNS(null, "x1") === connectedLinesA[i].getAttributeNS(null, "x1") &&
                rectLines[k].getAttributeNS(null, "y1") === connectedLinesA[i].getAttributeNS(null, "y1")) {
                  nextElement = rect;
              break;
            }
          }
        }
        if (nextElement) break;
      }
      
      handlePreLines(nextElement);
    }
    /*
    for (let i = 0; i < connectedLinesA.length; i++) {
      connectedLinesA[i].setAttributeNS(null, "x1", parseFloat(selectedElement.getAttributeNS(null, "x")) - OFFSET_SEGMENT_X + OFFSET_POSTLINE_X)
      connectedLinesA[i].setAttributeNS(null, "y1", parseFloat(selectedElement.getAttributeNS(null, "y")) + OFFSET_SEGMENT_Y)
    }
    */
  }

  /**
   * @name handleLines
   * @description Handles the drag animations for lines connected
   * to the selected element
   * @param {*} selectedElement 
   * @returns {void}
   */
  function handleLines(selectedElement) {
    handlePreLines(selectedElement);
    handlePostLines(selectedElement);
  }

  /**
   * @name drag
   * @description Drag the selected element and all elements in 
   * the group
   * @param {Event} evt
   * @returns {void}
   */
  function drag(evt) {
    if (!selectedElement) return;
  
    evt.preventDefault();
  
    let coord = getMousePosition(evt);
  
    // Update the selected element's position
    selectedElement.setAttributeNS(null, "x", coord.x - offset.x);
    selectedElement.setAttributeNS(null, "y", coord.y - offset.y);
  
    // Move child elements based on initial offsets
    for (let i = 0; i < childElements.length; i++) {
      let child = childElements[i];
      if (child.localName === "circle") {
        child.setAttributeNS(null, "cx", coord.x + childOffsets[i].x);
        child.setAttributeNS(null, "cy", coord.y + childOffsets[i].y);
      } else if (child.localName === "a") {
        child.children[0].setAttributeNS(null, "x", coord.x + childOffsets[i].x);
        child.children[0].setAttributeNS(null, "y", coord.y + childOffsets[i].y);
      } else if (child.localName === "g") {
        for (let j = 0; j < child.children.length; j++) {
          child.children[j].setAttributeNS(null, "x", coord.x + childOffsets[i].x);
          child.children[j].setAttributeNS(null, "y", coord.y + childOffsets[i].y);
        }
      } else if (child.localName === "image" && child.id === "arrow") {
        child.setAttributeNS(null, "x", coord.x + childOffsets[i].x);
        child.setAttributeNS(null, "y", coord.y + childOffsets[i].y);
      } else {
        child.setAttributeNS(null, "x", coord.x + childOffsets[i].x);
        child.setAttributeNS(null, "y", coord.y + childOffsets[i].y);
      }
    }
  
    handleLines(selectedElement);
  }

  /**
   * @name endDrag
   * @description End the drag event, resets selectedElement and childElements
   * @param {void}
   * @returns {void}
   */
  function endDrag() {
    if (selectedElement) {
      const elementId = selectedElement.id;
      const x = parseInt(selectedElement.getAttributeNS(null, "x"));
      const y = parseInt(selectedElement.getAttributeNS(null, "y"));
  
      // Check if the element already exists in saveData[]
      let existingElement = saveData.find(el => el.id === elementId);
      if (existingElement) {
        existingElement.x = x;
        existingElement.y = y;
      } else {
        saveData.push({ id: elementId, x, y });
      }
    }
  
    selectedElement = null;
    childElements = [];
    childOffsets = [];
  }
  
  function generateSaveFile() {
    if (saveData.length === 0) {
      alert("No pipelines have been moved yet.");
      return;
    }
  
    // Convert JSON to a Blob
    const jsonBlob = new Blob([JSON.stringify(saveData, null, 2)], { type: "application/json" });
    
    // Create a temporary download link
    const link = document.createElementNS("http://www.w3.org/1999/xhtml", "a");
    link.href = URL.createObjectURL(jsonBlob);
    const jsonFileName = window.location.pathname.split("/").pop().replace(".svg", "") + "_positions.json";
    link.download = jsonFileName;
  
    // Append to SVG root and trigger download
    const svgRoot = document.documentElement;
    svgRoot.appendChild(link);
    link.click();
    svgRoot.removeChild(link);
  }  

  /**
   * @name init
   * @description Initialize line positions for all draggable elements
   * @returns {void}
   */
  function init() {
    const draggableElements = svg.querySelectorAll('.draggable');

    draggableElements.forEach(element => {
      if (element.localName === 'rect') {
        handleLines(element);
      }
    });

    document.getElementById("saveButtonGroup").addEventListener("click", generateSaveFile);
  }

  // Run init() after the SVG is loaded
  svg.addEventListener('load', init);

  // If the SVG is already loaded, initialize immediately
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    init();
  }
}
