import { gsap } from 'gsap';

/**
 * Intro: a logo animada toca grande no centro, encolhe enquanto o site aparece
 * e termina no canto superior esquerdo, no lugar da marca do topo.
 * Roda só uma vez por sessão e não roda com "reduzir movimento".
 */

// O recorte da marca do topo (logo-mark.png) usa 820 px de um quadro de 1080 px.
const RECORTE_MARCA = 820 / 1080;
// O K termina de aparecer por volta de 2,6 s do vídeo.
const INICIO_ENCOLHER_MS = 2700;

export function iniciarIntro() {
  const html = document.documentElement;
  if (!html.classList.contains('com-intro')) {
    revelarSemIntro();
    return;
  }

  const intro = document.querySelector<HTMLElement>('.intro')!;
  const video = document.querySelector<HTMLVideoElement>('.intro-video')!;
  const pular = intro.querySelector<HTMLButtonElement>('.intro-pular')!;
  const marcaImg = document.querySelector<HTMLElement>('.marca-img')!;

  gsap.set(video, { left: '50%', top: '50%', xPercent: -50, yPercent: -50 });
  gsap.set(marcaImg, { opacity: 0 });

  let tl: gsap.core.Timeline | null = null;
  let terminou = false;

  const terminar = () => {
    if (terminou) return;
    terminou = true;
    gsap.set(marcaImg, { opacity: 1 });
    intro.remove();
    video.remove();
    html.classList.remove('com-intro');
    gsap.set(['.topo > .wrap > *', '.hero-pe', '.hero-aura', '.linha > span'], { clearProps: 'all' });
    try { sessionStorage.setItem('kb-intro', '1'); } catch {}
  };

  const montarTimeline = () => {
    const alvo = marcaImg.getBoundingClientRect();
    const tamVideo = video.getBoundingClientRect().width;
    const escalaFinal = alvo.width / RECORTE_MARCA / tamVideo;
    const dx = alvo.left + alvo.width / 2 - window.innerWidth / 2;
    const dy = alvo.top + alvo.height / 2 - window.innerHeight / 2;

    tl = gsap.timeline({ onComplete: terminar });
    tl
      // 1. encolhe no centro e o fundo da intro some, revelando o site
      .to(video, { scale: 0.42, duration: 1.1, ease: 'power3.inOut' }, 0)
      .to(intro, { backgroundColor: 'rgba(11, 11, 20, 0)', duration: 1.0, ease: 'power2.inOut' }, 0.15)
      .to('.hero-aura', { opacity: 1, duration: 1.6, ease: 'power1.out' }, 0.4)
      .to('.linha > span', { y: 0, duration: 1.0, ease: 'power4.out', stagger: 0.12 }, 0.55)
      .to('.hero-pe', { opacity: 1, duration: 0.8, ease: 'power2.out' }, 1.05)
      // 2. vai para o canto superior esquerdo
      .to(video, { x: dx, y: dy, scale: escalaFinal, duration: 1.0, ease: 'power3.inOut' }, 1.25)
      .to('.topo > .wrap > *', { opacity: 1, duration: 0.6, ease: 'power2.out', stagger: 0.08 }, 1.75)
      .set(pular, { autoAlpha: 0 }, 1.25);
  };

  pular.addEventListener('click', () => {
    if (tl) tl.progress(1);
    else terminar();
  });

  // Se o vídeo não começar (autoplay bloqueado, rede lenta), mostra o site direto.
  const desistir = window.setTimeout(terminar, 2500);
  video.addEventListener('playing', () => {
    window.clearTimeout(desistir);
    window.setTimeout(() => !terminou && montarTimeline(), INICIO_ENCOLHER_MS);
  }, { once: true });
  video.addEventListener('error', terminar, { once: true });
  video.play().catch(terminar);
}

function revelarSemIntro() {
  document.querySelector('.intro')?.remove();
  document.querySelector('.intro-video')?.remove();
}
