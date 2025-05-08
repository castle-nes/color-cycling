# Color Cycling GIF Generator

This Python script creates animated GIFs by cycling specified colors within a PNG image. You provide a base PNG image and one or more lists of hex colors. The script will then find pixels in the image matching any of the colors you specified and animate them by cycling through their respective color lists, frame by frame.

## Features

*   Takes a PNG image as input.
*   Allows defining multiple independent color cycling groups.
*   Interactive prompts for entering color lists.
*   Supports hex color codes in `#RRGGBB` or `RRGGBB` format.
*   Customizable frame duration for the GIF.
*   Customizable loop count for the GIF (including infinite loop).
*   Outputs an animated GIF.
*   Handles images with different PNG modes by converting them to RGB.
*   Includes progress bar for frame generation.

## Installation

1.  **Prerequisites:**
    *   Python 3.7+
    *   `pip` (Python package installer)

2.  **Clone or Download:**
    Get the `color_cycling.py` script. If it's part of a repository, you can clone it:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    Otherwise, just download `color_cycling.py` into a directory.

3.  **Set up a Virtual Environment (Recommended):**
    It's good practice to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    ```
    Activate the environment:
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install Dependencies:**
    The script requires the `Pillow` library for image manipulation and `tqdm` for progress bars.
    ```bash
    pip install Pillow tqdm
    ```

## Usage

Run the script from your terminal:

```bash
python color_cycling.py <filepath> [options]
```

**Arguments:**

*   `filepath`: (Required) Path to the input PNG file.

**Options:**

*   `-o, --output <output_path>`: Path for the output GIF file.
    (Default: `input_filename_animated.gif`)
*   `-d, --duration <milliseconds>`: Frame duration in milliseconds.
    (Default: `100`)
*   `-l, --loop <count>`: Number of loops for the GIF (0 for infinite loop).
    (Default: `0`)

**Interactive Color Input:**

After running the script with the image path, you will be prompted to enter color lists:

```
Processing image: your_image.png
Enter comma-separated hex colors for cycle group 1 (e.g., #FF0000,#00FF00,#0000FF).
Press Enter with no input to finish:
```

*   Enter colors for each cycling group, separated by commas. Hex codes can be `#RRGGBB` or `RRGGBB`.
*   Each group must contain at least two colors.
*   After entering colors for one group, press Enter. You'll be prompted for the next group.
*   To finish entering color groups, press Enter on an empty line. You must provide at least one group.

**How it works:**
The script identifies all pixels in the input image that match *any* of the colors you provide in your lists.
When generating frames:
1.  If a pixel in the original image matches a color from one of your lists, it will be replaced.
2.  The replacement color is determined by "shifting" through the list that the original color belongs to. For example, if a color `C1` is part of list `[C1, C2, C3]`, in frame 0 it's `C1`, in frame 1 it's `C2`, frame 2 is `C3`, frame 3 is `C1` again, and so on.
3.  If a color is accidentally defined in multiple lists, it will cycle according to the *first* list it was defined in. A warning will be printed.

The total number of frames in the GIF will be the Least Common Multiple (LCM) of the lengths of all your color lists, ensuring all cycles complete smoothly.

## Examples

### Example 1: Single Color Cycle

Let's say you have an image `logo.png` and you want to cycle a specific red color (`#FF0000`) through green (`#00FF00`) and then blue (`#0000FF`).

1.  **Command:**
    ```bash
    python color_cycling.py logo.png -d 150 -o logo_animated.gif
    ```

2.  **Interactive Input:**
    ```
    Processing image: logo.png
    Enter comma-separated hex colors for cycle group 1 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: #FF0000,#00FF00,#0000FF
    Enter comma-separated hex colors for cycle group 2 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: <PRESS ENTER>
    ```

    This will:
    *   Find all pixels in `logo.png` that are `#FF0000`, `#00FF00`, or `#0000FF`.
    *   If a pixel is `#FF0000`, it will cycle: `#FF0000` -> `#00FF00` -> `#0000FF` -> `#FF0000`...
    *   If a pixel is `#00FF00`, it will cycle: `#00FF00` -> `#0000FF` -> `#FF0000` -> `#00FF00`... (and so on for `#0000FF`)
    *   The resulting `logo_animated.gif` will have 3 frames (LCM of 3 is 3), each lasting 150ms, and loop infinitely.

### Example 2: Multiple Independent Color Cycles

Suppose `artwork.png` has some elements in shades of purple you want to cycle, and other elements in shades of orange.

1.  **Command:**
    ```bash
    python color_cycling.py artwork.png -d 100 -l 5
    ```

2.  **Interactive Input:**
    ```
    Processing image: artwork.png
    Enter comma-separated hex colors for cycle group 1 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: #550055, #880088, #AA00AA, #880088
    Enter comma-separated hex colors for cycle group 2 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: FF8C00, FFA500, FFD700
    Enter comma-separated hex colors for cycle group 3 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: <PRESS ENTER>
    ```

    This will:
    *   **Group 1 (Purples):** Pixels matching `#550055`, `#880088`, or `#AA00AA` will cycle through the 4-color purple list (e.g., `#550055` -> `#880088` -> `#AA00AA` -> `#880088` -> `#550055`...).
    *   **Group 2 (Oranges):** Pixels matching `FF8C00` (dark orange), `FFA500` (orange), or `FFD700` (gold) will cycle through the 3-color orange list.
    *   The generated `artwork_animated.gif` will have LCM(4, 3) = 12 frames.
    *   Each frame will last 100ms, and the GIF will loop 5 times.

### Example 3: Short cycle for a specific effect

Imagine you have `icon.png` with a border color `#CCCCCC` and you want it to briefly flash to `#FFFFFF` and back.

1.  **Command:**
    ```bash
    python color_cycling.py icon.png -d 50
    ```

2.  **Interactive Input:**
    ```
    Processing image: icon.png
    Enter comma-separated hex colors for cycle group 1 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: #CCCCCC, #FFFFFF
    Enter comma-separated hex colors for cycle group 2 (e.g., #FF0000,#00FF00,#0000FF).
    Press Enter with no input to finish: <PRESS ENTER>
    ```
    This will make any `#CCCCCC` pixels in `icon.png` alternate between `#CCCCCC` and `#FFFFFF`. Any existing `#FFFFFF` pixels (that were part of this specified cycle list) would alternate to `#CCCCCC` and back. The GIF will have 2 frames, each 50ms.

## Notes

*   The script converts the input image to 'RGB' mode. This means transparency information (alpha channel) from the original PNG might be lost or flattened against a black background if not handled by Pillow's default conversion.
*   For very large images or a very high number of frames (due to long color lists or many lists with lengths that are prime to each other), the script might consume a significant amount of memory.
