# Recorded-reference opening

The user supplied `Recording 2026-11-12 205539.mp4` (45.77 seconds, 1878 × 878). It remains an untracked local reference and is not an application asset or repository upload.

The recording was visually inspected through a temporary local video viewer. Its opening uses a full-viewport black/white binary field, large overlapping boolean/Sequence typography, small technical captions, and symbol/pause controls. Around 21 seconds the title includes binary substitutions; later captured scenes show a blue/white explanatory layout and a four-verb interaction section. Those later screens are reference-site content, not ANAVO's product flow.

ANAVO recreates the opening composition as a live canvas and GSAP sequence using neon lime, purple and black. It does not play the recording or depend on the reference website. It is a visual reconstruction, not a claim of identical original source or timing.

## Implemented sequence

- Contiguous moving binary territories fill a responsive, device-pixel-ratio-aware canvas.
- Large pixel `anavo` and `power` lettering enters from opposite sides, accompanied by binary substitutions.
- A purple inversion phase interrupts the black/lime field.
- Pointer proximity reverses nearby cells.
- Symbol buttons switch between 0/1, directional signs and charge signs, including while paused.
- Pause freezes the GSAP timeline and canvas. Play continues it.
- A system-ready caption leads into a stepped column curtain and upward reveal of the existing application.
- Total automatic opening is approximately 7.4 seconds; the 45-second recording also includes later reference-page interactions.

## Accessibility and lifecycle

The opening runs on every page load and refresh, with a footer replay control. Enter ANAVO and Escape skip it. The background is inert while the dialog is open, focus is contained within its controls, and body scrolling is restored on completion/unmount. Reduced-motion preference skips the opening and existing application animations remain reduced. GSAP timelines, resize/keyboard listeners and focus changes are cleaned up on unmount.

Pixelify Sans is applied to the opening and main hero/brand/closing typography; IBM Plex Mono remains on technical controls and data. Google Fonts has system-font fallbacks. The backend, objective model and solver contracts are unchanged.

Implementation: `frontend/src/components/SequenceIntro.tsx` and `sequence-intro.css`; integration: `frontend/src/App.tsx`.
