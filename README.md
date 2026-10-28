# CGI to Real Flux txt2img + Wan 2.2, Version 3

This graph writes a 480×832 still with FLUX.2 Klein 9B, pauses, then animates that still with Wan 2.2 for about 10 seconds.

Load `CGI to Real Flux txt2img Original with Ollama and Wan 2.2 Version 3.json` from disk. A save from an older open tab can put the old graph back.

## Install

1. Use ComfyUI with frontend 1.47 or newer. This graph was saved with frontend 1.47.10. The core nodes listed below ship with that ComfyUI.
2. Copy `custom_nodes/cgi-to-real-look-presets` from this repo into `ComfyUI/custom_nodes/`. Restart ComfyUI. That folder is the Lighting, Camera, and Color dropdowns and their thumbnail previews.
3. Install these packs, then restart ComfyUI:
   - [comfyui-ollama](https://github.com/stavsap/comfyui-ollama). Also install the `ollama` Python package.
   - [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF). Also install `gguf`, `sentencepiece`, and `protobuf`.
   - [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui).
   - [ComfyUI-pause](https://github.com/wywywywy/ComfyUI-pause).
4. Run the Ollama app so `http://127.0.0.1:11434` answers. The Ollama Connectivity node asks for `uncensored-text/qwen3-abliterated:14b`. Pull that tag, or point the node at a model you already have. Temperature 0.7 and num_predict 512 are switched on. Both chat nodes share that connection and those options.
5. Put the files below where ComfyUI can see them. The loader widgets use these exact names.

## Model files

`models/diffusion_models` (GGUF files may also be read from `models/unet`):

- `flux-2-klein-9b-fp8.safetensors`
- `Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf`
- `Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf`

`models/text_encoders`:

- `qwen_3_8b_fp8mixed.safetensors`
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`

`models/vae`:

- `full_encoder_small_decoder.safetensors`
- `Wan2.1_VAE.safetensors`

`models/loras`:

- `Flux/klein_snofs_v1_4.safetensors`
- `Flux/KLEIN-Unchained-V2.safetensors`
- `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`
- `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`
- `DR34ML4Y_I2V_14B_HIGH_V2.safetensors`
- `DR34ML4Y_I2V_14B_LOW_V2.safetensors`

The two Klein LoRAs sit in a `Flux` subfolder. The subgraph loader asks for `Flux\klein_snofs_v1_4.safetensors` and `Flux\KLEIN-Unchained-V2.safetensors`.

## Run

1. Edit **Core Subject & Actions** and **Scene & Background**.
2. Pick Lighting, Camera, and Color. `(none)` adds no sentence. The camera default is Full view.
3. Edit **Video action** if you want a different motion. That line is joined to the still prompt before the motion rewrite.
4. Queue the prompt. The still saves with the prefix `Flux2-Klein`. The graph then pauses. Press continue on **Pause Workflow**. Wan writes a video under `video/ComfyUI` at 10 fps, 101 frames.
5. Every person must be a clearly adult person. Both Ollama system prompts refuse a child, a teenager, or anyone under 18.

## What the graph does

Subject, scene, lighting, camera, and color are joined. Empty pieces are skipped. The first Ollama chat rewrites that into one Flux prompt of about 70 to 130 words and keeps shot size, lens millimetres, f-number, light direction, and color grade. That prompt feeds the FLUX.2 Klein subgraph.

Klein runs at 480×832. Those outer width and height values override the subgraph's internal 1024 latents. The sample is 4 steps, CFG 1, Euler, Flux2 scheduler, with two Klein LoRAs at strength 1. The still is saved, then Pause Workflow runs, then Free Memory.

The still is resized to 480×832 and becomes the Wan start image. Width, height, and batch come from that resized image. Length stays 101. A second Ollama chat writes the motion prompt. Wan is a high-noise pass and then a low-noise pass. Each pass has a lightx2v 4-step LoRA and a second LoRA, shift 5, Euler, simple, CFG 1. High noise samples steps 0 to 2 with noise on. Low noise samples steps 2 to 4 with add noise off. Both samplers are active. The word "disable" on the low-noise sampler is the add-noise switch, not a bypass. CFG 1 means the negative prompts are wired and do not steer the sample.

## Nodes

### Look and prompt

- `PrimitiveString` — Core Subject & Actions
- `PrimitiveString` — Scene & Background
- `CGILightingSetup` — Lighting Setup. Custom pack. Returns a sentence and a preview image.
- `CGICameraLens` — Camera & Lens Specifications. Custom pack.
- `CGIColorAesthetic` — Color Palette & Aesthetic Style. Custom pack.
- `PreviewImage` — Camera preview, Lighting preview, and Color preview
- `Text Concatenate` — WAS Node Suite. Joins the five strings and skips blanks.
- `PreviewAny` — Joined prompt preview. Core node. Display name is Preview as Text.
- `OllamaConnectivityV2` — URL and model. comfyui-ollama.
- `OllamaOptionsV2` — temperature 0.7 and num_predict 512. comfyui-ollama.
- `OllamaChat` — still-prompt writer. comfyui-ollama.
- `PreviewAny` — rewritten still prompt
- `StringConcatenate` — Video action. Core node.
- `OllamaChat` — motion-prompt writer. comfyui-ollama.
- `PreviewAny` — rewritten motion prompt

### Still

The outer node is the subgraph **Text to Image (FLUX.2 Klein 9B)**. Inside it:

- `UNETLoader` — `flux-2-klein-9b-fp8.safetensors`, passed in from the outer node
- `LoadLoraModel` — the two Klein LoRAs. Core node. Display name is Load LoRA (Model).
- `CLIPLoader` — `qwen_3_8b_fp8mixed.safetensors`, type `flux2`
- `VAELoader` — `full_encoder_small_decoder.safetensors`
- `CLIPTextEncode` — positive prompt, fed by the still Ollama node
- `CLIPTextEncode` — negative prompt
- `PrimitiveInt` — width and height, driven by the outer 480 and 832
- `EmptyFlux2LatentImage`
- `RandomNoise`
- `KSamplerSelect` — euler
- `Flux2Scheduler` — 4 steps
- `CFGGuider` — CFG 1
- `SamplerCustomAdvanced`
- `VAEDecode`

After the subgraph:

- `SaveImage` — prefix `Flux2-Klein`

### Between the stages

- `PauseWorkflowNode` — ComfyUI-pause. Waits until you press continue.
- `WASFreeMemory` — WAS Node Suite. Runs after the pause.
- `ResizeImageMaskNode` — core. Scales the still to 480×832.
- `GetImageSize` — core. Passes width, height, and batch into Wan.

### Video

- `UnetLoaderGGUF` — Wan 2.2 I2V high noise. ComfyUI-GGUF.
- `LoadLoraModel` — lightx2v high-noise LoRA and the second high-noise LoRA
- `ModelSamplingSD3` — shift 5 on the high-noise model
- `UnetLoaderGGUF` — Wan 2.2 I2V low noise
- `LoadLoraModel` — lightx2v low-noise LoRA and the second low-noise LoRA
- `ModelSamplingSD3` — shift 5 on the low-noise model
- `CLIPLoader` — `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type `wan`
- `CLIPTextEncode` — positive prompt, fed by the motion Ollama node
- `CLIPTextEncode` — negative prompt
- `VAELoader` — `Wan2.1_VAE.safetensors`
- `WanImageToVideo` — start image, length 101
- `KSamplerAdvanced` — high noise, steps 0 to 2, add noise on
- `KSamplerAdvanced` — low noise, steps 2 to 4, add noise off
- `VAEDecode`
- `CreateVideo` — 10 fps
- `SaveVideo` — folder `video/ComfyUI`
