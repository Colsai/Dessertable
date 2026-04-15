(function () {
    var activeBursts = 0;
    var MAX_BURSTS = 3;

    function triggerScreenFlash() {
        var el = document.getElementById('screen-flash');
        if (!el) return;
        el.classList.remove('flash-active');
        void el.offsetHeight; // force reflow to restart animation
        el.classList.add('flash-active');
        setTimeout(function () { el.classList.remove('flash-active'); }, 260);
    }

    function triggerPixelBurst(x, y) {
        if (activeBursts >= MAX_BURSTS) return;
        activeBursts++;

        // 8 directions: cardinal + diagonal
        var directions = [
            [-30, 0], [30, 0], [0, -30], [0, 30],
            [-21, -21], [21, -21], [-21, 21], [21, 21]
        ];

        // Alternate between ink and blue for visual variety
        var colors = [
            'var(--pixel-ink)',
            'var(--pixel-blue)',
            'var(--pixel-ink)',
            'var(--pixel-blue-bright)',
            'var(--pixel-ink)',
            'var(--pixel-blue)',
            'var(--pixel-ink)',
            'var(--pixel-blue)'
        ];

        directions.forEach(function (dir, i) {
            var p = document.createElement('div');
            p.className = 'pixel-burst-particle';
            p.setAttribute('aria-hidden', 'true');
            // Center the 8px particle on the click point
            p.style.cssText =
                'left:' + (x - 4) + 'px;' +
                'top:' + (y - 4) + 'px;' +
                '--dx:' + dir[0] + 'px;' +
                '--dy:' + dir[1] + 'px;' +
                'background:' + colors[i] + ';';
            document.body.appendChild(p);
            setTimeout(function () { if (p.parentNode) p.remove(); }, 520);
        });

        setTimeout(function () { activeBursts--; }, 520);
    }

    document.addEventListener('click', function (e) {
        // Skip disabled elements
        var target = e.target;
        if (target.disabled) return;
        var closest = target.closest('[disabled]');
        if (closest) return;

        triggerScreenFlash();
        triggerPixelBurst(e.clientX, e.clientY);
    });
})();
