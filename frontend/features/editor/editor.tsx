"use client";
import { useEditor } from "./hooks/use-editor";
import { LoadingOverlay } from "./components/loading-overlay";
import { EditorHeader } from "./components/editor-header";
import { LibraryPanel } from "./components/library-panel";
import { CanvasPanel } from "./components/canvas-panel";
import { InspectorPanel } from "./components/inspector-panel";
export default function Editor() {
  const editor = useEditor();
  const { keyboard, busy, exporting } = editor;
  return (
    <main className="app" onKeyDown={keyboard} aria-busy={busy || exporting}>
      <EditorHeader editor={editor} />
      <div className="workspace" inert={busy || exporting}>
        <LibraryPanel editor={editor} />
        <CanvasPanel editor={editor} />
        <InspectorPanel editor={editor} />
      </div>
      <LoadingOverlay busy={busy} exporting={exporting} />
    </main>
  );
}
