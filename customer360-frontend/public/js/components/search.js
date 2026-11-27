import { ApiService } from '../services/api.js';
import { Toast } from './toast.js';

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (character) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[character]);
}

const SECTION_LABELS = {
    account_and_site: 'Tài khoản và địa điểm',
    contacts_and_roles: 'Liên hệ và vai trò',
    recent_interactions: 'Tương tác gần đây',
    commercial_facts: 'Thông tin thương mại',
    service_issues: 'Vấn đề dịch vụ',
    suggested_questions_and_gaps: 'Câu hỏi gợi ý và dữ liệu còn thiếu'
};

export const SearchComponent = {
    currentFilter: 'ALL',
    searchSequence: 0,

    render(container, currentUser, accessToken, onNavigateToLogin) {
        this.accessToken = accessToken;
        this.onNavigateToLogin = onNavigateToLogin;
        container.innerHTML = `
            <div class="search-view-container">
                <div class="search-page-header">
                    <div class="search-title-group">
                        <h1 class="search-title">Tìm kiếm tài khoản doanh nghiệp</h1>
                        <p class="search-description">Chỉ hiển thị account trong phạm vi được cấp quyền.</p>
                    </div>
                    <button type="button" id="btn-back-to-login" class="btn-back-login">Đăng xuất</button>
                </div>
                <div class="search-box-card">
                    <form id="search-form" class="search-form-row">
                        <div class="search-input-wrapper">
                            <span class="search-icon-left" aria-hidden="true">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                    stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="7"></circle>
                                    <path d="m20 20-4-4"></path>
                                </svg>
                            </span>
                            <input type="search" id="account-search-input" class="search-input-control"
                                placeholder="Tên pháp lý hoặc mã số thuế" autocomplete="off" />
                            <button type="button" id="btn-clear-search-text" class="btn-clear-search"
                                title="Xóa nội dung tìm kiếm">×</button>
                        </div>
                        <button type="submit" class="btn-search-submit">Tìm kiếm</button>
                    </form>
                    <div class="filter-pills-row">
                        <span class="filter-label">Bộ lọc nhanh:</span>
                        <button type="button" class="filter-pill active" data-filter="ALL">Tất cả ngành</button>
                        <button type="button" class="filter-pill" data-filter="Công nghệ thông tin">Công nghệ thông tin & Viễn thông</button>
                        <button type="button" class="filter-pill" data-filter="Sản xuất">Sản xuất</button>
                        <button type="button" class="filter-pill" data-filter="Dược phẩm">Y tế & Dược phẩm</button>
                        <button type="button" class="filter-pill" data-filter="Bán lẻ">Bán lẻ</button>
                        <button type="button" class="filter-pill" data-filter="Năng lượng">Năng lượng</button>
                    </div>
                </div>
                <div class="results-summary-bar">
                    <div>Kết quả: <span id="results-count-text" class="results-count-badge">Đang tải...</span></div>
                    <div class="search-user-label">${escapeHtml(currentUser.full_name)} · ${escapeHtml(currentUser.role)}</div>
                </div>
                <div id="accounts-results-grid" class="accounts-grid"></div>
                <div id="accounts-empty-state" class="empty-state-box">
                    <h3 class="empty-title">Không tìm thấy tài khoản phù hợp</h3>
                    <p class="empty-subtitle">Thử từ khóa khác hoặc xóa bộ lọc ngành.</p>
                    <button type="button" id="btn-reset-filters" class="btn-reset-search">Xóa bộ lọc</button>
                </div>
            </div>
            <div id="briefing-modal-backdrop" class="modal-backdrop">
                <div class="modal-dialog">
                    <div class="modal-header">
                        <div class="modal-title-group"><h2 id="modal-account-title" class="modal-title">Account</h2></div>
                        <button type="button" id="btn-close-briefing-modal" class="btn-close-modal" title="Đóng">✕</button>
                    </div>
                    <div id="briefing-modal-body" class="modal-body"></div>
                    <div class="modal-footer">
                        <button type="button" id="btn-footer-close-modal" class="btn-modal-close-action">Đóng</button>
                    </div>
                </div>
            </div>
        `;

        const searchInput = container.querySelector('#account-search-input');
        const searchForm = container.querySelector('#search-form');
        const clearButton = container.querySelector('#btn-clear-search-text');
        const pills = container.querySelectorAll('.filter-pill');

        container.querySelector('#btn-back-to-login').addEventListener('click', onNavigateToLogin);
        searchForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.executeSearch(searchInput.value);
        });
        searchInput.addEventListener('input', () => {
            clearButton.classList.toggle('visible', Boolean(searchInput.value.trim()));
            this.executeSearch(searchInput.value);
        });
        clearButton.addEventListener('click', () => {
            searchInput.value = '';
            clearButton.classList.remove('visible');
            this.executeSearch('');
        });
        container.querySelector('#btn-reset-filters').addEventListener('click', () => {
            this.currentFilter = 'ALL';
            pills.forEach((pill) => pill.classList.toggle(
                'active',
                pill.getAttribute('data-filter') === 'ALL'
            ));
            this.executeSearch(searchInput.value);
        });
        pills.forEach((pill) => pill.addEventListener('click', () => {
            this.currentFilter = pill.getAttribute('data-filter');
            pills.forEach((item) => item.classList.toggle('active', item === pill));
            this.executeSearch(searchInput.value);
        }));

        const closeModal = () => container.querySelector('#briefing-modal-backdrop').classList.remove('visible');
        container.querySelector('#btn-close-briefing-modal').addEventListener('click', closeModal);
        container.querySelector('#btn-footer-close-modal').addEventListener('click', closeModal);
        container.querySelector('#briefing-modal-backdrop').addEventListener('click', (event) => {
            if (event.target.id === 'briefing-modal-backdrop') closeModal();
        });

        this.executeSearch('');
    },

    async executeSearch(query) {
        const sequence = ++this.searchSequence;
        const grid = document.querySelector('#accounts-results-grid');
        const emptyState = document.querySelector('#accounts-empty-state');
        const count = document.querySelector('#results-count-text');
        if (!grid || !emptyState || !count) return;

        try {
            const response = await ApiService.searchAccounts(query, this.accessToken);
            if (sequence !== this.searchSequence) return;
            let accounts = response.results || [];
            if (this.currentFilter !== 'ALL') {
                accounts = accounts.filter((account) =>
                    (account.industry || '').toLocaleLowerCase().includes(
                        this.currentFilter.toLocaleLowerCase()
                    )
                );
            }
            count.textContent = `${accounts.length} tài khoản`;
            emptyState.classList.toggle('visible', accounts.length === 0);
            grid.innerHTML = accounts.map((account) => this.renderAccountCard(account)).join('');
            grid.querySelectorAll('[data-action="view-account"]').forEach((button) => {
                button.addEventListener('click', () =>
                    this.handleViewAccount(button.getAttribute('data-account-id'))
                );
            });
        } catch (error) {
            if (sequence !== this.searchSequence) return;
            grid.innerHTML = '';
            count.textContent = 'Không tải được';
            emptyState.classList.add('visible');
            emptyState.querySelector('.empty-title').textContent = 'Không thể tải dữ liệu account';
            emptyState.querySelector('.empty-subtitle').textContent = error.message;
            Toast.show(error.message || 'Không thể tải account.', 'error');
            if (error.status === 401) this.onNavigateToLogin?.();
        }
    },

    renderAccountCard(account) {
        const isActive = account.status === 'ACTIVE';
        return `
            <article class="account-card">
                <div class="account-card-header">
                    <div class="account-name-group">
                        <h3 class="account-legal-name">${escapeHtml(account.legal_name)}</h3>
                        <span class="account-code-tag">MST: ${escapeHtml(account.tax_code || 'Chưa có')}</span>
                    </div>
                    <span class="status-badge ${isActive ? 'active' : 'inactive'}">
                        ${isActive ? 'ĐANG HOẠT ĐỘNG' : 'TẠM NGỪNG'}
                    </span>
                </div>
                <div class="account-detail-rows">
                    <div class="detail-row">
                        <span class="detail-label">Ngành:</span>
                        <span class="detail-val">${escapeHtml(account.industry || 'Chưa có')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">ID:</span>
                        <span class="detail-val">${escapeHtml(account.id)}</span>
                    </div>
                </div>
                <div class="account-actions">
                    <button type="button" class="btn-view-briefing" data-action="view-account"
                        data-account-id="${escapeHtml(account.id)}">
                        Chi tiết account & briefing
                    </button>
                </div>
            </article>
        `;
    },

    async handleViewAccount(accountId) {
        const backdrop = document.querySelector('#briefing-modal-backdrop');
        const title = document.querySelector('#modal-account-title');
        const body = document.querySelector('#briefing-modal-body');
        title.textContent = 'Đang tải dữ liệu...';
        body.innerHTML = '<p class="briefing-section-text">Đang truy vấn PostgreSQL...</p>';
        backdrop.classList.add('visible');

        try {
            const account = await ApiService.getAccount(accountId, this.accessToken);
            let briefing = null;
            try {
                briefing = await ApiService.getLatestBriefing(accountId, this.accessToken);
            } catch (error) {
                if (error.status !== 404) throw error;
            }
            const citations = briefing
                ? (await ApiService.getBriefingCitations(
                    briefing.briefing_id,
                    this.accessToken
                )).citations
                : [];
            this.renderAccountDetails(title, body, account, briefing, citations);
        } catch (error) {
            title.textContent = error.status === 403
                ? 'Quyền truy cập bị từ chối'
                : 'Không thể tải account';
            body.innerHTML = `<p class="briefing-section-text">${escapeHtml(error.message)}</p>`;
            Toast.show(error.message || 'Không thể tải account/briefing.', 'error');
            if (error.status === 401) this.onNavigateToLogin?.();
        }
    },

    renderAccountDetails(title, body, account, briefing, citations) {
        title.textContent = account.legal_name;
        const sites = account.sites || [];
        const siteOptions = [
            '<option value="">Toàn account</option>',
            ...sites.map((site) => `<option value="${escapeHtml(site.id)}">${escapeHtml(site.site_name)}</option>`)
        ].join('');
        const sections = briefing
            ? Object.entries(briefing.sections).map(([key, section]) => `
                <section class="briefing-section">
                    <h3 class="briefing-section-title">${escapeHtml(SECTION_LABELS[key] || key)}</h3>
                    <p class="briefing-section-text">${escapeHtml(section.content)}</p>
                    <p class="citation-source-tag">Citations: ${section.citations.length
                        ? escapeHtml(section.citations.join(', '))
                        : 'Không có'}</p>
                </section>
            `).join('')
            : '<p class="briefing-section-text">Account chưa có briefing đã lưu.</p>';
        const citationCards = citations.map((citation) => `
            <article class="citation-card">
                <span class="citation-source-tag">${escapeHtml(citation.source_type)} · #${citation.citation_number}</span>
                <p>${escapeHtml(citation.claim_text)}</p>
                <p class="briefing-section-text">${escapeHtml(citation.source_excerpt || '')}${
                    citation.page_number ? ` · Trang ${citation.page_number}` : ''
                }</p>
            </article>
        `).join('');
        const siteHtml = sites.length
            ? sites.map((site) =>
                `<p class="briefing-section-text">${escapeHtml(site.site_name)}${site.address
                    ? ` - ${escapeHtml(site.address)}`
                    : ''}</p>`
            ).join('')
            : '<p class="briefing-section-text">Chưa có địa điểm.</p>';

        body.innerHTML = `
            <section class="briefing-section">
                <h3 class="briefing-section-title">Chi tiết account</h3>
                <p class="briefing-section-text">MST: ${escapeHtml(account.tax_code || 'Chưa có')}</p>
                <p class="briefing-section-text">Ngành: ${escapeHtml(account.industry || 'Chưa có')}</p>
                <p class="briefing-section-text">Trạng thái: ${escapeHtml(account.status)}</p>
                ${siteHtml}
            </section>
            <section class="briefing-section">
                <h3 class="briefing-section-title">Briefing ${briefing ? `· ${escapeHtml(briefing.status)}` : ''}</h3>
                ${sections}
            </section>
            ${briefing ? `
                <section class="briefing-section">
                    <h3 class="briefing-section-title">Citations</h3>
                    ${citationCards || '<p class="briefing-section-text">Chưa có citations.</p>'}
                </section>
            ` : ''}
            <section class="briefing-section">
                <label for="briefing-site-select">Tạo briefing theo địa điểm</label>
                <select id="briefing-site-select">${siteOptions}</select>
                <button type="button" id="btn-generate-briefing" class="btn-view-briefing">
                    Tạo briefing mới
                </button>
            </section>
            <div class="compliance-banner">Không tự động ghi ngược dữ liệu vào CRM / ERP.</div>
        `;

        body.querySelector('#btn-generate-briefing').addEventListener('click', async (event) => {
            const button = event.currentTarget;
            const siteId = body.querySelector('#briefing-site-select').value;
            button.disabled = true;
            button.textContent = 'Đang tạo briefing...';
            try {
                const accepted = await ApiService.generateBriefing(
                    account.id,
                    siteId,
                    this.accessToken
                );
                const saved = await ApiService.getBriefing(
                    accepted.briefing_id,
                    this.accessToken
                );
                const savedCitations = (await ApiService.getBriefingCitations(
                    accepted.briefing_id,
                    this.accessToken
                )).citations;
                this.renderAccountDetails(title, body, account, saved, savedCitations);
                Toast.show('Briefing đã được tạo và lưu.', 'success');
            } catch (error) {
                button.disabled = false;
                button.textContent = 'Tạo briefing mới';
                Toast.show(error.message || 'Không thể tạo briefing.', 'error');
                if (error.status === 401) this.onNavigateToLogin?.();
            }
        });
    }
};
