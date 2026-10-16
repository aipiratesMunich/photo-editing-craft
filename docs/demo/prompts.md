# Image prompts

Prompts used for the README artwork and the demo photos. Generated images are AI-made and
labelled as such in the README.

## A. Pixel artwork (style of the retro asset kit)

Model: Higgsfield Nano Banana Pro (or Seedream 4). Generate text in the image never; titles are
added afterwards so they stay sharp and correct.

Style block, append to every prompt:

```
16-bit pixel art, hard-edged square pixels, no anti-aliasing, no blur, no gradients,
flat shading with 2 to 3 tones per color, crisp 1-pixel dark outlines,
limited palette: deep navy background #070b17 and #0d1630, neon cyan #5ac9ff,
magenta #f44594, violet #985bf4, green #25cc85, amber #ffc43b, orange #ff8b47,
skin tones #efb58c and #bb805e, late-1990s computer aesthetic, no text, no letters,
no logos, no watermark
```

### A1. Social preview / hero (16:9, export 1280 x 640 crop)
```
Wide pixel art scene: a retro desk at night with a chunky CRT monitor, the screen shows
a landscape photo split down the middle by a glowing cyan vertical line, left half dull and
orange-tinted, right half clean and vivid. A small pixel character with dark hair and a
green sweater sits at the keyboard holding a drawing stylus. Floating around the monitor:
pixel icons of crop brackets, a stack of layers, a pen nib, a letter-T shape made of blocks,
a sparkle. The left third of the image is empty dark navy space for a title.
```

### A2. README banner (4:1, export 1600 x 400)
```
Long horizontal pixel art banner: a row of five small CRT monitors on a dark navy shelf,
each screen showing a different before-and-after split image: a coffee mug, misty hills,
an orange sneaker, a beach, a portrait. Thin cyan scanlines, tiny blinking amber power LEDs,
a pixel mouse cursor hovering over the middle screen. Empty dark space on the far left.
```

### A3. Mascot (1:1)
```
Pixel art character, full body, centered: a friendly small robot retoucher with a boxy
navy head, a cyan visor screen showing two pixel eyes, a magenta scarf, holding an oversized
pixel stylus in one hand and a tiny photo frame in the other. Plain dark navy background,
lots of empty space around the figure.
```

### A4. Recipe icon sheet (4:3, 4 x 3 grid)
```
Pixel art icon sprite sheet, 12 icons in a 4 by 3 grid, each icon in its own dark navy
square tile with a thin cyan border, consistent size and line weight:
1 a water drop half orange half neutral gray, 2 an S-shaped curve on a small graph,
3 a bandage over a dot, 4 dashed scissors cutting around a shape, 5 a shape in front of a
swapped background square, 6 a bold block letter T with a drop shadow, 7 a phone in portrait
format with a photo, 8 a monitor with a down arrow, 9 a printer with four colored dots
cyan magenta yellow black, 10 a faint translucent stamp in a corner, 11 a black and white
split circle, 12 a frame with darkened corners.
```

### A5. Loop for a GIF (image to video, 3 s)
Start image: A1. Then:
```
The glowing cyan line on the CRT screen sweeps slowly from left to right and back, revealing
the vivid side of the photo, the pixel character taps the stylus once, the amber LED blinks.
Camera static, pixel art preserved, seamless loop.
```

## B. Demo photos for the before/after GIFs

These are inputs. The recipes really run on them, so the GIFs show actual results.
Model: Seedream 4 or Higgsfield Soul, photo-real. Save under `docs/demo/inputs/` with the
file names given.

| File | Size | Prompt |
|---|---|---|
| mug.jpg | 3:2 | Product photo of a plain white ceramic coffee mug on a light oak table next to a white folded napkin, shot indoors under warm tungsten bulbs, strong orange yellow color cast over the whole image, slightly dim, realistic smartphone photo, no text |
| hazy.jpg | 3:2 | Wide landscape photo of rolling green hills and a lake with mountains behind, heavy haze and fog, very low contrast, washed out milky colors, flat light, realistic camera photo, no text |
| sneaker.jpg | 3:2 | Studio product photo of a single bright orange running sneaker, side view, centered, on a plain light gray seamless paper background, soft even lighting, crisp edges, e-commerce catalog style, no text, no logo |
| beach.jpg | 3:2 | Bright summer beach scene, turquoise sea, sand, a few palm trees on the left, clear blue sky with empty space in the upper half for a headline, realistic travel photo, no people, no text |
| portrait.jpg | 4:5 | Natural outdoor portrait photo of a smiling middle-aged man with short gray hair, soft daylight, green park background blurred, realistic, documentary style, no text |
