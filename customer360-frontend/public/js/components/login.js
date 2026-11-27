/**
 * Login Component
 * Handles static UI, client-side input validation, password toggle, and navigation.
 */
import { ApiService } from '../services/api.js';
import { Toast } from './toast.js';

export const LoginComponent = {
    render(container, onLoginSuccess) {
        container.innerHTML = `
            <div class="login-view-container">
                <div class="login-card">
                    <div class="login-header-group">
                        <span class="login-badge-tag">CUSTOMER 360 ENTERPRISE</span>
                        <h1 class="login-title">Đăng nhập Hệ thống</h1>
                        <p class="login-subtitle">Truy cập hồ sơ khách hàng 360 & dữ liệu thương mại</p>
                    </div>

                    <!-- Error Alert Banner -->
                    <div id="login-error-banner" class="login-error-banner">
                        <svg class="login-error-icon" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                        <span id="login-error-text">Vui lòng điền đầy đủ thông tin đăng nhập.</span>
                    </div>

                    <form id="login-form" novalidate>
                        <!-- Username / Email Field -->
                        <div class="form-group">
                            <label class="form-label" for="login-username">Email</label>
                            <div class="input-wrapper">
                                <span class="input-icon-left">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                        <circle cx="12" cy="7" r="4"></circle>
                                    </svg>
                                </span>
                                <input
                                    type="text"
                                    id="login-username"
                                    class="form-control"
                                    placeholder="username@gmail.com"
                                    autocomplete="username"
                                />
                            </div>
                            <span id="username-error-text" class="field-error-text">Tên tài khoản hoặc email không được để trống.</span>
                        </div>

                        <!-- Password Field -->
                        <div class="form-group">
                            <label class="form-label" for="login-password">Mật khẩu</label>
                            <div class="input-wrapper">
                                <span class="input-icon-left">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                    </svg>
                                </span>
                                <input
                                    type="password"
                                    id="login-password"
                                    class="form-control"
                                    placeholder="••••••••••••"
                                    autocomplete="current-password"
                                />
                                <button type="button" id="btn-toggle-password" class="btn-toggle-password" title="Hiển thị/ẩn mật khẩu">
                                    <!-- Eye Icon (Show) -->
                                    <svg id="eye-icon-show" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                    <!-- Eye Off Icon (Hide) -->
                                    <svg id="eye-icon-hide" style="display: none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                        <line x1="1" y1="1" x2="23" y2="23"></line>
                                    </svg>
                                </button>
                            </div>
                            <span id="password-error-text" class="field-error-text">Mật khẩu không được để trống.</span>
                        </div>

                        <!-- Submit Button -->
                        <button type="submit" id="btn-submit-login" class="btn-submit-login">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                                <polyline points="10 17 15 12 10 7"></polyline>
                                <line x1="15" y1="12" x2="3" y2="12"></line>
                            </svg>
                            <span>Đăng nhập</span>
                        </button>
                    </form>

                </div>
            </div>
        `;

        this.attachEvents(container, onLoginSuccess);
    },

    attachEvents(container, onLoginSuccess) {
        const form = container.querySelector('#login-form');
        const usernameInput = container.querySelector('#login-username');
        const passwordInput = container.querySelector('#login-password');
        const togglePasswordBtn = container.querySelector('#btn-toggle-password');
        const eyeShow = container.querySelector('#eye-icon-show');
        const eyeHide = container.querySelector('#eye-icon-hide');
        const bannerError = container.querySelector('#login-error-banner');
        const bannerErrorText = container.querySelector('#login-error-text');
        const usernameError = container.querySelector('#username-error-text');
        const passwordError = container.querySelector('#password-error-text');

        // Toggle Password Visibility
        togglePasswordBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            eyeShow.style.display = isPassword ? 'none' : 'block';
            eyeHide.style.display = isPassword ? 'block' : 'none';
        });

        // Real-time error clearance on input
        usernameInput.addEventListener('input', () => {
            if (usernameInput.value.trim()) {
                usernameInput.classList.remove('input-error');
                usernameError.classList.remove('visible');
            }
        });

        passwordInput.addEventListener('input', () => {
            if (passwordInput.value.trim()) {
                passwordInput.classList.remove('input-error');
                passwordError.classList.remove('visible');
            }
        });

        // Form Submit Handler
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            let hasError = false;

            // Interface-level Validation Check
            if (!username) {
                usernameInput.classList.add('input-error');
                usernameError.classList.add('visible');
                hasError = true;
            } else {
                usernameInput.classList.remove('input-error');
                usernameError.classList.remove('visible');
            }

            if (!password) {
                passwordInput.classList.add('input-error');
                passwordError.classList.add('visible');
                hasError = true;
            } else {
                passwordInput.classList.remove('input-error');
                passwordError.classList.remove('visible');
            }

            if (hasError) {
                bannerErrorText.textContent = 'Thông báo: Vui lòng điền đầy đủ tên tài khoản/email và mật khẩu trước khi đăng nhập.';
                bannerError.classList.add('visible');
                return;
            }

            bannerError.classList.remove('visible');

            // Authentication must be verified by the backend.
            const res = await ApiService.login(username, password);
            if (res.success && res.access_token && res.user) {
                Toast.show('Đăng nhập thành công! Đang chuyển đến màn hình tra cứu...', 'success');
                setTimeout(() => {
                    onLoginSuccess(res.user, res.access_token);
                }, 500);
            } else {
                bannerErrorText.textContent = res.message || 'Tài khoản hoặc mật khẩu không chính xác.';
                bannerError.classList.add('visible');
                Toast.show(res.message || 'Lỗi đăng nhập', 'error');
            }
        });
    },

    clearErrors({ usernameInput, passwordInput, bannerError, usernameError, passwordError }) {
        usernameInput.classList.remove('input-error');
        passwordInput.classList.remove('input-error');
        bannerError.classList.remove('visible');
        usernameError.classList.remove('visible');
        passwordError.classList.remove('visible');
    }
};
