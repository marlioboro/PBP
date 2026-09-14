const parallaxScene = document.querySelector('[data-parallax]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (parallaxScene) {
    let pointerX = 0;
    let pointerY = 0;
    let scrollOffset = 0;
    let animationFrame = null;

    function renderParallax() {
        parallaxScene.style.setProperty('--back-x', `${pointerX * -0.25}px`);
        parallaxScene.style.setProperty('--back-y', `${(pointerY * -0.2) - (scrollOffset * 0.35)}px`);
        parallaxScene.style.setProperty('--mid-x', `${pointerX * 0.45}px`);
        parallaxScene.style.setProperty('--mid-y', `${(pointerY * 0.35) - (scrollOffset * 0.7)}px`);
        parallaxScene.style.setProperty('--front-x', `${pointerX * 0.8}px`);
        parallaxScene.style.setProperty('--front-y', `${(pointerY * 0.55) - scrollOffset}px`);
        animationFrame = null;
    }

    function scheduleRender() {
        if (animationFrame === null) {
            animationFrame = window.requestAnimationFrame(renderParallax);
        }
    }

    function updatePointer(event) {
        if (reducedMotion.matches || event.pointerType === 'touch') {
            return;
        }

        pointerX = ((event.clientX / window.innerWidth) - 0.5) * 22;
        pointerY = ((event.clientY / window.innerHeight) - 0.5) * 14;
        scheduleRender();
    }

    function updateScroll() {
        if (reducedMotion.matches) {
            return;
        }

        scrollOffset = Math.min(window.scrollY, window.innerHeight) * 0.12;
        scheduleRender();
    }

    function resetParallax() {
        pointerX = 0;
        pointerY = 0;
        scrollOffset = 0;
        scheduleRender();
    }

    window.addEventListener('pointermove', updatePointer, { passive: true });
    window.addEventListener('scroll', updateScroll, { passive: true });
    reducedMotion.addEventListener('change', resetParallax);
    updateScroll();
}
