export const analyzeImageQuality = (imageUrl) => {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d", {
        willReadFrequently: true,
      });

      const maxAnalysisSize = 500;

      let width = img.naturalWidth;
      let height = img.naturalHeight;

      const scale = Math.min(
        1,
        maxAnalysisSize / Math.max(width, height)
      );

      const analysisWidth = Math.max(
        1,
        Math.round(width * scale)
      );

      const analysisHeight = Math.max(
        1,
        Math.round(height * scale)
      );

      canvas.width = analysisWidth;
      canvas.height = analysisHeight;

      ctx.drawImage(
        img,
        0,
        0,
        analysisWidth,
        analysisHeight
      );

      const imageData = ctx.getImageData(
        0,
        0,
        analysisWidth,
        analysisHeight
      );

      const pixels = imageData.data;

      let brightnessTotal = 0;
      const grayValues = [];

      for (let i = 0; i < pixels.length; i += 4) {
        const r = pixels[i];
        const g = pixels[i + 1];
        const b = pixels[i + 2];

        const gray =
          0.299 * r +
          0.587 * g +
          0.114 * b;

        brightnessTotal += gray;
        grayValues.push(gray);
      }

      const brightness =
        brightnessTotal / grayValues.length;

      let edgeDifference = 0;
      let edgeCount = 0;

      for (let y = 0; y < analysisHeight - 1; y++) {
        for (let x = 0; x < analysisWidth - 1; x++) {
          const index =
            y * analysisWidth + x;

          const current =
            grayValues[index];

          const right =
            grayValues[index + 1];

          const below =
            grayValues[index + analysisWidth];

          edgeDifference +=
            Math.abs(current - right) +
            Math.abs(current - below);

          edgeCount += 2;
        }
      }

      const sharpness =
        edgeCount > 0
          ? edgeDifference / edgeCount
          : 0;

      const resolutionGood =
        width >= 640 &&
        height >= 480;

      const brightnessGood =
        brightness >= 55 &&
        brightness <= 210;

      const sharpnessGood =
        sharpness >= 8;

      const passedChecks = [
        resolutionGood,
        brightnessGood,
        sharpnessGood,
      ].filter(Boolean).length;

      const score = Math.round(
        (passedChecks / 3) * 100
      );

      resolve({
        width,
        height,

        brightness: Math.round(brightness),

        brightnessLabel:
          brightness < 55
            ? "Too Dark"
            : brightness > 210
            ? "Too Bright"
            : "Good",

        sharpness:
          Number(sharpness.toFixed(1)),

        sharpnessLabel:
          sharpnessGood
            ? "Good"
            : "Possibly Blurry",

        resolutionGood,
        brightnessGood,
        sharpnessGood,

        score,

        suitable:
          resolutionGood &&
          brightnessGood &&
          sharpnessGood,
      });
    };

    img.onerror = () => {
      reject(
        new Error("Unable to analyze image.")
      );
    };

    img.src = imageUrl;
  });
};