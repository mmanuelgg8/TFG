//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 1 }
  };
}

function evaluatePixel(samples) {
  // let result = [samples.B04, samples.B08];
  // return result;
  let val = index(samples.B08, samples.B04);
  // if (samples.dataMask == 0) {
  //   return [0];
  // }
  // if (val < 0.1) {
  //   return [-1];
  // }
  // if (val < 0.4) {
  //   return [0.4];
  // }
  return [val];
}
