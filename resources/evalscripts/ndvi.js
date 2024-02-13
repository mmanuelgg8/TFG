//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 2 }
  };
}

const ramp = [
  [-1, 0x660033], // Dark purple for non-vegetated areas (clouds, water, snow)
  [-0.1, 0x999999], // Gray for rocks and bare soil
  [0, 0xffffff], // White for empty areas (rocks, sand, snow)
  [0.1, 0xffff00], // Yellow for sparse vegetation (shrubs, grasslands)
  [0.2, 0x00ff00], // Green for moderate vegetation (meadows, crops)
  [0.3, 0x008000], // Dark green for dense vegetation (forests)
  [0.6, 0x228b22], // Forest green for temperate forests
  [0.8, 0x2e8b57] // Sea green for tropical forests
];

const visualizer = new ColorRampVisualizer(ramp);

function evaluatePixel(samples) {
  // let ndvi = index(samples.B08, samples.B04);
  // let imgVals = visualizer.process(ndvi);
  // return imgVals.concat(samples.dataMask);
  // let ndvi = (samples.B08 - samples.B04) / (samples.B08 + samples.B04);
  // let val = isNaN(ndvi) ? -1 : ndvi;
  // let rgba = visualizer.process(val);
  // let result = [val, samples.dataMask];
  let result = [samples.B04, samples.B08];
  return result;
}
