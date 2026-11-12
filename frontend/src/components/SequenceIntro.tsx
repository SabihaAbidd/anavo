import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import './sequence-intro.css';

type SymbolMode = 'binary' | 'direction' | 'charge';

/** A live generative composition rebuilt from the supplied recording, not video playback. */
export default function SequenceIntro({ done }: { done: () => void }) {
  const root = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const timeline = useRef<gsap.core.Timeline | null>(null);
  const repaint = useRef<(() => void) | null>(null);
  const mode = useRef<SymbolMode>('binary');
  const pointer = useRef({ x: -1000, y: -1000 });
  const [paused, setPaused] = useState(false);
  const [selectedMode, setSelectedMode] = useState<SymbolMode>('binary');

  useEffect(() => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      done();
      return;
    }
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    root.current?.querySelector<HTMLButtonElement>('button')?.focus();
    const element = canvas.current!;
    const context = element.getContext('2d');
    if (!context) { done(); return () => { document.body.style.overflow = previousOverflow; }; }
    let width = 0;
    let height = 0;
    let cell = 52;
    let columns = 0;
    let rows = 0;
    let lastFrame = '';
    const clock = { time: 0 };
    const resize = () => {
      const rect = root.current!.getBoundingClientRect();
      width = rect.width; height = rect.height;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      element.width = Math.round(width * dpr);
      element.height = Math.round(height * dpr);
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      cell = width < 600 ? 34 : Math.max(44, Math.round(width / 25));
      columns = Math.ceil(width / cell); rows = Math.ceil(height / cell);
      lastFrame = '';
      repaint.current?.();
    };
    const draw = () => {
      const frame = Math.floor(clock.time * 9);
      const renderKey = `${frame}:${mode.current}`;
      if (renderKey === lastFrame) return;
      lastFrame = renderKey;
      const inverted = clock.time >= 3 && clock.time < 4.35;
      const base = inverted ? '#a182ff' : '#090b08';
      const ink = inverted ? '#11100e' : '#b7ff39';
      const symbols = mode.current === 'binary' ? ['0', '1'] : mode.current === 'direction' ? ['<', '>'] : ['−', '+'];
      context.fillStyle = base; context.fillRect(0, 0, width, height);
      context.font = `500 ${Math.round(cell * .69)}px "IBM Plex Mono", monospace`;
      context.textAlign = 'center'; context.textBaseline = 'middle';
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < columns; x++) {
          // Moving contiguous territories rather than unrelated flashing random pixels.
          const field = Math.sin(x * .83 + frame * .22) + Math.cos(y * .91 - frame * .18)
            + Math.sin((x + y) * .41 + frame * .12);
          const nearPointer = Math.hypot(x * cell - pointer.current.x, y * cell - pointer.current.y) < cell * 2.2;
          const bit = (field > .2) !== nearPointer;
          const accent = Math.sin(x * .27 - y * .34 + frame * .08) > .87;
          context.fillStyle = bit ? (accent && !inverted ? '#a182ff' : ink) : base;
          context.fillRect(x * cell, y * cell, cell, cell);
          context.fillStyle = bit ? base : ink;
          context.fillText(symbols[bit ? 1 : 0], (x + .5) * cell, (y + .5) * cell + 1);
        }
      }
    };
    resize();
    repaint.current = draw;
    window.addEventListener('resize', resize);
    const ctx = gsap.context(() => {
      const sequence = gsap.timeline({ onComplete: done });
      timeline.current = sequence;
      sequence.to(clock, { time: 7.4, duration: 7.4, ease: 'none', onUpdate: draw }, 0)
        .from('.sequence-header, .sequence-caption, .sequence-bottom', { opacity: 0, duration: .45, stagger: .12 }, .1)
        .from('.sequence-title-one', { xPercent: -105, duration: 1.05, ease: 'expo.out' }, .3)
        .from('.sequence-title-two', { xPercent: 110, duration: 1.15, ease: 'expo.out' }, .55)
        .to('.sequence-code', { textContent: '101101', duration: 1.1, snap: { textContent: 1 }, ease: 'steps(9)' }, 1.8)
        .to('.sequence-title-two', { xPercent: -8, duration: 1.4, ease: 'power2.inOut' }, 2.3)
        .to('.sequence-title-one', { xPercent: 5, duration: 1.4, ease: 'power2.inOut' }, 2.3)
        .to('.sequence-code', { textContent: '010010', duration: 1.25, snap: { textContent: 1 }, ease: 'steps(10)' }, 3.4)
        .to('.sequence-titles', { scale: .86, duration: .8, ease: 'power3.inOut' }, 4.6)
        .to('.sequence-canvas', { opacity: .18, duration: .8 }, 4.6)
        .to('.sequence-caption', { opacity: 0, duration: .25 }, 4.8)
        .from('.sequence-ready', { opacity: 0, y: 20, duration: .5 }, 5)
        .to('.sequence-title-two', { clipPath: 'inset(0 0 100% 0)', duration: .55, ease: 'steps(7)' }, 5.75)
        .to('.sequence-title-one', { yPercent: 30, duration: .55, ease: 'power3.inOut' }, 5.75)
        .to('.sequence-curtain', { scaleY: 1, duration: .55, stagger: { each: .035, from: 'center' }, ease: 'steps(5)' }, 6.1)
        .to(root.current, { yPercent: -100, duration: .65, ease: 'power4.inOut' }, 6.75);
    }, root);
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') done();
      if (event.key !== 'Tab') return;
      const controls = Array.from(root.current!.querySelectorAll<HTMLButtonElement>('button'));
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', onKey);
    return () => {
      ctx.revert(); timeline.current = null; repaint.current = null;
      window.removeEventListener('resize', resize);
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = previousOverflow;
      if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
    };
  }, [done]);

  function chooseMode(next: SymbolMode) { mode.current = next; setSelectedMode(next); repaint.current?.(); }
  function togglePause() { timeline.current?.paused(!paused); setPaused(!paused); }

  return <div className="sequence-intro" ref={root} role="dialog" aria-modal="true" aria-label="ANAVO binary opening sequence"
    onPointerMove={event => { pointer.current = { x: event.clientX, y: event.clientY }; }}
    onPointerLeave={() => { pointer.current = { x: -1000, y: -1000 }; }}>
    <canvas className="sequence-canvas" ref={canvas} aria-hidden="true" />
    <div className="sequence-header"><span className="sequence-brand">anavo<span>®</span></span>
      <div className="sequence-controls" aria-label="Animation controls">
        <button aria-label="Plus and minus symbols" aria-pressed={selectedMode === 'charge'} onClick={() => chooseMode('charge')}>+/−</button>
        <button aria-label="Binary symbols" aria-pressed={selectedMode === 'binary'} onClick={() => chooseMode('binary')}>0/1</button>
        <button aria-label="Direction symbols" aria-pressed={selectedMode === 'direction'} onClick={() => chooseMode('direction')}>{'><'}</button>
        <button aria-label={paused ? 'Play opening' : 'Pause opening'} onClick={togglePause}>{paused ? '▶ PLAY' : 'Ⅱ PAUSE'}</button>
      </div></div>
    <div className="sequence-kicker"><span>ANAVO / GENERATIVE ENERGY SYSTEMS</span><span>PK—001</span></div>
    <div className="sequence-titles" aria-hidden="true"><div className="sequence-title-one">anavo</div><div className="sequence-title-two">power<span className="sequence-code">010101</span></div></div>
    <div className="sequence-caption"><p>A little power.<br/>A world of possibility.</p><span>FROM BINARY CHOICES<br/>TO BRIGHTER NIGHTS.</span></div>
    <div className="sequence-ready">SYSTEM READY <span>→</span> POWER WHAT MATTERS.</div>
    <div className="sequence-ruler" aria-hidden="true">{Array.from({ length: 12 }, (_, i) => <i key={i} />)}</div>
    <div className="sequence-bottom"><span>0 = DEFER / 1 = POWER</span><button onClick={done}>ENTER ANAVO ↗ <small>SKIP INTRO / ESC</small></button><span>QUANTUM ASSISTED.<br/>HUMAN CENTERED.</span></div>
    <div className="sequence-curtains" aria-hidden="true">{Array.from({ length: 14 }, (_, i) => <i key={i} className="sequence-curtain" />)}</div>
  </div>;
}
