(function(){
  const slides = Array.from(document.querySelectorAll('.slide'));
  let idx = 0;
  const total = slides.length;
  const slideCountEl = document.getElementById('slideCount');
  const slideIndexEl = document.getElementById('slideIndex');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  const screenshotBtn = document.getElementById('screenshot');
  slideCountEl.textContent = total;

  function show(i){
    slides.forEach(s=>s.classList.remove('active'));
    idx = (i+total)%total;
    slides[idx].classList.add('active');
    slideIndexEl.textContent = idx+1;
    // update document title
    const t = slides[idx].dataset.title || `Slide ${idx+1}`;
    document.title = `CSSA — ${t}`;
  }

  prevBtn.addEventListener('click', ()=> show(idx-1));
  nextBtn.addEventListener('click', ()=> show(idx+1));
  document.addEventListener('keydown', (e)=>{
    if(e.key === 'ArrowLeft') show(idx-1);
    if(e.key === 'ArrowRight') show(idx+1);
    if(e.key === 's' || e.key === 'S') toggleScreenshotMode();
  });

  let screenshot = false;
  function toggleScreenshotMode(){
    screenshot = !screenshot;
    if(screenshot){
      document.documentElement.classList.add('screenshot-mode');
      // force white background for screenshot
      document.body.style.background = '#ffffff';
      // optional: small delay to allow styles to apply
      setTimeout(()=> window.scrollTo(0,0), 50);
      screenshotBtn.textContent = 'Exit Screenshot (S)';
    } else {
      document.documentElement.classList.remove('screenshot-mode');
      document.body.style.background = '';
      screenshotBtn.textContent = 'Screenshot Mode (S)';
    }
  }

  // Initialize
  show(0);
})();
