import cv2
import os
from PIL import Image
from tqdm import tqdm
import argparse
import glob
from rembg import remove
import ast
import time


def find_first_video():
    """
    Search the current directory for the first video file.
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    for extension in video_extensions:
        for video_file in glob.glob(f'*{extension}'):
            return video_file
    return None

def find_all_video():
    """
    Search the current directory for all video file.
    """
    vedio_list = []
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    for extension in video_extensions:
        for video_file in glob.glob(f'*{extension}'):
            vedio_list.append(video_file)
    
    if len(vedio_list) == 0:
        return None
    else:
        return vedio_list


def remove_background(image_path):
    """
    Remove the background from an image file using the rembg library.
    """
    with open(image_path, 'rb') as f:
        input_image = f.read()
    output_image = remove(input_image)
    with open(image_path, 'wb') as f:
        f.write(output_image)


def video_to_png(video_path, output_folder, save_fps, remove_bg_flag, crop):
    """
    Converts a video to a series of PNG images.
    """
    if not os.path.exists(output_folder):
        print(f"Create folder : {output_folder}.")
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            print(
                f"Unable to create folder {output_folder}, raise exception {e}")
            return -1

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    video_fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = 1 if save_fps == - \
        1 else max(int(round(video_fps / save_fps)), 1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    saved_frame_count = 0

    for frame_id in tqdm(range(total_frames), desc="Converting video"):
        ret, frame = cap.read()
        if not ret:
            break
        if crop != ((-1, -1), (-1, -1)):
            left, upper = crop[0]
            right, lower = crop[1]
            frame = frame[upper:lower, left:right]

        if frame_id % frame_interval == 0:
            frame_path = os.path.join(
                output_folder, str(time.time())+ "_" + f"frame_{saved_frame_count:04d}_.png")

            is_success, im_buf_arr = cv2.imencode(".jpg", frame)
            im_buf_arr.tofile(frame_path)

            if remove_bg_flag:
                remove_background(frame_path)

            saved_frame_count += 1

    cap.release()
    print(f"Done! Extracted {saved_frame_count} frames.")


def main():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert a video to PNG images with optional background removal.")
    parser.add_argument("-i", "--input", type=str,
                        help="Path to the input video file.")
    parser.add_argument("-o", "--output", type=str,
                        default=".\\output", help="Path to the output folder (default is a folder named output in the current folder).")
    parser.add_argument("-f", "--fps", type=int, default=-
                        1, help="Frames per second to save.")
    parser.add_argument("-r", "--remove_bg", action='store_true',
                        help="Remove background from each image after saving.", default=False)
    parser.add_argument("-c", "--crop", type=ast.literal_eval, default=((-1, -1), (-1, -1)),
                        help="Crop area as a tuple of two points: (left, upper), (right, lower).")
    parser.add_argument("-b", "--batch", type=str, help="Batch convert")
    args = parser.parse_args()

    if not args.input:
        if not args.batch:
            args.input = find_first_video()
            if args.input is None:
                print("No video file found. Please specify an input video file.")
                return
            else:
                print(f"Found video file: {args.input}")
        else:
            pass


    if not args.batch:
        video_to_png(args.input, args.output, args.fps, args.remove_bg, args.crop)
    else:
        count = 0
        vedio_list = find_all_video()
        
        for vedio_file in vedio_list:
            video_to_png(vedio_file, str(count), args.fps, args.remove_bg, args.crop)
            count = count + 1

if __name__ == "__main__":
    main()
