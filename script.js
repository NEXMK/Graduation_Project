// Apply saved theme immediately before paint (prevents flash)
(function () {
    const saved = localStorage.getItem('chatcsv-theme') || 'dark';
    document.body.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {

    // ── Theme Toggle ──────────────────────────────────────────────────────────
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.body.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', next);
            localStorage.setItem('chatcsv-theme', next);
        });
    }

    // ── Auth Modal ────────────────────────────────────────────────────────────
    const backdrop   = document.getElementById('authBackdrop');
    const modalClose = document.getElementById('modalClose');
    const loginBtn   = document.getElementById('loginBtn');
    const signupBtn  = document.getElementById('signupBtn');
    const tabs       = document.querySelectorAll('.modal-tab');
    const panels     = document.querySelectorAll('.modal-panel');

    function openModal(tabId) {
        if (!backdrop) return;
        switchTab(tabId);
        backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        const panel = document.getElementById(tabId === 'tabSignIn' ? 'panelSignIn' : 'panelSignUp');
        const first = panel && panel.querySelector('input');
        if (first) setTimeout(() => first.focus(), 120);
    }

    function closeModal() {
        if (!backdrop) return;
        backdrop.classList.remove('open');
        document.body.style.overflow = '';
        clearErrors();
    }

    function switchTab(tabId) {
        tabs.forEach(t => t.classList.toggle('active', t.id === tabId));
        panels.forEach(p => {
            const match = (tabId === 'tabSignIn' && p.id === 'panelSignIn') ||
                        (tabId === 'tabSignUp' && p.id === 'panelSignUp');
            p.classList.toggle('active', match);
        });
        clearErrors();
    }

    if (loginBtn)  loginBtn.addEventListener('click', () => openModal('tabSignIn'));
    if (signupBtn) signupBtn.addEventListener('click', () => openModal('tabSignUp'));
    if (modalClose) modalClose.addEventListener('click', closeModal);
    
    if (backdrop) {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.id));
    });

    document.querySelectorAll('.link-btn[data-switch]').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.getAttribute('data-switch')));
    });

    // Show / Hide Password
    document.querySelectorAll('.toggle-pw').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.closest('.input-wrapper').querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = '🙈';
            } else {
                input.type = 'password';
                btn.textContent = '👁️';
            }
        });
    });

    // Validation helpers
    function showError(input, msg) {
        const wrapper = input.closest('.input-wrapper');
        const group   = input.closest('.field-group');
        wrapper.classList.add('error');
        const old = group.querySelector('.field-error');
        if (old) old.remove();
        const err = document.createElement('span');
        err.className = 'field-error';
        err.textContent = msg;
        group.appendChild(err);
        input.addEventListener('input', () => {
            wrapper.classList.remove('error');
            err.remove();
        }, { once: true });
    }

    function clearErrors() {
        document.querySelectorAll('.input-wrapper.error').forEach(w => w.classList.remove('error'));
        document.querySelectorAll('.field-error').forEach(e => e.remove());
    }

    const emailRx = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const formSignIn = document.getElementById('formSignIn');
    if (formSignIn) {
        formSignIn.addEventListener('submit', (e) => {
            e.preventDefault();
            let ok = true;
            const email = document.getElementById('siEmail');
            const pw    = document.getElementById('siPassword');
            if (!emailRx.test(email.value.trim())) { showError(email, 'Enter a valid email.'); ok = false; }
            if (pw.value.length < 6)               { showError(pw,    'At least 6 characters.'); ok = false; }
            if (ok) {
                alert('Signed in! Replace this with your real backend call.');
                closeModal();
            }
        });
    }

    const formSignUp = document.getElementById('formSignUp');
    if (formSignUp) {
        formSignUp.addEventListener('submit', (e) => {
            e.preventDefault();
            let ok      = true;
            const uname   = document.getElementById('suUsername');
            const email   = document.getElementById('suEmail');
            const pw      = document.getElementById('suPassword');
            const confirm = document.getElementById('suConfirm');
            const terms   = document.getElementById('suTerms');
            if (uname.value.trim().length < 3)     { showError(uname,   'At least 3 characters.'); ok = false; }
            if (!emailRx.test(email.value.trim())) { showError(email,   'Enter a valid email.'); ok = false; }
            if (pw.value.length < 8)               { showError(pw,      'At least 8 characters.'); ok = false; }
            if (confirm.value !== pw.value)        { showError(confirm, 'Passwords do not match.'); ok = false; }
            if (!terms.checked) {
                const lbl = terms.closest('.checkbox-label');
                lbl.style.color = '#ef4444';
                setTimeout(() => lbl.style.color = '', 1500);
                ok = false;
            }
            if (ok) {
                alert('Account created! Replace this with your real backend call.');
                closeModal();
            }
        });
    }


    // ── Smooth scrolling for anchor links ─────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ── File Upload Logic ─────────────────────────────────────────────────────
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const removeBtn = document.getElementById('remove-file');
    const startChatBtn = document.getElementById('start-chat');

    // Original elements to hide/show
    const uploadIconWrapper = dropZone.querySelector('.upload-icon-wrapper');
    const uploadTitle = dropZone.querySelector('h3');
    const uploadHint = dropZone.querySelector('.upload-hint');
    const uploadBtn = dropZone.querySelector('.upload-btn');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle selected files from dialog
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];

        // Validate file type
        if (file.name.endsWith('.csv') || file.type === 'text/csv') {
            displayFile(file);
        } else {
            alert('Please upload a valid CSV file.');
        }
    }

    function displayFile(file) {
        fileNameDisplay.textContent = file.name;

        // Hide original upload Prompts
        uploadIconWrapper.style.display = 'none';
        uploadTitle.style.display = 'none';
        uploadHint.style.display = 'none';
        uploadBtn.style.display = 'none';

        // Show file info and start chat button
        fileInfo.classList.remove('hidden');
        startChatBtn.classList.remove('hidden');
    }

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering the dropzone click if any

        // Reset file input
        fileInput.value = '';

        // Hide file info and chat button
        fileInfo.classList.add('hidden');
        startChatBtn.classList.add('hidden');

        // Show original upload Prompts
        uploadIconWrapper.style.display = 'flex';
        uploadTitle.style.display = 'block';
        uploadHint.style.display = 'block';
        uploadBtn.style.display = 'inline-flex';
    });

    startChatBtn.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (file || document.querySelector('.file-name').textContent !== 'dataset.csv') {
            // In a real app, this would upload the file and redirect to the chat interface
            startChatBtn.textContent = 'Processing...';
            startChatBtn.style.opacity = '0.8';

            setTimeout(() => {
                alert('File uploaded successfully! Redirecting to chat interface...');
                startChatBtn.textContent = 'Initialize Chat Interface';
                startChatBtn.style.opacity = '1';
            }, 1500);
        } else {
            alert('Please select a file first.');
        }
    });
});
