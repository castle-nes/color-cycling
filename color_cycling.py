import argparse
import os
import sys
import re
import math
from PIL import Image
from tqdm import tqdm

# --- Helper Functions ---

def hex_to_rgb(hex_color):
    """Converts a hex color string (#RRGGBB or RRGGBB) to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color format: '{hex_color}'")
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"Invalid characters in hex color: '{hex_color}'")

def validate_hex_color(color_str):
    """Checks if a string is a valid hex color format."""
    return re.match(r'^#?([a-fA-F0-9]{6})$', color_str.strip())

def calculate_lcm(a, b):
    """Calculates the Least Common Multiple (LCM) of two integers."""
    return abs(a * b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def get_color_lists_from_user():
    """Prompts the user to enter one or more lists of hex colors."""
    color_lists_hex = []
    list_num = 1
    while True:
        prompt = (f"Enter comma-separated hex colors for cycle group {list_num} "
                  f"(e.g., #FF0000,#00FF00,#0000FF).\n"
                  f"Press Enter with no input to finish: ")
        try:
            user_input = input(prompt).strip()
            if not user_input:
                if not color_lists_hex:
                    print("Error: At least one color list must be provided.", file=sys.stderr)
                    continue # Ask again for the first list
                else:
                    break # Finished entering lists

            colors_hex = [c.strip() for c in user_input.split(',') if c.strip()]

            # Validate hex format
            invalid_colors = [c for c in colors_hex if not validate_hex_color(c)]
            if invalid_colors:
                print(f"Error: Invalid hex color format found: {', '.join(invalid_colors)}", file=sys.stderr)
                print("Please use #RRGGBB or RRGGBB format.")
                continue # Ask for the current list again

            # Validate minimum number of colors
            if len(colors_hex) < 2:
                print("Error: Each color list must contain at least 2 colors.", file=sys.stderr)
                continue # Ask for the current list again

            color_lists_hex.append(colors_hex)
            list_num += 1

        except EOFError: # Handle Ctrl+D or unexpected end of input
             print("\nInput cancelled.", file=sys.stderr)
             if not color_lists_hex:
                 sys.exit(1) # Exit if no lists were successfully entered
             else:
                 break # Proceed with the lists entered so far

    return color_lists_hex

# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(description="Create a color cycling GIF animation from a PNG image.")
    parser.add_argument("filepath", help="Path to the input PNG file.")
    parser.add_argument("-o", "--output", help="Path for the output GIF file (default: input_filename_animated.gif)")
    parser.add_argument("-d", "--duration", type=int, default=100, help="Frame duration in milliseconds (default: 100)")
    parser.add_argument("-l", "--loop", type=int, default=0, help="Number of loops for the GIF (0 for infinite loop, default: 0)")

    args = parser.parse_args()

    # 1. Validate input filepath
    if not os.path.exists(args.filepath):
        print(f"Error: Input file not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    if not args.filepath.lower().endswith(".png"):
        print(f"Error: Input file must be a PNG file: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    # 2. Get color lists from user
    print(f"Processing image: {args.filepath}")
    color_lists_hex = get_color_lists_from_user()
    if not color_lists_hex:
         print("No valid color lists provided. Exiting.", file=sys.stderr)
         sys.exit(1)

    # 3. Convert hex colors to RGB and store targets
    color_lists_rgb = []
    all_target_colors_rgb = set()
    color_list_map = {} # Maps an original RGB color to the index of its list

    print("\n--- Target Color Groups ---")
    try:
        for i, hex_list in enumerate(color_lists_hex):
            rgb_list = [hex_to_rgb(c) for c in hex_list]
            print(f"Group {i+1}: {[f'#{r:02x}{g:02x}{b:02x}' for r, g, b in rgb_list]}")
            color_lists_rgb.append(rgb_list)
            for color_rgb in rgb_list:
                if color_rgb in all_target_colors_rgb:
                    print(f"Warning: Color {f'#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}'} "
                          f"appears in multiple lists. It will cycle according to the *first* list it appeared in.", file=sys.stderr)
                else:
                     # Only add to map if not already present from another list
                     color_list_map[color_rgb] = i
                all_target_colors_rgb.add(color_rgb)
    except ValueError as e:
        print(f"Error processing hex colors: {e}", file=sys.stderr)
        sys.exit(1)
    print("---------------------------\n")


    # 4. Load the base image
    try:
        base_image = Image.open(args.filepath)
        # Convert to RGB to handle different PNG modes (like palette, RGBA) consistently
        # We lose original alpha channel info this way, but processing becomes simpler.
        # If alpha preservation is critical, this needs adjustment.
        if base_image.mode != 'RGB':
             print(f"Converting image from mode '{base_image.mode}' to 'RGB'. Transparency might be lost.")
             base_image = base_image.convert('RGB')

    except Exception as e:
        print(f"Error opening or processing image: {e}", file=sys.stderr)
        sys.exit(1)

    width, height = base_image.size
    base_pixels = list(base_image.getdata()) # Get pixel data as a list

    # 5. Calculate total number of frames (LCM of list lengths)
    num_frames = 1
    if color_lists_rgb:
        num_frames = len(color_lists_rgb[0])
        for i in range(1, len(color_lists_rgb)):
            num_frames = calculate_lcm(num_frames, len(color_lists_rgb[i]))

    print(f"Generating {num_frames} frames...")

    # 6. Generate frames
    frames = []
    try:
        for frame_index in tqdm(range(num_frames), desc="Generating Frames", unit="frame"):
            new_pixel_data = list(base_pixels) # Start with a copy of original data

            # Determine color mapping for this frame
            # A dictionary mapping original_color -> new_color for this frame
            current_frame_map = {}
            for list_index, color_list in enumerate(color_lists_rgb):
                list_len = len(color_list)
                for i, original_color in enumerate(color_list):
                    # Only map colors belonging to *this* list based on our initial mapping
                    if color_list_map.get(original_color) == list_index:
                        new_color_index = (i + frame_index) % list_len
                        current_frame_map[original_color] = color_list[new_color_index]


            # Apply color mapping to pixels
            for i in range(len(new_pixel_data)):
                original_pixel = new_pixel_data[i]
                # Check if this pixel's color is one of the *originally* targeted colors
                if original_pixel in current_frame_map:
                     new_pixel_data[i] = current_frame_map[original_pixel]


            # Create the frame image
            frame_image = Image.new('RGB', (width, height))
            frame_image.putdata(new_pixel_data)
            frames.append(frame_image)

    except MemoryError:
         print("\nError: Ran out of memory while generating frames.", file=sys.stderr)
         print("Try with a smaller image or fewer frames/colors.", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         print(f"\nError during frame generation: {e}", file=sys.stderr)
         sys.exit(1)


    # 7. Save as GIF
    output_filename = args.output
    if not output_filename:
        base_name = os.path.splitext(os.path.basename(args.filepath))[0]
        output_filename = f"{base_name}_animated.gif"

    try:
        print(f"\nSaving GIF to {output_filename}...")
        frames[0].save(
            output_filename,
            save_all=True,
            append_images=frames[1:], # Append frames 1 to end
            duration=args.duration,   # ms per frame
            loop=args.loop,           # 0 = loop forever
            optimize=False            # Optimization can sometimes affect colors/quality
        )
        print("GIF saved successfully!")
    except Exception as e:
        print(f"Error saving GIF: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()