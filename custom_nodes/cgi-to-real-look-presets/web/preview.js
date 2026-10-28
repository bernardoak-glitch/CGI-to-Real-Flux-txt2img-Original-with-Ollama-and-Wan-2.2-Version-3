import { app } from "../../scripts/app.js";

const KINDS = {
    CGICameraLens: "camera",
    CGILightingSetup: "lighting",
    CGIColorAesthetic: "color",
};

function slug(label) {
    return String(label || "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "") || "none";
}

function kindOf(node) {
    return KINDS[node.comfyClass] || KINDS[node.type];
}

function linkedPreview(node) {
    const output = (node.outputs || []).find((item) => item.name === "preview");
    const linkId = output && output.links && output.links[0];
    if (linkId == null || !app.graph.links) return null;
    const link = app.graph.links[linkId];
    if (!link) return null;
    return app.graph.getNodeById(link.target_id);
}

app.registerExtension({
    name: "cgi-to-real.look-preview",
    async nodeCreated(node) {
        const kind = kindOf(node);
        if (!kind) return;

        const img = new Image();
        const show = () => {
            const combo = (node.widgets || []).find((item) => item.name === "preset");
            const label = combo ? combo.value : "(none)";
            img.src = `extensions/cgi-to-real-look-presets/thumbs/${kind}/${slug(label)}.png`;
            const preview = linkedPreview(node);
            if (preview) {
                preview.imgs = [img];
                app.graph.setDirtyCanvas(true, true);
            }
        };

        const combo = (node.widgets || []).find((item) => item.name === "preset");
        if (combo) {
            const previous = combo.callback;
            combo.callback = function () {
                if (previous) previous.apply(this, arguments);
                show();
            };
        }
        img.onload = () => app.graph.setDirtyCanvas(true, true);
        setTimeout(show, 50);
    },
});
