from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

import os

import librosa
import numpy as np
import soundfile as sf
import torch
from tqdm import tqdm

from lib import dataset
from lib import nets
from lib import spec_utils
from lib import utils


config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="clean-audio", log_extension=extension)

_BASE_FOLDER = "tmp/audio-clean/"
_GPU = -1
_MODEL = 'models/baseline.pth'
_SR = 44100
_N_FFT = 2048
_HOP_LENGTH = 1024
_BATCH = 4
_CROP = 256
_TTA = False

log.info("Loading Machine Learning Model")
device = torch.device('cpu')
model = nets.CascadedNet(_N_FFT)
model.load_state_dict(torch.load(_MODEL, map_location=device))
if torch.cuda.is_available() and _GPU >= 0:
    device = torch.device('cuda:{}'.format(_GPU))
    model.to(device)
else:
    log.warning("No available GPU detected")
log.done("Model Loaded succesfuly.")

class Separator(object):

    def __init__(self, model, device, batchsize, cropsize, postprocess=False):
        self.model = model
        self.offset = model.offset
        self.device = device
        self.batchsize = batchsize
        self.cropsize = cropsize
        self.postprocess = postprocess

    def _separate(self, X_mag_pad, roi_size):
        X_dataset = []
        patches = (X_mag_pad.shape[2] - 2 * self.offset) // roi_size
        for i in range(patches):
            start = i * roi_size
            X_mag_crop = X_mag_pad[:, :, start:start + self.cropsize]
            X_dataset.append(X_mag_crop)

        X_dataset = np.asarray(X_dataset)

        self.model.eval()
        with torch.no_grad():
            mask = []
            # To reduce the overhead, dataloader is not used.
            for i in tqdm(range(0, patches, self.batchsize)):
                X_batch = X_dataset[i: i + self.batchsize]
                X_batch = torch.from_numpy(X_batch).to(self.device)

                pred = self.model.predict_mask(X_batch)

                pred = pred.detach().cpu().numpy()
                pred = np.concatenate(pred, axis=2)
                mask.append(pred)

            mask = np.concatenate(mask, axis=2)

        return mask

    def _preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def _postprocess(self, mask, X_mag, X_phase):
        if self.postprocess:
            mask = spec_utils.merge_artifacts(mask)

        y_spec = mask * X_mag * np.exp(1.j * X_phase)
        v_spec = (1 - mask) * X_mag * np.exp(1.j * X_phase)

        return y_spec, v_spec

    def separate(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = dataset.make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)
        mask = mask[:, :, :n_frame]

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec

    def separate_tta(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = dataset.make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)

        pad_l += roi_size // 2
        pad_r += roi_size // 2
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask_tta = self._separate(X_mag_pad, roi_size)
        mask_tta = mask_tta[:, :, roi_size // 2:]
        mask = (mask[:, :, :n_frame] + mask_tta[:, :, :n_frame]) * 0.5

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec

def clean_audio_extract(_input,_output):
    log.info('loading wave source...')
    X, sr = librosa.load(
        _input, _SR, False, dtype=np.float32, res_type='kaiser_fast')
    #basename = os.path.splitext(os.path.basename(_input))[0]
    log.done('Wawe loaded succesfuly')

    if X.ndim == 1:
        # mono to stereo
        X = np.asarray([X, X])

    log.info('stft of wave source...')
    X_spec = spec_utils.wave_to_spectrogram(X, _HOP_LENGTH, _N_FFT)
    log.done("Complete")

    sp = Separator(model, device, _BATCH, _CROP, False)

    if _TTA:
        y_spec, v_spec = sp.separate_tta(X_spec)
    else:
        y_spec, v_spec = sp.separate(X_spec)

    log.info('inverse stft of instruments...')
    wave = spec_utils.spectrogram_to_wave(y_spec, hop_length=_HOP_LENGTH)
    log.done("Complete")
    log.info("Writting in file")
    sf.write(_output, wave.T, sr)
    log.done("Completed")

def clean_all_audio(hash,nb_clip):
    """
        Clean all audio
    """
    output_path = _BASE_FOLDER+str(hash)
    input_path = "tmp/audio-clip/"+str(hash)
    log.info("Creation of folder : %s" % output_path)
    os.mkdir(output_path)
    log.done("Folder creation completed")
    for clip_id in range(1,nb_clip):
        input_file = f'{input_path}/audio_clip_{clip_id}.wav'
        output_file = f'{output_path}/clean_audio_{clip_id}.wav'
        try:
            clean_audio_extract(input_file,output_file)
        except Exception as e:
            pass
        os.remove(input_file)
