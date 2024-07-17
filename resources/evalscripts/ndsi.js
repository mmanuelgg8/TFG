//VERSION=3
function setup() {
  return {
    input: ["B03", "B11", "dataMask"],
    output: { bands: 1 }
  };
}

function evaluatePixel(samples) {
  let val = index(samples.B03, samples.B11);

  if (samples.dataMask == 0) {
    return [0];
  }
  if (val > 0.42) return [1];
  else return [-1];
}
