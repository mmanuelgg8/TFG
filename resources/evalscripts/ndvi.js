//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 4 }
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

/* const ramp = [
  [-0.5, 0x0c0c0c],
  [-0.2, 0xbfbfbf],
  [-0.1, 0xdbdbdb],
  [0, 0xeaeaea],
  [0.025, 0xfff9cc],
  [0.05, 0xede8b5],
  [0.075, 0xddd89b],
  [0.1, 0xccc682],
  [0.125, 0xbcb76b],
  [0.15, 0xafc160],
  [0.175, 0xa3cc59],
  [0.2, 0x91bf51],
  [0.25, 0x7fb247],
  [0.3, 0x70a33f],
  [0.35, 0x609635],
  [0.4, 0x4f892d],
  [0.45, 0x3f7c23],
  [0.5, 0x306d1c],
  [0.55, 0x216011],
  [0.6, 0x0f540a],
  [1, 0x004400]
];
 */
const visualizer = new ColorRampVisualizer(ramp);

function evaluatePixel(samples) {
  let ndvi = index(samples.B08, samples.B04);
  let imgVals = visualizer.process(ndvi);
  return imgVals.concat(samples.dataMask);
}
