//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  if (sample.dataMask == 1) {
    var ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    var ndviColor = colorMap(
      ndvi,
      [-1, 0, 1],
      [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 1]
      ]
    );
    return [ndviColor[0], ndviColor[1], ndviColor[2]];
  } else {
    return [0, 0, 0];
  }
}

function colorMap(value, inputRange, outputRange) {
  var result = [];
  for (var i = 0; i < inputRange.length; i++) {
    if (value <= inputRange[i]) {
      result = outputRange[i];
      break;
    }
  }
  return result;
}
