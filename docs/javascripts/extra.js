/* Custom JavaScript for IVEXES documentation */

document.addEventListener('DOMContentLoaded', function() {
    // Add copy button functionality to code blocks
    addCopyButtons();
    
    // Add version warning for development docs
    addVersionWarning();
    
    // Enhance navigation
    enhanceNavigation();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
});

function addCopyButtons() {
    // Find all code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(function(codeBlock) {
        const pre = codeBlock.parentNode;
        
        // Skip if copy button already exists
        if (pre.querySelector('.copy-button')) return;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '📋';
        copyButton.title = 'Copy to clipboard';
        
        // Style the button
        copyButton.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: var(--md-default-bg-color);
            border: 1px solid var(--md-default-fg-color--lighter);
            border-radius: 0.2rem;
            padding: 0.2rem 0.4rem;
            cursor: pointer;
            font-size: 0.8rem;
            opacity: 0.7;
            transition: opacity 0.2s;
        `;
        
        // Make pre relative for absolute positioning
        pre.style.position = 'relative';
        
        // Add click handler
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent).then(function() {
                copyButton.innerHTML = '✅';
                setTimeout(function() {
                    copyButton.innerHTML = '📋';
                }, 2000);
            });
        });
        
        // Show/hide on hover
        pre.addEventListener('mouseenter', function() {
            copyButton.style.opacity = '1';
        });
        
        pre.addEventListener('mouseleave', function() {
            copyButton.style.opacity = '0.7';
        });
        
        pre.appendChild(copyButton);
    });
}

function addVersionWarning() {
    // Check if this is a development version
    const currentUrl = window.location.href;
    const isDev = currentUrl.includes('localhost') || currentUrl.includes('127.0.0.1');
    
    if (isDev) {
        const warning = document.createElement('div');
        warning.className = 'version-warning';
        warning.innerHTML = `
            <strong>⚠️ Development Documentation</strong><br>
            You are viewing development documentation. 
            For the latest stable version, visit the 
            <a href="https://letsdrinksometea.github.io/ivexes/">official documentation</a>.
        `;
        
        const main = document.querySelector('main .md-content');
        if (main) {
            main.insertBefore(warning, main.firstChild);
        }
    }
}

function enhanceNavigation() {
    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });
    
    // Highlight current section in navigation
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                if (id) {
                    // Remove previous active states
                    document.querySelectorAll('.md-nav__link--active').forEach(function(el) {
                        el.classList.remove('md-nav__link--active');
                    });
                    
                    // Add active state to current section
                    const navLink = document.querySelector(`a[href="#${id}"]`);
                    if (navLink) {
                        navLink.classList.add('md-nav__link--active');
                    }
                }
            }
        });
    }, {
        rootMargin: '-20% 0px -80% 0px'
    });
    
    // Observe all headings
    document.querySelectorAll('h2[id], h3[id], h4[id]').forEach(function(heading) {
        observer.observe(heading);
    });
}

function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.blur();
            }
        }
    });
}

// Add utility functions for API documentation
window.ivexesUtils = {
    // Toggle code signature visibility
    toggleSignature: function(element) {
        const signature = element.nextElementSibling;
        if (signature && signature.classList.contains('doc-signature')) {
            signature.style.display = signature.style.display === 'none' ? 'block' : 'none';
        }
    },
    
    // Copy API reference link
    copyApiLink: function(element) {
        const link = window.location.origin + window.location.pathname + '#' + element.id;
        navigator.clipboard.writeText(link).then(function() {
            console.log('API link copied:', link);
        });
    }
};

// Analytics (if needed)
if (window.gtag) {
    // Track documentation usage
    gtag('event', 'page_view', {
        page_title: document.title,
        page_location: window.location.href
    });
}