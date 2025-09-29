// Mobile Touch Enhancement JavaScript
// Enhances mobile user experience with touch interactions

class MobileTouchEnhancer {
    constructor() {
        this.touchStartTime = 0;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.isScrolling = false;
        this.init();
    }

    init() {
        this.addTouchEnhancements();
        this.addMobileMenuToggle();
        this.addPullToRefresh();
        this.optimizeForMobile();
        this.addHapticFeedback();
    }

    addTouchEnhancements() {
        // Add touch feedback to buttons and cards
        const interactiveElements = document.querySelectorAll('button, .clinical-card, .tab-btn, .nav-tab');

        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                this.touchStartTime = Date.now();
                element.style.transform = 'scale(0.98)';
                element.style.transition = 'transform 0.1s ease';
            });

            element.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    element.style.transform = '';
                    element.style.transition = '';
                }, 100);
            });
        });
    }

    addMobileMenuToggle() {
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }
    }

    toggleMobileMenu() {
        // Create or toggle mobile navigation menu
        let mobileMenu = document.getElementById('mobileMenu');

        if (!mobileMenu) {
            mobileMenu = this.createMobileMenu();
        }

        const isVisible = mobileMenu.style.display !== 'none';
        mobileMenu.style.display = isVisible ? 'none' : 'block';

        // Animate menu appearance
        if (!isVisible) {
            mobileMenu.style.opacity = '0';
            mobileMenu.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                mobileMenu.style.opacity = '1';
                mobileMenu.style.transform = 'translateY(0)';
            }, 10);
        }
    }

    createMobileMenu() {
        const mobileMenu = document.createElement('div');
        mobileMenu.id = 'mobileMenu';
        mobileMenu.className = 'fixed top-16 left-0 right-0 bg-white shadow-lg z-50 border-b md:hidden';
        mobileMenu.style.display = 'none';
        mobileMenu.style.transition = 'all 0.3s ease';

        mobileMenu.innerHTML = `
            <div class="p-4 space-y-3">
                <div class="flex items-center justify-between py-2">
                    <span class="text-gray-700">Connection Status</span>
                    <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span class="text-sm text-gray-600">Online</span>
                    </div>
                </div>
                <div class="flex items-center justify-between py-2">
                    <span class="text-gray-700">Language</span>
                    <select class="border border-gray-300 rounded px-2 py-1 text-sm">
                        <option value="en">English</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                    </select>
                </div>
                <div class="border-t pt-3">
                    <button onclick="clearChat()" class="w-full text-left py-2 text-red-600 hover:bg-red-50 rounded px-2">
                        <i class="fas fa-trash-alt mr-2"></i>Clear Chat
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(mobileMenu);
        return mobileMenu;
    }

    addPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        let refreshThreshold = 80;
        let isRefreshing = false;

        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].pageY;
        });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && !isRefreshing) {
                pullDistance = e.touches[0].pageY - startY;

                if (pullDistance > 0 && pullDistance < refreshThreshold * 2) {
                    // Visual feedback for pull
                    this.showPullIndicator(pullDistance, refreshThreshold);
                }
            }
        });

        document.addEventListener('touchend', (e) => {
            if (pullDistance > refreshThreshold && !isRefreshing) {
                this.performRefresh();
            }
            this.hidePullIndicator();
            pullDistance = 0;
        });
    }

    showPullIndicator(distance, threshold) {
        let indicator = document.getElementById('pullIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pullIndicator';
            indicator.className = 'fixed top-0 left-0 right-0 bg-blue-500 text-white text-center py-2 z-50 transition-all duration-300';
            indicator.innerHTML = '<i class="fas fa-arrow-down animate-bounce mr-2"></i>Pull to refresh';
            document.body.appendChild(indicator);
        }

        const opacity = Math.min(distance / threshold, 1);
        indicator.style.opacity = opacity;
        indicator.style.transform = `translateY(${Math.min(distance / 4, 20)}px)`;

        if (distance > threshold) {
            indicator.innerHTML = '<i class="fas fa-sync-alt animate-spin mr-2"></i>Release to refresh';
            indicator.className = indicator.className.replace('bg-blue-500', 'bg-green-500');
        }
    }

    hidePullIndicator() {
        const indicator = document.getElementById('pullIndicator');
        if (indicator) {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-50px)';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }
    }

    performRefresh() {
        console.log('Refreshing application...');

        // Show refresh indicator
        let indicator = document.getElementById('pullIndicator');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-sync-alt animate-spin mr-2"></i>Refreshing...';
            indicator.className = 'fixed top-0 left-0 right-0 bg-blue-500 text-white text-center py-2 z-50';
        }

        // Simulate refresh action
        setTimeout(() => {
            this.hidePullIndicator();
            // Actual refresh logic would go here
            location.reload();
        }, 1500);
    }

    optimizeForMobile() {
        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (window.innerWidth < 768) {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                }
            });

            input.addEventListener('blur', () => {
                if (window.innerWidth < 768) {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, user-scalable=no');
                }
            });
        });

        // Optimize chat input for mobile
        const messageInput = document.getElementById('messageInput');
        if (messageInput && window.innerWidth < 768) {
            messageInput.style.fontSize = '16px'; // Prevents zoom on iOS
            messageInput.addEventListener('focus', () => {
                // Scroll input into view
                setTimeout(() => {
                    messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            });
        }
    }

    addHapticFeedback() {
        // Add haptic feedback for supported devices
        if ('vibrate' in navigator) {
            const hapticElements = document.querySelectorAll('button, .clinical-card');

            hapticElements.forEach(element => {
                element.addEventListener('touchstart', () => {
                    // Light haptic feedback
                    navigator.vibrate(10);
                });
            });
        }
    }
}

// Initialize mobile enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768) {
        new MobileTouchEnhancer();
    }
});

// Re-initialize on resize if switching to mobile
window.addEventListener('resize', () => {
    if (window.innerWidth <= 768 && !window.mobileTouchEnhancer) {
        window.mobileTouchEnhancer = new MobileTouchEnhancer();
    }
});
