export function computeAverageBrightness(imageData: ImageData): number {
  const data = imageData.data;
  let brightness = 0;
  // Sample every 8th pixel to speed up processing (same as original loop)
  for (let i = 0; i < data.length; i += 4 * 8) {
    brightness += (data[i] + data[i + 1] + data[i + 2]) / 3;
  }
  return brightness / (data.length / (4 * 8));
}
