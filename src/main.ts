import fs from 'fs';
import sharp from 'sharp';
import * as ort from 'onnxruntime-node';
import { postprocess, preprocess } from './utils';

(async () => {
  const filename: string = 'test.png'; // REPLACE

  const buffer: Buffer = fs.readFileSync(filename);

  const { height, input, width } = await preprocess(buffer);

  const model = await ort.InferenceSession.create('custom.onnx');

  const tensor = new ort.Tensor(Float32Array.from(input), [1, 3, 640, 640]);

  const outputs = await model.run({ images: tensor });

  const result: Array<[number, number, number, number, string, number]> =
    postprocess(outputs['output0'].data, width, height);

  const image = sharp(filename);

  const metadata = await image.metadata();

  const svgOverlay = `
    <svg width="${metadata.width}" height="${metadata.height}" xmlns="http://www.w3.org/2000/svg">
      ${result
        .map(
          ([x1, y1, x2, y2, label, confidence]) => `
        <rect x="${x1}" y="${y1}" width="${x2 - x1}" height="${y2 - y1}" 
          fill="none" stroke="red" stroke-width="3" />
        <text x="${x1 + 5}" y="${y1 - 5}" fill="red" font-size="20" font-family="Arial">
          ${label} (${(confidence * 100).toFixed(2)}%)
        </text>
      `,
        )
        .join('')}
    </svg>
  `;

  await image
    .composite([
      {
        input: Buffer.from(svgOverlay),
        top: 0,
        left: 0,
      },
    ])
    .toFile('output.png');
})();
