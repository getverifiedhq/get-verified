import fs from 'fs';
import * as ort from 'onnxruntime-node';
import { postprocess, preprocess } from './utils';

(async () => {
  const buffer: Buffer = fs.readFileSync('test.png'); // REPLACE

  const { height, input, width } = await preprocess(buffer);

  const model = await ort.InferenceSession.create('custom.onnx');

  const tensor = new ort.Tensor(Float32Array.from(input), [1, 3, 640, 640]);

  const outputs = await model.run({ images: tensor });

  const result = postprocess(outputs['output0'].data, width, height);

  console.log(result);
})();
