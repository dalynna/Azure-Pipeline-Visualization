const { JSDOM } = require("jsdom");
const fs = require("fs");
const path = require("path");

// index.test.js

/**
 * @jest-environment jsdom
 */


describe("generateSaveFile", () => {
  let generateSaveFile, saveData, alertMock, createElementNSMock, createObjectURLMock;

  beforeAll(() => {
    // Load the index.js file
    const filePath = path.resolve(__dirname, "index.js");
    const scriptContent = fs.readFileSync(filePath, "utf8");
    const dom = new JSDOM(`<!DOCTYPE html><html><body><svg></svg></body></html>`, {
      runScripts: "dangerously",
      resources: "usable",
    });
    global.window = dom.window;
    global.document = dom.window.document;

    // Execute the script to load the functions
    const script = dom.window.document.createElement("script");
    script.textContent = scriptContent;
    dom.window.document.body.appendChild(script);

    // Extract the generateSaveFile function and saveData
    generateSaveFile = dom.window.generateSaveFile;
    saveData = dom.window.saveData;

    // Mock alert
    alertMock = jest.spyOn(global.window, "alert").mockImplementation(() => {});

    // Mock createElementNS
    createElementNSMock = jest.spyOn(global.document, "createElementNS").mockImplementation(() => {
      return {
        click: jest.fn(),
        setAttribute: jest.fn(),
        remove: jest.fn(),
      };
    });

    // Mock URL.createObjectURL
    createObjectURLMock = jest.spyOn(global.window.URL, "createObjectURL").mockImplementation(() => "mockURL");
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  it("should alert when saveData is empty", () => {
    saveData.length = 0; // Ensure saveData is empty
    generateSaveFile();
    expect(alertMock).toHaveBeenCalledWith("No pipelines have been moved yet.");
  });

  it("should generate a JSON file and trigger download when saveData is populated", () => {
    saveData.push({ id: "rect1", x: 100, y: 200 }); // Populate saveData

    const linkMock = {
      click: jest.fn(),
      setAttribute: jest.fn(),
      remove: jest.fn(),
    };
    createElementNSMock.mockReturnValue(linkMock);

    generateSaveFile();

    expect(createObjectURLMock).toHaveBeenCalled();
    expect(createElementNSMock).toHaveBeenCalledWith("http://www.w3.org/1999/xhtml", "a");
    expect(linkMock.setAttribute).toHaveBeenCalledWith("download", expect.stringContaining("_positions.json"));
    expect(linkMock.click).toHaveBeenCalled();
    expect(linkMock.remove).toHaveBeenCalled();
  });
});