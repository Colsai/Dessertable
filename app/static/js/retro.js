/*
 * ink.js — subtle ink drop effect on interaction.
 * Replaces the former 8-bit pixel burst with a soft radial expand.
 */
(function () {
    var activeBursts = 0;
    var maxBursts = 3;

    document.addEventListener('click', function (e) {
        if (activeBursts >= maxBursts) return;
        var target = e.target;
        if (target.disabled || (target.closest && target.closest('[disabled]'))) return;

        activeBursts++;
        var drop = document.createElement('div');
        drop.setAttribute('aria-hidden', 'true');
        drop.style.cssText =
            'position:fixed;' +
            'left:' + (e.clientX - 20) + 'px;' +
            'top:' + (e.clientY - 20) + 'px;' +
            'width:40px;height:40px;' +
            'border-radius:50%;' +
            'border:1px solid rgba(46,74,110,0.45);' +
            'pointer-events:none;z-index:99998;' +
            'animation:inkDrop 0.5s ease-out forwards;';
        document.body.appendChild(drop);
        setTimeout(function () {
            if (drop.parentNode) drop.remove();
            activeBursts--;
        }, 520);
    });
})();
