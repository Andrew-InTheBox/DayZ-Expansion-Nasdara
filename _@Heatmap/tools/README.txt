DayZ Heatmap Visulaization Tool

This tool is a small website you can open with any browser on your local PC to inspect heatmap files.
The tool requires javascript to be enabled!

How to use:

1. Open the index.html (Nasdara is selected by default).
2. Select the map at the top of the page.
3. Drag and drop any number of heatmap files into the browser window.
4. Click Merge Data and Map to generate a combined image you can save using right click context

If the map is not present but you have a image of the map and know the maps size you can use Local Map and select the image and set the size yourself.

Adding your own map:
1. Add a your map to the mapSelect element.
2. Add the size of your map to mapSize.
3. Add a link to the image of your map to mapImage.
4. Open the website in your browser

Nasdara background and alignment:
- Uses ../../custom_scripts/assets/nasdara-map-background.png directly.
- World bounds are X 0 to 16384 and Z 0 to 16384 meters, matching the patrol explorer.
- The full rectangular PNG is scaled into a square map viewport; the overlay canvas
  uses exactly the same displayed dimensions, including when the page is resized.
- X increases to the right; Z increases upward. World (0, 0) is bottom-left,
  (16384, 16384) is top-right, and (8192, 8192) is the center.
- Keep tools/index.html in the server folder layout so the relative asset path works.
- The Nasdara background and session-file import work offline. The existing merged
  image export uses external html2canvas and FileSaver scripts and needs internet.
- Alignment assumes the supplied PNG covers the full world square. Landmark/pixel
  calibration of the source image has not been independently verified.
