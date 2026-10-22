document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const statusBar = document.getElementById('status-bar');
    const resultsContainer = document.getElementById('results-container');
    const cardsGrid = document.getElementById('cards-grid');
    const exportJsonBtn = document.getElementById('export-json-btn');
    const clearBtn = document.getElementById('clear-btn');

    let analyzedFiles = [];

    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    function showStatus(msg, type = 'info') {
        statusBar.textContent = msg;
        statusBar.className = `status-bar ${type}`;
        statusBar.classList.remove('hidden');
        setTimeout(() => statusBar.classList.add('hidden'), 5000);
    }

    async function handleFiles(files) {
        if (files.length === 1) {
            await uploadSingleFile(files[0]);
        } else {
            await uploadBatchFiles(files);
        }
    }

    async function uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        showStatus(`Analyzing ${file.name}...`, 'info');
        try {
            const res = await fetch('/api/analyze', { method: 'POST', body: formData });
            const data = await res.json();

            if (!res.ok) throw new Error(data.error || 'Failed to analyze file');

            analyzedFiles.unshift(data);
            renderResults();
            showStatus(`Successfully analyzed ${file.name}`, 'info');
        } catch (err) {
            showStatus(err.message, 'error');
        }
    }

    async function uploadBatchFiles(files) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        showStatus(`Analyzing batch of ${files.length} files...`, 'info');
        try {
            const res = await fetch('/api/batch', { method: 'POST', body: formData });
            const data = await res.json();

            if (!res.ok) throw new Error(data.error || 'Failed batch analysis');

            data.results.forEach(meta => {
                if (!meta.error) analyzedFiles.unshift(meta);
            });
            renderResults();
            showStatus(`Batch analysis complete: processed ${data.count} files`, 'info');
        } catch (err) {
            showStatus(err.message, 'error');
        }
    }

    function renderResults() {
        if (analyzedFiles.length === 0) {
            resultsContainer.classList.add('hidden');
            return;
        }

        resultsContainer.classList.remove('hidden');
        cardsGrid.innerHTML = '';

        analyzedFiles.forEach((file, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';

            const riskLevel = file.security ? file.security.risk_level : 'safe';
            const riskWarnings = file.security && file.security.warnings.length > 0
                ? file.security.warnings.join(', ')
                : 'No suspicious indicators found.';

            card.innerHTML = `
                <div class="result-card-header">
                    <div>
                        <div class="file-title">${file.filename}</div>
                        <span class="file-category-badge">${file.category}</span>
                    </div>
                    <span class="file-size-badge">${file.size_human}</span>
                </div>

                <div class="meta-grid">
                    <div>
                        <span class="meta-label">MIME Type</span>
                        <span class="meta-value">${file.mime_type}</span>
                    </div>
                    <div>
                        <span class="meta-label">Extension</span>
                        <span class="meta-value">${file.extension || 'None'}</span>
                    </div>
                </div>

                <div class="hash-section">
                    <div class="hash-row">
                        <span class="meta-label">MD5 Checksum</span>
                        <div class="hash-value">
                            <span>${file.hashes.md5}</span>
                            <button class="copy-mini-btn" onclick="navigator.clipboard.writeText('${file.hashes.md5}')">Copy</button>
                        </div>
                    </div>
                    <div class="hash-row">
                        <span class="meta-label">SHA-256 Checksum</span>
                        <div class="hash-value">
                            <span>${file.hashes.sha256}</span>
                            <button class="copy-mini-btn" onclick="navigator.clipboard.writeText('${file.hashes.sha256}')">Copy</button>
                        </div>
                    </div>
                </div>

                <div class="security-section ${riskLevel}">
                    <strong>Security Assessment: ${riskLevel.toUpperCase()}</strong>
                    <p style="font-size:0.75rem;">${riskWarnings}</p>
                </div>

                ${renderContentDetails(file)}
            `;

            cardsGrid.appendChild(card);
        });
    }

    function renderContentDetails(file) {
        if (!file.analysis || Object.keys(file.analysis).length === 0) {
            return '';
        }

        if (file.category === 'image') {
            const img = file.analysis;
            return `
                <div class="content-section">
                    <h4>Image Attributes</h4>
                    <div class="content-details">
                        <div>Dimensions: <strong>${img.width} x ${img.height}</strong></div>
                        <div>Color Mode: <strong>${img.mode}</strong></div>
                        <div>Format: <strong>${img.format}</strong></div>
                        <div>Transparency: <strong>${img.has_transparency ? 'Yes' : 'No'}</strong></div>
                    </div>
                </div>
            `;
        }

        if (file.is_text) {
            const txt = file.analysis;
            return `
                <div class="content-section">
                    <h4>Text Metrics</h4>
                    <div class="content-details">
                        <div>Lines: <strong>${txt.line_count}</strong></div>
                        <div>Words: <strong>${txt.word_count}</strong></div>
                        <div>Characters: <strong>${txt.char_count}</strong></div>
                        <div>Encoding: <strong>${txt.encoding}</strong></div>
                    </div>
                </div>
            `;
        }

        return '';
    }

    exportJsonBtn.addEventListener('click', () => {
        if (analyzedFiles.length === 0) return;
        const blob = new Blob([JSON.stringify(analyzedFiles, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metadata_analysis_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    });

    clearBtn.addEventListener('click', () => {
        analyzedFiles = [];
        renderResults();
    });
});
