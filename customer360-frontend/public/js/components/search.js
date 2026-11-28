/**
 * Account Search Component
 * Features:
 * - Search bar with instant / button search
 * - Result cards with legal name, tax code, industry, status, sites
 * - Empty state when not found
 * - Back to login button
 * - Customer 360 Briefing modal that faithfully demonstrates the Sequence Diagram flow:
 *   [Permission revoked] -> HTTP 403 -> Display access revoked
 *   [Permission still valid] -> HTTP 200 -> Display Briefing and warnings
 *   No automatic write-back to CRM / ERP
 */
import { ApiService } from '../services/api.js';
import { Toast } from './toast.js';

export const SearchComponent = {
    accounts: [],
    currentFilter: 'ALL',

    render(container, currentUser, onNavigateToLogin) {
        container.innerHTML = `
            <div class="search-view-container">
                <!-- Header -->
                <div class="search-page-header">
                    <div class="search-title-group">
                        <h1 class="search-title">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2.2">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                            <span>Tìm kiếm tài khoản doanh nghiệp</span>
                        </h1>
                        <p class="search-description">Tra cứu hồ sơ khách hàng 360, phạm vi phân quyền và trạng thái tóm tắt</p>
                    </div>

                    <button type="button" id="btn-back-to-login" class="btn-back-login">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="19" y1="12" x2="5" y2="12"></line>
                            <polyline points="12 19 5 12 12 5"></polyline>
                        </svg>
                        <span>Quay lại Đăng nhập</span>
                    </button>
                </div>

                <!-- Search Input Card -->
                <div class="search-box-card">
                    <form id="search-form" class="search-form-row">
                        <div class="search-input-wrapper">
                            <span class="search-icon-left">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                </svg>
                            </span>
                            <input
                                type="text"
                                id="account-search-input"
                                class="search-input-control"
                                placeholder="Nhập tên pháp lý công ty, mã số thuế (MST) hoặc ngành nghề..."
                                autocomplete="off"
                            />
                            <button type="button" id="btn-clear-search-text" class="btn-clear-search" title="Xóa nội dung tìm kiếm">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                </svg>
                            </button>
                        </div>

                        <button type="submit" id="btn-search-action" class="btn-search-submit">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                            <span>Tìm kiếm</span>
                        </button>
                    </form>

                    <!-- Industry quick filters -->
                    <div class="filter-pills-row">
                        <span class="filter-label">Bộ lọc nhanh:</span>
                        <button type="button" class="filter-pill active" data-filter="ALL">Tất cả ngành</button>
                        <button type="button" class="filter-pill" data-filter="Viễn thông">CNTT & Viễn thông</button>
                        <button type="button" class="filter-pill" data-filter="Sản xuất">Sản xuất</button>
                        <button type="button" class="filter-pill" data-filter="Dược phẩm">Y tế & Dược phẩm</button>
                        <button type="button" class="filter-pill" data-filter="Bán lẻ">Bán lẻ</button>
                        <button type="button" class="filter-pill" data-filter="Năng lượng">Năng lượng</button>
                    </div>
                </div>

                <!-- Results Summary Bar -->
                <div class="results-summary-bar">
                    <div>Kết quả tra cứu: <span id="results-count-text" class="results-count-badge">0 tài khoản</span></div>
                    <div style="font-size: 0.8rem; color: var(--color-text-muted);">
                        Sơ đồ kiến trúc: Authorization Service & Briefing Orchestrator
                    </div>
                </div>

                <!-- Accounts Grid Area -->
                <div id="accounts-results-grid" class="accounts-grid"></div>

                <!-- Empty State -->
                <div id="accounts-empty-state" class="empty-state-box">
                    <div class="empty-illustration">
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            <line x1="8" y1="11" x2="14" y2="11"></line>
                        </svg>
                    </div>
                    <h3 class="empty-title">Không tìm thấy tài khoản phù hợp</h3>
                    <p class="empty-subtitle">Không có tài khoản nào khớp với từ khóa đã nhập. Vui lòng thử tìm kiếm bằng mã số thuế, tên pháp lý khác hoặc thiết lập lại bộ lọc.</p>
                    <button type="button" id="btn-reset-filters" class="btn-reset-search">Xem tất cả tài khoản</button>
                </div>
            </div>

            <!-- Briefing Modal (Sequence Diagram Visualizer) -->
            <div id="briefing-modal-backdrop" class="modal-backdrop">
                <div class="modal-dialog">
                    <div class="modal-header">
                        <div class="modal-title-group">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                                <polyline points="10 9 9 9 8 9"></polyline>
                            </svg>
                            <h2 id="modal-account-title" class="modal-title">Hồ sơ Customer 360</h2>
                        </div>
                        <button type="button" id="btn-close-briefing-modal" class="btn-close-modal" title="Đóng">✕</button>
                    </div>
                    <div id="briefing-modal-body" class="modal-body">
                        <!-- Dynamic content injected here -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" id="btn-footer-close-modal" class="btn-modal-close-action">Đóng cửa sổ</button>
                    </div>
                </div>
            </div>
        `;

        this.attachEvents(container, currentUser, onNavigateToLogin);
        this.executeSearch('');
    },

    attachEvents(container, currentUser, onNavigateToLogin) {
        const backBtn = container.querySelector('#btn-back-to-login');
        const searchForm = container.querySelector('#search-form');
        const searchInput = container.querySelector('#account-search-input');
        const clearBtn = container.querySelector('#btn-clear-search-text');
        const resetBtn = container.querySelector('#btn-reset-filters');
        const filterPills = container.querySelectorAll('.filter-pill');
        const modalBackdrop = container.querySelector('#briefing-modal-backdrop');
        const modalCloseBtn = container.querySelector('#btn-close-briefing-modal');
        const modalFooterCloseBtn = container.querySelector('#btn-footer-close-modal');

        // Back to Login
        backBtn.addEventListener('click', () => {
            onNavigateToLogin();
        });

        // Search Form Submit
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.executeSearch(searchInput.value.trim());
        });

        // Search input keyup/change
        searchInput.addEventListener('input', () => {
            const val = searchInput.value;
            if (val.trim()) {
                clearBtn.classList.add('visible');
            } else {
                clearBtn.classList.remove('visible');
            }
            this.executeSearch(val.trim());
        });

        // Clear Search text
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.classList.remove('visible');
            searchInput.focus();
            this.executeSearch('');
        });

        // Reset search button inside empty state
        resetBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.classList.remove('visible');
            filterPills.forEach(p => p.classList.remove('active'));
            container.querySelector('[data-filter="ALL"]').classList.add('active');
            this.currentFilter = 'ALL';
            this.executeSearch('');
        });

        // Filter pills click
        filterPills.forEach(pill => {
            pill.addEventListener('click', () => {
                filterPills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                this.currentFilter = pill.getAttribute('data-filter');
                this.executeSearch(searchInput.value.trim());
            });
        });

        // Close Modal
        const closeModal = () => modalBackdrop.classList.remove('visible');
        modalCloseBtn.addEventListener('click', closeModal);
        modalFooterCloseBtn.addEventListener('click', closeModal);
        modalBackdrop.addEventListener('click', (e) => {
            if (e.target === modalBackdrop) closeModal();
        });
    },

    async executeSearch(query) {
        const resultsGrid = document.querySelector('#accounts-results-grid');
        const emptyState = document.querySelector('#accounts-empty-state');
        const countText = document.querySelector('#results-count-text');

        if (!resultsGrid) return;

        const res = await ApiService.searchAccounts(query);
        let list = res.data || [];

        // Apply industry filter pill if selected
        if (this.currentFilter && this.currentFilter !== 'ALL') {
            list = list.filter(acc => acc.industry.toLowerCase().includes(this.currentFilter.toLowerCase()));
        }

        this.accounts = list;
        countText.textContent = `${list.length} tài khoản`;

        if (list.length === 0) {
            resultsGrid.innerHTML = '';
            emptyState.classList.add('visible');
        } else {
            emptyState.classList.remove('visible');
            this.renderCards(resultsGrid, list);
        }
    },

    renderCards(container, accounts) {
        container.innerHTML = accounts.map(acc => {
            const isRevoked = !acc.has_permission;
            const statusBadgeClass = isRevoked ? 'revoked' : (acc.status === 'ACTIVE' ? 'active' : 'inactive');
            const statusBadgeLabel = isRevoked ? 'QUYỀN BỊ THU HỒI' : (acc.status === 'ACTIVE' ? 'ĐANG HOẠT ĐỘNG' : 'TẠM NGỪNG');

            const sitesHtml = (acc.sites || []).map(site => `
                <span class="site-chip" title="${site.address}">📍 ${site.site_name}</span>
            `).join('');

            return `
                <div class="account-card" data-account-id="${acc.id}">
                    <div>
                        <div class="account-card-header">
                            <div class="account-name-group">
                                <h3 class="account-legal-name">${acc.legal_name}</h3>
                                <span class="account-code-tag">MST: ${acc.tax_code}</span>
                            </div>
                            <span class="status-badge ${statusBadgeClass}">${statusBadgeLabel}</span>
                        </div>

                        <div class="account-detail-rows">
                            <div class="detail-row">
                                <span class="detail-label">Lĩnh vực / Ngành:</span>
                                <span class="detail-val">${acc.industry}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Mã định danh ID:</span>
                                <span class="detail-val" style="font-family: var(--font-mono); font-size: 0.8rem;">${acc.id}</span>
                            </div>
                        </div>

                        <div class="sites-container">
                            <div class="sites-label">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                                    <circle cx="12" cy="10" r="3"></circle>
                                </svg>
                                <span>Địa điểm & Chi nhánh (${(acc.sites || []).length}):</span>
                            </div>
                            <div class="sites-chips-list">
                                ${sitesHtml || '<span style="font-size:0.75rem; color:var(--color-text-muted);">Không có địa điểm</span>'}
                            </div>
                        </div>
                    </div>

                    <div class="account-actions">
                        <button type="button" class="btn-view-briefing" data-action="view-briefing" data-account-id="${acc.id}">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                            </svg>
                            <span>Xem tóm tắt hồ sơ (Customer 360)</span>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        // Attach Card Click Events
        container.querySelectorAll('[data-action="view-briefing"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const accId = btn.getAttribute('data-account-id');
                this.handleViewBriefing(accId);
            });
        });
    },

    async handleViewBriefing(accountId) {
        const modalBackdrop = document.querySelector('#briefing-modal-backdrop');
        const modalTitle = document.querySelector('#modal-account-title');
        const modalBody = document.querySelector('#briefing-modal-body');

        modalTitle.textContent = 'Đang kiểm tra quyền và tải hồ sơ...';
        modalBody.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <p style="color: var(--color-text-secondary);">Đang gửi yêu cầu xác thực tới Authorization Service...</p>
            </div>
        `;
        modalBackdrop.classList.add('visible');

        // Sequence Diagram Orchestration
        const response = await ApiService.getAccountBriefing(accountId);

        // ALT BRANCH 1: [Permission revoked] -> HTTP 403 -> Display access revoked
        if (response.status === 403 || !response.ok) {
            const errData = response.data || {};
            modalTitle.textContent = 'Quyền truy cập bị từ chối';
            modalBody.innerHTML = `
                <!-- Sequence Diagram [Permission revoked] representation -->
                <div class="diagram-callout revoked">
                    <svg class="diagram-callout-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                    <div class="diagram-callout-content">
                        <span class="diagram-step-tag">QUY TRÌNH SƠ ĐỒ: [PERMISSION REVOKED] &rarr; HTTP 403</span>
                        <strong>Display access revoked</strong>
                        <span>${errData.message || 'Quyền truy cập hồ sơ khách hàng đã bị thu hồi hoặc bạn không nằm trong danh sách phân quyền (Account Scope).'}</span>
                    </div>
                </div>

                <div class="briefing-section">
                    <div class="briefing-section-title">Chi tiết kỹ thuật từ hệ thống</div>
                    <p class="briefing-section-text">
                        - <strong>Mã phản hồi:</strong> HTTP 403 Forbidden<br/>
                        - <strong>Dịch vụ từ chối:</strong> Authorization Service &rarr; Backend API<br/>
                        - <strong>Hành động thực hiện:</strong> Ghi nhật ký Audit Log (Action: BRIEFING_ACCESS_REVOKED_BLOCKED) và chặn hoàn toàn kết quả hiển thị thông tin nhạy cảm.
                    </p>
                </div>

                <div class="compliance-banner">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>Nguyên tắc hệ thống: No automatic write-back to CRM / ERP</span>
                </div>
            `;
            Toast.show('Cảnh báo HTTP 403: Quyền truy cập đã bị thu hồi.', 'error');
            return;
        }

        // ALT BRANCH 2: [Permission still valid] -> HTTP 200 -> Display Briefing and warnings
        const briefing = response.data?.data || {};
        modalTitle.textContent = `${briefing.legal_name || 'Hồ sơ khách hàng 360'}`;

        const citationsHtml = (briefing.citations || []).map(cit => `
            <div class="citation-card">
                <span class="citation-source-tag">${cit.source_type} SOURCE [Trích dẫn #${cit.citation_number}]</span>
                <p style="font-weight: 600; margin-bottom: 0.2rem;">${cit.claim_text}</p>
                <p style="font-size: 0.8rem; color: var(--color-text-muted);">Trích xuất: ${cit.source_excerpt || 'N/A'}</p>
            </div>
        `).join('');

        const warningsHtml = (briefing.sections?.risk_warnings || []).map(w => `
            <li style="margin-left: 1.25rem; font-size: 0.88rem; color: var(--color-warning-dark);">${w}</li>
        `).join('');

        modalBody.innerHTML = `
            <!-- Sequence Diagram [Permission still valid] representation -->
            <div class="diagram-callout valid">
                <svg class="diagram-callout-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <div class="diagram-callout-content">
                    <span class="diagram-step-tag">QUY TRÌNH SƠ ĐỒ: [PERMISSION STILL VALID] &rarr; HTTP 200</span>
                    <strong>Display Briefing and warnings</strong>
                    <span>Xác thực quyền thành công &bull; Đã lưu bản ghi Audit Log &bull; Trích xuất thông tin tươi mới.</span>
                </div>
            </div>

            <!-- Company Overview -->
            <div class="briefing-section">
                <div class="briefing-section-title">Tổng quan doanh nghiệp</div>
                <p class="briefing-section-text">${briefing.sections?.company_overview || 'Không có mô tả.'}</p>
            </div>

            <!-- Commercial Summary -->
            <div class="briefing-section">
                <div class="briefing-section-title">Tóm tắt thương mại & Đơn hàng</div>
                <p class="briefing-section-text">${briefing.sections?.commercial_summary || 'Không có dữ liệu thương mại.'}</p>
                <div style="margin-top: 0.5rem; font-size: 0.82rem; color: var(--color-text-muted);">
                    <strong>Trạng thái dữ liệu:</strong> ${briefing.freshness_status || 'Cập nhật thời gian thực'}
                </div>
            </div>

            <!-- Citations Section -->
            <div class="briefing-section">
                <div class="briefing-section-title">Bằng chứng & Trích dẫn nguồn (PDF & ERP Commercial)</div>
                <div class="citations-list">
                    ${citationsHtml || '<p style="font-size:0.85rem; color:var(--color-text-muted);">Chưa có trích dẫn nguồn được ghi nhận.</p>'}
                </div>
            </div>

            <!-- Warnings & Compliance -->
            <div class="briefing-section" style="border-left: 3px solid var(--color-warning);">
                <div class="briefing-section-title">Cảnh báo rủi ro & Xác thực</div>
                <ul style="display: flex; flex-direction: column; gap: 0.35rem; margin-top: 0.4rem;">
                    ${warningsHtml || '<li style="margin-left: 1.25rem; font-size: 0.88rem;">Không có cảnh báo rủi ro cao.</li>'}
                </ul>
            </div>

            <!-- Bottom constraint from Sequence Diagram -->
            <div class="compliance-banner">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <span>Tuân thủ kiến trúc: No automatic write-back to CRM / ERP</span>
            </div>
        `;

        Toast.show('Đã tải thành công hồ sơ tóm tắt khách hàng 360.', 'success');
    }
};
