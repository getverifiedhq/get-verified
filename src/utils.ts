import sharp from 'sharp';

export function intersection(
  box1: [number, number, number, number, string, number],
  box2: [number, number, number, number, string, number],
): number {
  const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
  const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;

  const x1 = Math.max(box1_x1, box2_x1);
  const y1 = Math.max(box1_y1, box2_y1);
  const x2 = Math.min(box1_x2, box2_x2);
  const y2 = Math.min(box1_y2, box2_y2);

  return (x2 - x1) * (y2 - y1);
}

export function iou(
  box1: [number, number, number, number, string, number],
  box2: [number, number, number, number, string, number],
): number {
  return intersection(box1, box2) / union(box1, box2);
}

export function union(
  box1: [number, number, number, number, string, number],
  box2: [number, number, number, number, string, number],
): number {
  const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
  const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;

  const box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1);
  const box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1);

  return box1_area + box2_area - intersection(box1, box2);
}

export async function preprocess(buffer: Buffer): Promise<{
  input: any;
  height: number;
  width: number;
}> {
  const image = sharp(buffer);

  const metadata = await image.metadata();

  if (!metadata.height || !metadata.width) {
    throw new Error();
  }

  const bufferPixels: Buffer = await image
    .removeAlpha()
    .resize({ width: 640, height: 640, fit: 'fill' })
    .raw()
    .toBuffer();

  const red: Array<number> = [];
  const green: Array<number> = [];
  const blue: Array<number> = [];

  for (let index = 0; index < bufferPixels.length; index += 3) {
    red.push(bufferPixels[index] / 255.0);
    green.push(bufferPixels[index + 1] / 255.0);
    blue.push(bufferPixels[index + 2] / 255.0);
  }

  return {
    height: metadata.height,
    input: [...red, ...green, ...blue],
    width: metadata.width,
  };
}

export function postprocess(output: any, width: number, height: number) {
  let boxes: any = [];

  for (let index = 0; index < 8400; index++) {
    const [class_id, prob] = [...Array(80).keys()]
      .map((col) => [col, output[8400 * (col + 4) + index]])
      .reduce((accum, item) => (item[1] > accum[1] ? item : accum), [0, 0]);

    if (prob < 0.5) {
      continue;
    }
    const label = [
      'identity_card',
      'image',
      'id_design',
      'flag',
      'braille',
      'signature',
    ][class_id];

    const xc = output[index];
    const yc = output[8400 + index];
    const w = output[2 * 8400 + index];
    const h = output[3 * 8400 + index];

    const x1 = ((xc - w / 2) / 640) * width;
    const y1 = ((yc - h / 2) / 640) * height;
    const x2 = ((xc + w / 2) / 640) * width;
    const y2 = ((yc + h / 2) / 640) * height;

    boxes.push([x1, y1, x2, y2, label, prob]);
  }

  boxes = boxes.sort((box1: any, box2: any) => box2[5] - box1[5]);

  const result = [];

  while (boxes.length > 0) {
    result.push(boxes[0]);
    boxes = boxes.filter((box: any) => iou(boxes[0], box) < 0.7);
  }

  return result;
}
