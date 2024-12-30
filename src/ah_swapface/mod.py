import sys
from pathlib import Path
from typing import List, Optional, Set, Union
import os
import nanoid
import cv2
import insightface
import numpy as np
import onnxruntime
import torch
from insightface.model_zoo.inswapper import INSwapper
from PIL import Image
from .utils import pil2tensor, tensor2pil
from .download import download_and_extract
from lib.providers.services import service
import traceback

swapper = None

class FaceSwap:
    def __init__(self):
        # Ensure models directory exists
        os.makedirs("models/face", exist_ok=True)
        
        self.check_for_models()
 
        self.face_analyser = insightface.app.FaceAnalysis(
            name="buffalo_l",
            root="models/face"
        )
        self.swap_model = INSwapper(
            "models/face/inswapper_128.onnx",
            onnxruntime.InferenceSession(
                path_or_bytes='models/face/inswapper_128.onnx',
                providers=onnxruntime.get_available_providers(),
            ),
        )

    def check_for_models(self):
        model_path = Path("models/face/inswapper_128.onnx")
        if not model_path.exists():
            print("Models not found, downloading them")
            self.download_models()
        else:
            print("Models found, skipping download")

    def download_models(self):
        download_and_extract("https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip", "models/face")
        download_and_extract("https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx?download=true", "models/face")

    def get_face_single(
        self,
        img_data: np.ndarray, face_index=0, det_size=(640, 640)
    ):
        self.face_analyser.prepare(ctx_id=0, det_size=det_size)
        face = self.face_analyser.get(img_data)

        if len(face) == 0 and det_size[0] > 320 and det_size[1] > 320:
            print("No face detected, trying again with smaller image")
            det_size_half = (det_size[0] // 2, det_size[1] // 2)
            return self.get_face_single(
                img_data,
                face_index=face_index,
                det_size=det_size_half,
            )

        try:
            return sorted(face, key=lambda x: x.bbox[0])[face_index]
        except IndexError:
            return None


    def swap_face(
        self,
        source_img: Union[Image.Image, List[Image.Image]],
        target_img: Union[Image.Image, List[Image.Image]],
        faces_index: Optional[Set[int]] = None,
    ) -> Image.Image:
        if faces_index is None:
            faces_index = {0}
        print(f"Swapping faces: {faces_index}")
        result_image = target_img

        if self.swap_model is not None:
            cv_source_img = cv2.cvtColor(np.array(source_img), cv2.COLOR_RGB2BGR)
            cv_target_img = cv2.cvtColor(np.array(target_img), cv2.COLOR_RGB2BGR)
            source_face = self.get_face_single(cv_source_img, face_index=0)
            if source_face is not None:
                result = cv_target_img

                for face_num in faces_index:
                    target_face = self.get_face_single(
                        cv_target_img, face_index=face_num
                    )
                    if target_face is not None:
                        result = self.swap_model.get(
                            result, target_face, source_face
                        )
                    else:
                        print(f"No target face found for {face_num}")

                result_image = Image.fromarray(
                    cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                )
            else:
                print("No source face found")
        else:
            print("No face swap model provided")
        return result_image

def setup():
    global swapper
    print("initializing face swap")
    swapper = FaceSwap()

async def do_swap_face(src_dir, target_img_filepath):
    target_img = Image.open(target_img_filepath)
    src_images = []

    print(f"looking for source face ref in {src_dir}")
    for filename in os.listdir(src_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            src_img_path = os.path.join(src_dir, filename)
            src_img = Image.open(src_img_path)
            src_images.append(src_img)
    
    if len(src_images) > 0:
        swapped_img = swapper.swap_face(src_images[0], target_img)
        
        # Ensure imgs directory exists
        os.makedirs("imgs", exist_ok=True)
        output_fname = os.path.join("imgs", nanoid.generate() + ".png")
        swapped_img.save(output_fname)
        return output_fname
    else:
        print("No source images found in the directory.")

@service()
async def swap_face(input_ref_dir, target_image_path, context=None, skip_nsfw=False, wrap_html=False): 
    """Swap faces in target image using reference faces.
    
    Args:
        input_ref_dir (str): Directory containing reference face images
        target_image_path (str): Path to target image where faces will be swapped
        context (object, optional): Service context. Defaults to None.
        skip_nsfw (bool, optional): Skip NSFW content detection. Defaults to False.
        wrap_html (bool, optional): Wrap result in HTML img tag. Defaults to False.
    
    Returns:
        str: Path to resulting image, or HTML img tag if wrap_html=True
    """
    try:
      fname = await do_swap_face(input_ref_dir, target_image_path)
      if wrap_html and fname:
          fname = f'<img src="{fname}" style="max-width: 100%; height: auto;" />'
    except Exception as e:
        trace = sys.exc_info()[2]
        print("Error in swap_face:", e)
        print(trace)
        fname = None
    return fname

setup()
