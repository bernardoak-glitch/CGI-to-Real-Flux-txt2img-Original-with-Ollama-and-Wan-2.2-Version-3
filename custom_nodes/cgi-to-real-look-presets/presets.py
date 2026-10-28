"""Short menu labels mapped to one photography sentence each.

The sentence is what gets concatenated into the Flux prompt. The label is
only what the dropdown shows. An empty string means the choice adds nothing.
"""

CAMERA = {
    "Full view": (
        "the subject shown from head to toe on a 35mm lens at f/4, with the whole body "
        "and a little of the setting in frame and focus held across the figure"
    ),
    "Extreme close-up, 100mm": (
        "an extreme close-up on a 100mm macro lens, the frame filled by eyes, skin, or a small detail "
        "with a very thin plane of focus"
    ),
    "Beauty close-up, 100mm f/2": (
        "a beauty close-up on a 100mm lens at f/2, the face large in frame, skin detail sharp, "
        "and the background reduced to a smooth tone"
    ),
    "Close-up, 85mm f/1.4": (
        "a tight facial close-up on an 85mm lens at f/1.4, the eyes critically sharp "
        "and the background fully separated"
    ),
    "Head and shoulders, 85mm f/1.8": (
        "a head-and-shoulders portrait on an 85mm lens at f/1.8, flattering compression, "
        "eyes sharp, and the background softly melted"
    ),
    "Medium close-up, 50mm f/1.8": (
        "a medium close-up on a 50mm lens at f/1.8, framed from the chest up "
        "with natural perspective and a gentle falloff behind the subject"
    ),
    "Medium shot, 50mm f/2.8": (
        "a medium shot on a 50mm lens at f/2.8, framed from the waist up, "
        "with the subject and the immediate surroundings both readable"
    ),
    "Cowboy shot, 35mm": (
        "a cowboy shot on a 35mm lens, framed from mid-thigh up, "
        "with room for posture and a sense of the ground"
    ),
    "Full body, 35mm f/4": (
        "a full-body frame on a 35mm lens at f/4, the entire figure sharp from head to feet "
        "with a modest amount of environment around it"
    ),
    "Wide environmental, 24mm f/8": (
        "a wide environmental view on a 24mm lens at f/8, the subject small enough "
        "that the place around them carries the frame, in deep focus"
    ),
    "Ultra wide, 16mm": (
        "an ultra-wide 16mm view from close range, strong perspective, "
        "and the subject large against a stretched background"
    ),
    "Establishing wide, 18mm": (
        "an establishing wide shot on an 18mm lens, the location introduced first "
        "and the subject placed clearly inside it"
    ),
    "Low angle, 24mm": (
        "a low camera on a 24mm lens, looking up so the subject towers, "
        "with a dramatic horizon and lengthened stance"
    ),
    "High angle, 35mm": (
        "a high angle on a 35mm lens, looking down on the subject "
        "with the ground visible around them"
    ),
    "Overhead, 35mm": (
        "a true overhead view on a 35mm lens, the camera straight down "
        "and the subject laid out in a graphic top-down composition"
    ),
    "Worm's-eye, 20mm": (
        "a worm's-eye view on a 20mm lens, the camera on the ground "
        "looking up past the subject into the space above"
    ),
    "Dutch angle, 35mm": (
        "a Dutch angle on a 35mm lens, the horizon tilted, "
        "the frame uneasy, and the subject kept as the clear focus"
    ),
    "Over the shoulder, 50mm": (
        "an over-the-shoulder shot on a 50mm lens, the near shoulder soft in the foreground "
        "and the subject sharp beyond it"
    ),
    "Point of view, 24mm": (
        "a point-of-view shot on a 24mm lens, seen as if through someone's eyes, "
        "with the near space leading into the scene"
    ),
    "Profile, 85mm f/2": (
        "a clean profile on an 85mm lens at f/2, the face in exact side view "
        "against a simple separated background"
    ),
    "Three-quarter view, 50mm": (
        "a three-quarter view on a 50mm lens, the face turned partway from camera "
        "so both eyes and the cheek plane read clearly"
    ),
    "Two-shot, 35mm": (
        "a two-shot on a 35mm lens, both people framed from the waist up "
        "with enough air between them to read how they stand together"
    ),
    "Anamorphic widescreen, 40mm": (
        "an anamorphic 40mm widescreen frame, oval highlights, a horizontal flare, "
        "and a wide cinematic field with the subject placed in it"
    ),
    "Telephoto compression, 135mm f/2": (
        "a compressed telephoto view on a 135mm lens at f/2, the subject isolated "
        "and the background stacked close behind them"
    ),
    "Tilt-shift": (
        "a tilt-shift look, the plane of focus tipped so only a narrow band is sharp "
        "and the rest of the frame falls into a miniature blur"
    ),
    "Shallow depth of field, 85mm f/1.2": (
        "very shallow depth of field on an 85mm lens at f/1.2, one plane of the subject sharp "
        "and everything else a smooth wash"
    ),
    "Deep focus, 35mm f/11": (
        "deep focus on a 35mm lens at f/11, the subject and the background both sharp "
        "from the near detail to the far wall"
    ),
    "Handheld documentary, 28mm": (
        "a handheld documentary frame on a 28mm lens, close to the action, "
        "a slightly imperfect horizon, and the feeling of available light"
    ),
    "Locked-off tripod, 50mm": (
        "a locked-off tripod shot on a 50mm lens, a level horizon, "
        "and a still composition with nothing drifting in the frame"
    ),
    "Aerial, 24mm": (
        "an aerial view on a 24mm lens from well above, the subject small in a wide landscape "
        "with a clear sense of height"
    ),
    "Fisheye, 8mm": (
        "an 8mm fisheye view, strong barrel distortion, a huge field of view, "
        "and the subject held toward the center of the bulge"
    ),
    "Medium format, 80mm f/2.8": (
        "a medium-format look on an 80mm lens at f/2.8, smooth tonal roll-off, fine detail, "
        "and a slightly larger-than-life presence"
    ),
    "Vintage lens, 58mm f/2": (
        "a vintage 58mm lens at f/2, a gentle glow in the highlights, softer corners, "
        "and a little optical character"
    ),
    "Side tracking, 35mm": (
        "a side-on tracking view on a 35mm lens, the subject in profile crossing the frame "
        "with the background sliding past"
    ),
    "Insert detail, 90mm macro": (
        "an insert detail on a 90mm macro lens, a hand, fabric, or small object "
        "filling the frame with crisp texture"
    ),
    "Long-lens silhouette, 200mm": (
        "a distant 200mm view, the subject compressed and readable as a clean silhouette "
        "against the background"
    ),
}

LIGHTING = {
    "(none)": "",
    "Soft window light": (
        "soft daylight from a large window to camera-left, a gentle wrap on the face, "
        "and no hard shadow edge"
    ),
    "Golden hour": (
        "low golden-hour sun from the side, long soft shadows, "
        "and a warm rim along the subject"
    ),
    "Blue hour": (
        "blue-hour ambient light, the cool open sky as the key, "
        "and a faint warm practical somewhere in the background"
    ),
    "Overcast sky": (
        "even light from an overcast sky, soft shadows, neutral color, "
        "and detail held in both the highlights and the shade"
    ),
    "Hard noon sun": (
        "hard overhead noon sun, short dark shadows under the brow and chin, "
        "high contrast, and bright speculars"
    ),
    "Rembrandt": (
        "Rembrandt lighting, a key from about 45 degrees "
        "leaving a small triangle of light on the shadow cheek"
    ),
    "Butterfly lighting": (
        "butterfly lighting, a soft key above the camera, a small shadow under the nose, "
        "and even light across the face"
    ),
    "Split lighting": (
        "split lighting, one half of the face fully lit "
        "and the other half falling into a clean shadow"
    ),
    "Loop lighting": (
        "loop lighting, the key slightly above and to the side, "
        "with a small nose shadow that does not meet the cheek"
    ),
    "Rim light": (
        "a bright rim from behind separating the subject from the background, "
        "with the face opened by a softer fill"
    ),
    "Three-point studio": (
        "classic three-point studio light, a soft key, a lower fill, "
        "and a hair light defining the edge of the head"
    ),
    "Warm practical lamps": (
        "warm practical lamps in the room as the key, pools of tungsten light, "
        "and deeper shadow between them"
    ),
    "Neon practicals": (
        "colored neon practicals nearby, cyan and magenta spill across skin and surfaces, "
        "with darkness between the signs"
    ),
    "Candlelight": (
        "candlelight from low and to the side, a small warm source, fast falloff, "
        "and most of the room in shadow"
    ),
    "Moonlight": (
        "cool moonlight as the only source, blue-silver highlights "
        "and deep underexposed shadows"
    ),
    "Cool rain": (
        "diffuse cool light under rain, wet surfaces carrying speculars, "
        "low contrast, and a gray-blue cast"
    ),
    "God rays": (
        "strong volumetric god rays through haze, a hard sunbeam cutting the air, "
        "and the subject partly inside it"
    ),
    "High-key": (
        "high-key lighting, bright almost shadowless illumination, "
        "clean whites, and an airy background"
    ),
    "Low-key chiaroscuro": (
        "low-key chiaroscuro, a single controlled source, most of the frame in black, "
        "and the lit edge carrying the form"
    ),
    "Fluorescent office": (
        "overhead fluorescent office light, slightly green, flat across the face, "
        "with a faint reflection from the ceiling"
    ),
    "Golden rim, cool fill": (
        "a warm rim from a low sun behind the subject "
        "and a cool soft fill from the open sky on the face"
    ),
    "On-camera flash": (
        "direct on-camera flash, a hard frontal specular, a short shadow thrown behind, "
        "and darker surroundings"
    ),
    "Beauty dish": (
        "a beauty dish just above the lens, crisp but soft facial light, "
        "a defined catchlight, and a gentle cheek shadow"
    ),
    "Ring light": (
        "a ring light around the lens, even frontal illumination, "
        "and a circular catchlight in both eyes"
    ),
    "Sunset backlight": (
        "sunset directly behind the subject, the figure edged in gold, "
        "with the face opened just enough to read"
    ),
    "Firelight": (
        "firelight from a low source nearby, warm illumination on one side "
        "and deep shadow on the other"
    ),
    "Forest canopy": (
        "dappled light through a forest canopy, small patches of sun "
        "and green-filtered shade across the subject"
    ),
    "Stage spotlight": (
        "a hard stage spotlight from above and in front, a bright pool on the subject, "
        "and the surroundings dropped to black"
    ),
    "Open shade": (
        "open shade outdoors, the subject lit by sky rather than sun, "
        "soft and even with a slightly cool cast"
    ),
    "Mixed color gels": (
        "a white key on the face, a cool gel on the shadow side, "
        "and a warm gel grazing the edge"
    ),
    "Dawn fog": (
        "low dawn light through fog, the source broad and milky, contrast softened, "
        "and highlights glowing around the subject"
    ),
}

COLOR = {
    "(none)": "",
    "Natural documentary": (
        "natural documentary color, true-to-life skin, restrained saturation, "
        "and no stylized grade"
    ),
    "Teal and orange": (
        "a teal-and-orange cinematic grade, cool shadows, warm skin highlights, "
        "and controlled contrast"
    ),
    "Kodak Portra warmth": (
        "Kodak Portra warmth, gentle highlight roll-off, flattering skin, "
        "and slightly faded pastels"
    ),
    "Fuji cool greens": (
        "a Fuji-like cool palette, greenish shadows, crisp midtones, and clean whites"
    ),
    "Bleach bypass": (
        "a bleach-bypass look, silver retained in the highlights, muted color, "
        "and gritty contrast"
    ),
    "Desaturated": (
        "desaturated color, hue pulled down so texture and light carry the image"
    ),
    "High-contrast film": (
        "high-contrast film color, deep blacks, bright highlights, and saturated midtones"
    ),
    "Soft pastel": (
        "a soft pastel palette, lifted blacks, low contrast, "
        "and pale pinks, blues, and creams"
    ),
    "Muted earth": (
        "a muted earth palette of ochre, olive, brown, and dusty clay, "
        "with restrained saturation"
    ),
    "Black and white": (
        "black and white, a full tonal scale from deep black to clean white, with color removed"
    ),
    "Sepia": (
        "a warm sepia grade, browns and creams in place of full color, like an aged photograph"
    ),
    "Cyberpunk neon": (
        "a cyberpunk palette, electric magenta and cyan against near-black shadows "
        "and wet highlights"
    ),
    "Golden luxury": (
        "a golden luxury grade, honey highlights, deep brown shadows, and a rich warm finish"
    ),
    "Clinical clean": (
        "a clinical clean grade, neutral white balance, accurate color, and almost no stylistic tint"
    ),
    "1970s vintage": (
        "a 1970s film look, warm midtones, slightly green shadows, gentle halation, and faded blacks"
    ),
    "Moody noir": (
        "a moody noir grade, crushed shadows, cool steel highlights, and only a trace of color"
    ),
    "Sun-faded summer": (
        "sun-faded summer color, bleached highlights, pale blues, and a warm haze over the frame"
    ),
    "Forest green": (
        "a forest-green cast, moss and deep green in the shadows, "
        "with skin kept just warm enough to read"
    ),
    "Arctic blue": (
        "an arctic blue palette, cold whites, ice-blue shadows, "
        "and very little warmth except in the skin"
    ),
    "Rose gold": (
        "a rose-gold grade, pink highlights, soft gold midtones, and gentle contrast"
    ),
    "Cross-processed": (
        "a cross-processed look, skewed color, cyan shadows, yellow-green highlights, "
        "and punchy contrast"
    ),
    "Technicolor": (
        "a rich Technicolor palette, saturated reds, deep blues, and greens that stay distinct"
    ),
    "Matte cinema": (
        "a matte cinema grade, lifted blacks, softened highlights, and a low-shine finish"
    ),
    "Warm tungsten interior": (
        "warm tungsten color indoors, orange practical light balanced so skin stays natural "
        "and the room stays amber"
    ),
    "Daylight neutral": (
        "neutral daylight color, a clean 5600K balance, honest whites, and no creative cast"
    ),
    "Autumn amber": (
        "an autumn amber palette, rust, gold, and brown dominating, "
        "with cooler notes only in the deepest shade"
    ),
    "Midnight blue": (
        "a midnight-blue grade, navy shadows, sparse warm pinpricks of light, and an overall cool key"
    ),
    "Dusty western": (
        "a dusty western grade, sun-bleached tan, a pale sky, and grit in the highlights"
    ),
    "Editorial fashion": (
        "an editorial fashion grade, precise skin, a slightly cool background, "
        "and contrast shaped around clothing and face"
    ),
    "Painterly": (
        "a painterly finish, softened micro-contrast, blended color transitions, "
        "and light that feels brushed rather than digital"
    ),
    "HDR crisp": (
        "a crisp HDR finish, extended local contrast, clear texture in shadows and highlights, "
        "and vivid but controlled color"
    ),
}
