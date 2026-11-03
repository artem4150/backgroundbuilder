export type ExportAsset = {
  url: string;
  x: number;
  y: number;
  width: number;
  height: number;
  angle: number;
  id: string;
};
/** Embed immutable SVG source trees, namespace IDs and download a vector-only scene. */
export async function downloadSvg(specs: ExportAsset[], w: number, h: number) {
  const root = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  root.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  root.setAttribute("viewBox", `0 0 ${w} ${h}`);
  root.setAttribute("width", String(w));
  root.setAttribute("height", String(h));
  const texts = await Promise.all(
    specs.map((s) =>
      fetch(s.url).then((r) => {
        if (!r.ok) throw Error();
        return r.text();
      }),
    ),
  );
  specs.forEach((s, index) => {
    let text = texts[index];
    const ids = [...text.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
    ids.forEach((id) => {
      text = text
        .replaceAll(`id="${id}"`, `id="${s.id}-${id}"`)
        .replaceAll(`url(#${id})`, `url(#${s.id}-${id})`)
        .replaceAll(`href="#${id}"`, `href="#${s.id}-${id}"`);
    });
    const parsed = new DOMParser().parseFromString(text, "image/svg+xml");
    if (parsed.querySelector("parsererror") || parsed.documentElement.localName !== "svg")
      throw Error("Invalid SVG");
    const nested = parsed.documentElement;
    nested.setAttribute("x", String(s.x));
    nested.setAttribute("y", String(s.y));
    nested.setAttribute("width", String(s.width));
    nested.setAttribute("height", String(s.height));
    if (index === 0) nested.setAttribute("preserveAspectRatio", "none");
    const g = document.createElementNS(root.namespaceURI, "g");
    const vb = (nested.getAttribute("viewBox") || "0 0 1 1").split(/\s+/).map(Number);
    const scale = Math.min(s.width / vb[2], s.height / vb[3]);
    const sx = index === 0 ? s.width / vb[2] : scale,
      sy = index === 0 ? s.height / vb[3] : scale;
    const dx = index === 0 ? 0 : (s.width - vb[2] * scale) / 2,
      dy = index === 0 ? 0 : (s.height - vb[3] * scale) / 2;
    g.setAttribute(
      "transform",
      `translate(${s.x} ${s.y}) rotate(${s.angle} ${s.width / 2} ${s.height / 2}) translate(${dx} ${dy}) scale(${sx} ${sy}) translate(${-vb[0]} ${-vb[1]})`,
    );
    g.setAttribute("fill", nested.getAttribute("fill") || "none");
    g.setAttribute("data-object", s.id);
    while (nested.firstChild) g.append(nested.firstChild);
    root.append(g);
  });
  const url = URL.createObjectURL(
    new Blob([new XMLSerializer().serializeToString(root)], { type: "image/svg+xml" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = "composition.svg";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
