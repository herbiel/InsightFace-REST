import sys
if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated
from typing import Callable, List
from typing import Optional

import msgpack
import numpy as np
from fastapi import File, Form, Header, HTTPException, APIRouter
from fastapi import Request, Response
from fastapi.responses import UJSONResponse
from fastapi.routing import APIRoute
from starlette.responses import StreamingResponse, PlainTextResponse

from if_rest.core.processing import ProcessingDep
from if_rest.schemas import BodyDraw, BodyExtract
from if_rest.schemas import BodyCompare


class MsgPackRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "application/msgpack" in self.headers.getlist("Content-Type"):
                body = msgpack.unpackb(body)
            self._body = body
        return self._body


class MsgpackRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = MsgPackRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


router = APIRouter(route_class=MsgpackRoute)


@router.post('/extract', tags=['Detection & recognition'])
async def extract(data: BodyExtract,
                  processing: ProcessingDep,
                  accept: Optional[List[str]] = Header(None),
                  content_type: Annotated[str | None, Header()] = None):
    """
    Face extraction/embeddings endpoint accept json with
    parameters in following format:

       - **images**: dict containing either links or data lists. (*required*)
       - **threshold**: Detection threshold. Default: 0.6 (*optional*)
       - **embed_only**: Treat input images as face crops (112x112 crops required), omit detection step. Default: False (*optional*)
       - **return_face_data**: Return face crops encoded in base64. Default: False (*optional*)
       - **return_landmarks**: Return face landmarks. Default: False (*optional*)
       - **extract_embedding**: Extract face embeddings (otherwise only detect faces). Default: True (*optional*)
       - **extract_ga**: Extract gender/age. Default: False (*optional*)
       - **limit_faces**: Maximum number of faces to be processed.  0 for unlimited number. Default: 0 (*optional*)
       - **verbose_timings**: Return all timings. Default: False (*optional*)
       - **msgpack**: Serialize output to msgpack format for transfer. Default: False (*optional*)
       \f

       :return:
       List[List[dict]]
    """
    try:
        b64_decode = True
        if content_type == 'application/msgpack':
            b64_decode = False
        output = await processing.extract(data.images, return_face_data=data.return_face_data,
                                            embed_only=data.embed_only, extract_embedding=data.extract_embedding,
                                            threshold=data.threshold, extract_ga=data.extract_ga,
                                            limit_faces=data.limit_faces, min_face_size=data.min_face_size,
                                            return_landmarks=data.return_landmarks,
                                            detect_masks=data.detect_masks,
                                            verbose_timings=data.verbose_timings, b64_decode=b64_decode,
                                            img_req_headers=data.img_req_headers)

        if data.msgpack or 'application/x-msgpack' in accept:
            return PlainTextResponse(msgpack.dumps(output, use_single_float=True), media_type='application/x-msgpack')
        else:
            return UJSONResponse(output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post('/draw_detections', tags=['Detection & recognition'])
async def draw(data: BodyDraw,
               processing: ProcessingDep):
    """
    Return image with drawn faces for testing purposes.

       - **images**: dict containing either links or data lists. (*required*)
       - **threshold**: Detection threshold. Default: 0.6 (*optional*)
       - **draw_landmarks**: Draw faces landmarks Default: True (*optional*)
       - **draw_scores**: Draw detection scores Default: True (*optional*)
       - **draw_sizes**: Draw face sizes Default: True (*optional*)
       - **limit_faces**: Maximum number of faces to be processed.  0 for unlimited number. Default: 0 (*optional*)
       \f
    """
    try:
        output = await processing.draw(data.images, threshold=data.threshold,
                                       draw_landmarks=data.draw_landmarks, draw_scores=data.draw_scores,
                                       limit_faces=data.limit_faces, min_face_size=data.min_face_size,
                                       draw_sizes=data.draw_sizes,
                                       detect_masks=data.detect_masks)
        output.seek(0)
        return StreamingResponse(output, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/multipart/draw_detections', tags=['Detection & recognition'])
async def draw_upl(processing: ProcessingDep, file: bytes = File(...), threshold: float = Form(0.6),
                   draw_landmarks: bool = Form(True),
                   draw_scores: bool = Form(True), draw_sizes: bool = Form(True), limit_faces: int = Form(0),
                   use_rotation: bool = Form(False)):
    """
    Return image with drawn faces for testing purposes.

       - **file**: Image file (*required*)
       - **threshold**: Detection threshold. Default: 0.6 (*optional*)
       - **draw_landmarks**: Draw faces landmarks Default: True (*optional*)
       - **draw_scores**: Draw detection scores Default: True (*optional*)
       - **draw_sizes**: Draw face sizes Default: True (*optional*)
       - **limit_faces**: Maximum number of faces to be processed.  0 for unlimited number. Default: 0 (*optional*)
       \f
    """
    try:
        output = await processing.draw(file, threshold=threshold,
                                       draw_landmarks=draw_landmarks, draw_scores=draw_scores, draw_sizes=draw_sizes,
                                       limit_faces=limit_faces,
                                       multipart=True)
        output.seek(0)
        return StreamingResponse(output, media_type='image/jpg')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/compare', tags=['Detection & recognition'])
async def compare(data: BodyCompare,
                  processing: ProcessingDep):
    """
    Compare two images and return similarity score between the top face in each image.

    Body example:
    {
      "images": {"urls": ["/path/or/url/to/image1.jpg", "/path/or/url/to/image2.jpg"]},
      "threshold": 0.6,
      "face_index": 0
    }

    Returns JSON: {"score": float, "metric": "cosine"}
    """
    try:
        imgs = data.images

        # determine number of provided images (either urls or data)
        n_imgs = 0
        if getattr(imgs, 'urls', None):
            n_imgs = len(imgs.urls)
        elif getattr(imgs, 'data', None):
            n_imgs = len(imgs.data)

        if n_imgs != 2:
            raise HTTPException(status_code=400, detail='Please provide exactly two images (in urls or data)')

        # Use processing.extract to fetch images and compute embeddings (limit faces sufficiently high so face_index is valid)
        # We set limit_faces to 0 (no limit) so we can pick face_index later
        out = await processing.extract(imgs, threshold=data.threshold, limit_faces=0,
                                       extract_embedding=True, extract_ga=False,
                                       return_face_data=False)

        if not out or 'data' not in out or len(out['data']) < 2:
            raise HTTPException(status_code=400, detail='Failed to process provided images')

        fi = int(getattr(data, 'face_index', 0) or 0)

        def _get_vec_from_entry(entry, idx):
            faces = entry.get('faces') or []
            if len(faces) == 0:
                return None
            if idx < 0 or idx >= len(faces):
                return None
            f = faces[idx]
            v = f.get('vec')
            if v is None:
                return None
            return np.asarray(v, dtype=np.float32)

        v1 = _get_vec_from_entry(out['data'][0], fi)
        v2 = _get_vec_from_entry(out['data'][1], fi)

        if v1 is None or v2 is None:
            raise HTTPException(status_code=400, detail='Failed to extract face embedding at requested face_index from one or both images')

        metric = getattr(data, 'metric', 'cosine_norm') or 'cosine_norm'

        if metric in ('cosine_norm', 'cosine_raw'):
            denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
            if denom == 0:
                raise HTTPException(status_code=500, detail='Zero-length embedding encountered')
            cos_raw = float(np.dot(v1, v2) / denom)
            cos_norm = float((cos_raw + 1.0) / 2.0)
            if metric == 'cosine_raw':
                return UJSONResponse({'score': cos_raw, 'metric': 'cosine_raw'})
            else:
                return UJSONResponse({'score': cos_norm, 'metric': 'cosine_norm', 'cosine': cos_raw})

        elif metric in ('euclidean', 'euclidean_sim'):
            dist = float(np.linalg.norm(v1 - v2))
            # map distance -> similarity in 0..1: sim = 1/(1+dist)
            sim = float(1.0 / (1.0 + dist))
            return UJSONResponse({'score': sim, 'metric': 'euclidean', 'distance': dist})

        else:
            raise HTTPException(status_code=400, detail=f'Unsupported metric: {metric}')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
