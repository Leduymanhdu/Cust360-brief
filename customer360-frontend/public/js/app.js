/**
 * Main Application Router & State Manager
 */
import { LoginComponent } from './components/login.js';
import { SearchComponent } from './components/search.js';
import { Toast } from './components/toast.js';

class App {
    constructor() {
        this.currentUser = {
            id: 'usr-002',
            email: 'sales@cust360.vn',
            full_name: 'Trần Thị Thu Thảo',
            role: 'SALES',
            is_active: true
        };
        this.currentScreen = 'login'; // 'login' or 'search'
    }

    init() {
        // Handle URL hash changes
        window.addEventListener('hashchange', () => this.handleRouting());

        // Initial route
        const initialHash = window.location.hash.replace('#', '');
        if (initialHash === 'search') {
            this.currentScreen = 'search';
        } else {
            this.currentScreen = 'login';
        }

        this.render();
    }

    handleRouting() {
        const hash = window.location.hash.replace('#', '');
        if (hash === 'search') {
            this.currentScreen = 'search';
        } else {
            this.currentScreen = 'login';
        }
        this.render();
    }

    navigateTo(screen) {
        this.currentScreen = screen;
        window.location.hash = screen;
        this.render();
    }

    render() {
        this.renderHeader();
        this.renderMainContent();
    }

    renderHeader() {
        const headerContainer = document.getElementById('app-header');
        if (!headerContainer) return;

        const isSearchScreen = this.currentScreen === 'search';

        headerContainer.innerHTML = `
            <div class="brand-wrapper">
                <div class="brand-logo-icon">360</div>
                <div class="brand-text-group">
                    <span class="brand-name">Customer 360</span>
                    <span class="brand-subtitle">Enterprise Briefing & Account Scope</span>
                </div>
            </div>

            <div class="header-right">
                ${isSearchScreen ? `
                    <div class="user-badge">
                        <div class="user-avatar-circle">
                            ${(this.currentUser.full_name || 'U').charAt(0)}
                        </div>
                        <span class="user-info-text">${this.currentUser.full_name || this.currentUser.email}</span>
                        <span class="user-role-tag">${this.currentUser.role || 'SALES'}</span>
                    </div>

                    <button type="button" id="header-btn-logout" class="btn-logout" title="Đăng xuất khỏi hệ thống">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                            <polyline points="16 17 21 12 16 7"></polyline>
                            <line x1="21" y1="12" x2="9" y2="12"></line>
                        </svg>
                        <span>Đăng xuất</span>
                    </button>
                ` : `
                    <div style="font-size: 0.85rem; color: var(--color-text-secondary); font-weight: 500;">
                        Phiên bản 1.0 (Giai đoạn SDS M7-M8)
                    </div>
                `}
            </div>
        `;

        if (isSearchScreen) {
            const logoutBtn = headerContainer.querySelector('#header-btn-logout');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => {
                    Toast.show('Đã đăng xuất khỏi tài khoản.', 'info');
                    this.navigateTo('login');
                });
            }
        }
    }

    renderMainContent() {
        const mainContainer = document.getElementById('app-content');
        if (!mainContainer) return;

        if (this.currentScreen === 'login') {
            LoginComponent.render(
                mainContainer,
                (user) => {
                    if (user) this.currentUser = user;
                    this.navigateTo('search');
                },
                () => {
                    this.navigateTo('search');
                }
            );
        } else {
            SearchComponent.render(
                mainContainer,
                this.currentUser,
                () => {
                    this.navigateTo('login');
                }
            );
        }
    }
}

// Initialize Application once DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
