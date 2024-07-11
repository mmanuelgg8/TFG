//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 1 }
  };
}

function evaluatePixel(samples) {
  let val = index(samples.B08, samples.B04);
  return [val];
}
