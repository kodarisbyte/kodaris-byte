import { gsap } from 'gsap';

/**
 * Intro: a logo animada toca grande no centro, encolhe enquanto o site aparece
 * e termina no canto superior esquerdo, no lugar da marca do topo.
 * Roda só uma vez por sessão e não roda com "reduzir movimento".
 *
 * O vídeo tem fundo preto. Em vez de mix-blend-mode (que o Chrome ignora quando
 * o vídeo vai para a camada de hardware, deixando um quadrado preto), cada frame
 * é desenhado num canvas WebGL que transforma o preto em transparência.
 */

// O recorte da marca do topo (logo-mark.png) usa 820 px de um quadro de 1080 px.
const RECORTE_MARCA = 820 / 1080;
// O K termina de aparecer por volta de 2,6 s do vídeo.
const INICIO_ENCOLHER_MS = 2700;

export function iniciarIntro() {
  const html = document.documentElement;
  const intro = document.querySelector<HTMLElement>('.intro');
  const canvas = document.querySelector<HTMLCanvasElement>('.intro-logo');
  const video = document.querySelector<HTMLVideoElement>('.intro-src');
  if (!html.classList.contains('com-intro') || !intro || !canvas || !video) {
    [intro, canvas, video].forEach((el) => el?.remove());
    return;
  }

  const pular = intro.querySelector<HTMLButtonElement>('.intro-pular')!;
  const marcaImg = document.querySelector<HTMLElement>('.marca-img')!;

  // Elemento que a animação move: o canvas, ou o próprio vídeo se não houver WebGL.
  const desenho = criarDesenho(canvas, video);
  const logo: HTMLElement = desenho ? canvas : video;
  if (!desenho) {
    canvas.remove();
    video.classList.add('plano-b');
  }

  gsap.set(logo, { left: '50%', top: '50%', xPercent: -50, yPercent: -50 });
  gsap.set(marcaImg, { opacity: 0 });

  let tl: gsap.core.Timeline | null = null;
  let terminou = false;

  const terminar = () => {
    if (terminou) return;
    terminou = true;
    desenho?.parar();
    gsap.set(marcaImg, { opacity: 1 });
    [intro, canvas, video].forEach((el) => el.remove());
    html.classList.remove('com-intro');
    gsap.set(['.topo > .wrap > *', '.hero-pe', '.hero-aura', '.linha > span'], { clearProps: 'all' });
    try { sessionStorage.setItem('kb-intro', '1'); } catch {}
  };

  const montarTimeline = () => {
    const alvo = marcaImg.getBoundingClientRect();
    const tamLogo = logo.getBoundingClientRect().width;
    const escalaFinal = alvo.width / RECORTE_MARCA / tamLogo;
    const dx = alvo.left + alvo.width / 2 - window.innerWidth / 2;
    const dy = alvo.top + alvo.height / 2 - window.innerHeight / 2;

    tl = gsap.timeline({ onComplete: terminar });
    if (location.search.includes('debug')) (window as any).__kbIntro = { tl, video };
    tl
      // 1. encolhe no centro e o fundo da intro some, revelando o site
      .to(logo, { scale: 0.42, duration: 1.1, ease: 'power3.inOut' }, 0)
      .to(intro, { backgroundColor: 'rgba(11, 11, 20, 0)', duration: 1.0, ease: 'power2.inOut' }, 0.15)
      .to('.hero-aura', { opacity: 1, duration: 1.6, ease: 'power1.out' }, 0.4)
      .to('.linha > span', { y: 0, duration: 1.0, ease: 'power4.out', stagger: 0.12 }, 0.55)
      .to('.hero-pe', { opacity: 1, duration: 0.8, ease: 'power2.out' }, 1.05)
      // 2. vai para o canto superior esquerdo
      .to(logo, { x: dx, y: dy, scale: escalaFinal, duration: 1.0, ease: 'power3.inOut' }, 1.25)
      .to('.topo > .wrap > *', { opacity: 1, duration: 0.6, ease: 'power2.out', stagger: 0.08 }, 1.75)
      .set(pular, { autoAlpha: 0 }, 1.25);
  };

  pular.addEventListener('click', () => {
    if (tl) tl.progress(1);
    else terminar();
  });

  // Se o vídeo não começar (autoplay bloqueado, rede lenta), mostra o site direto.
  const desistir = window.setTimeout(terminar, 3000);
  video.addEventListener('playing', () => {
    window.clearTimeout(desistir);
    desenho?.iniciar();
    window.setTimeout(() => !terminou && montarTimeline(), INICIO_ENCOLHER_MS);
  }, { once: true });
  video.addEventListener('error', terminar, { once: true });
  video.play().catch(terminar);
}

/** Desenha o vídeo no canvas com o preto convertido em alfa. Retorna null sem WebGL. */
function criarDesenho(canvas: HTMLCanvasElement, video: HTMLVideoElement) {
  const gl = canvas.getContext('webgl', { premultipliedAlpha: true, alpha: true, antialias: false });
  if (!gl) return null;

  const vs = `
    attribute vec2 p;
    varying vec2 uv;
    void main() {
      uv = vec2(p.x * 0.5 + 0.5, 0.5 - p.y * 0.5);
      gl_Position = vec4(p, 0.0, 1.0);
    }`;
  // O vídeo é "logo sobre preto", ou seja, cor já pré-multiplicada pelo alfa.
  // Alfa = canal mais claro; um corte suave some com o ruído do fundo.
  const fs = `
    precision mediump float;
    varying vec2 uv;
    uniform sampler2D tex;
    void main() {
      vec3 c = texture2D(tex, uv).rgb;
      float a = max(c.r, max(c.g, c.b));
      float k = smoothstep(0.015, 0.05, a);
      // esmaece o brilho antes da borda do quadro (a esfera ocupa raio ~0,3)
      k *= 1.0 - smoothstep(0.34, 0.5, distance(uv, vec2(0.5)));
      gl_FragColor = vec4(c * k, a * k);
    }`;

  const compilar = (tipo: number, src: string) => {
    const s = gl.createShader(tipo)!;
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  };
  const prog = gl.createProgram()!;
  gl.attachShader(prog, compilar(gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, compilar(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.clearColor(0, 0, 0, 0);

  let ativo = false;
  const desenhar = () => {
    if (!ativo) return;
    if (video.readyState >= 2) {
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, video);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    agendar();
  };
  const v = video as HTMLVideoElement & { requestVideoFrameCallback?: (cb: () => void) => number };
  const agendar = () => {
    // fora do loop de vídeo (pausado no último frame) continua desenhando via rAF
    if (v.requestVideoFrameCallback && !video.paused && !video.ended) v.requestVideoFrameCallback(desenhar);
    else requestAnimationFrame(desenhar);
  };

  return {
    iniciar() { if (!ativo) { ativo = true; desenhar(); } },
    parar() { ativo = false; },
  };
}
