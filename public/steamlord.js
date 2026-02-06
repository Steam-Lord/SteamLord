// SteamLord button injection (standalone plugin)
(function () {
    'use strict';

    // Forward logs to Millennium backend so they appear in the dev console
    function backendLog(message) {
        try {
            if (typeof Millennium !== 'undefined' && typeof Millennium.callServerMethod === 'function') {
                Millennium.callServerMethod('steamlord', 'Logger.log', { message: String(message) });
            }
        } catch (err) {
            if (typeof console !== 'undefined' && console.warn) {
                console.warn('[SteamLord] backendLog failed', err);
            }
        }
    }

    backendLog('SteamLord script loaded');

    // --- INJECT CUSTOM STYLES FOR UI ENHANCEMENTS ---
    function injectCustomStyles() {
        if (document.getElementById('steamlord-custom-css')) return;
        const style = document.createElement('style');
        style.id = 'steamlord-custom-css';
        style.textContent = `
            /* Animations */
            @keyframes steamlordFadeIn {
                from { opacity: 0; transform: scale(0.95) translateY(10px); }
                to { opacity: 1; transform: scale(1) translateY(0); }
            }
            @keyframes steamlordBorderRotate {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            @keyframes steamlordPulse {
                0% { box-shadow: 0 0 0 0 rgba(102, 192, 244, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(102, 192, 244, 0); }
                100% { box-shadow: 0 0 0 0 rgba(102, 192, 244, 0); }
            }

            /* Glassmorphism Modal Container */
            .steamlord-glass-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(4px);
                z-index: 99999;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: steamlordFadeIn 0.2s ease-out;
            }

            /* The Modal Box */
            .steamlord-glass-modal {
                position: relative;
                background: linear-gradient(145deg, rgba(15, 35, 70, 0.95), rgba(10, 25, 55, 0.98));
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border-radius: 20px;
                border: 2px solid rgba(30, 120, 220, 0.4);
                padding: 0;
                box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(30, 100, 200, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
                min-width: 400px;
                max-width: 600px;
                overflow: hidden;
                animation: steamlordFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }

            /* Animated Gradient Border Background */
            .steamlord-glass-modal::before {
                content: "";
                position: absolute;
                inset: 0;
                border-radius: 20px;
                padding: 2px;
                background: linear-gradient(45deg, rgba(30, 120, 220, 0.5), rgba(30, 150, 255, 0.3), rgba(20, 80, 160, 0.5));
                background-size: 300% 300%;
                animation: steamlordBorderRotate 4s ease infinite;
                -webkit-mask: 
                   linear-gradient(#fff 0 0) content-box, 
                   linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
                pointer-events: none;
                opacity: 0.4;
            }

            /* Inner Content */
            .steamlord-modal-content {
                background: transparent;
                border-radius: 18px;
                padding: 30px;
                display: flex;
                flex-direction: column;
                gap: 20px;
                position: relative;
                z-index: 1;
            }

            /* Typography */
            .steamlord-title {
                font-size: 24px;
                font-weight: 700;
                color: #fff;
                text-shadow: 0 0 30px rgba(30, 150, 255, 0.5);
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .steamlord-title i {
                color: #4da6ff;
            }
            .steamlord-text {
                font-size: 14px;
                line-height: 1.7;
                color: #7fc4ff;
            }

            /* Buttons */
            .steamlord-btn-row {
                display: flex;
                gap: 15px;
                justify-content: flex-end;
                margin-top: 15px;
            }

            .steamlord-btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                text-decoration: none;
                color: #fff !important;
                background: linear-gradient(135deg, rgba(30, 100, 200, 0.3), rgba(20, 80, 160, 0.2));
                border: 2px solid rgba(30, 120, 220, 0.4);
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }
            
            .steamlord-btn span { position: relative; z-index: 2; }

            .steamlord-btn::after {
                content: '';
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(rgba(255,255,255,0.1), rgba(255,255,255,0));
                opacity: 0;
                transition: opacity 0.2s;
            }

            .steamlord-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(30, 100, 200, 0.4);
                border-color: rgba(30, 150, 255, 0.8);
                color: #fff;
            }
            .steamlord-btn:hover::after { opacity: 1; }
            .steamlord-btn:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }

            /* Button Variants */
            .steamlord-btn.primary {
                background: linear-gradient(135deg, #1e90ff 0%, #0066cc 50%, #1e78d0 100%);
                border-color: rgba(30, 150, 255, 0.6);
                box-shadow: 0 6px 20px rgba(30, 100, 200, 0.4);
            }
            .steamlord-btn.success {
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                border-color: rgba(34, 197, 94, 0.6);
                box-shadow: 0 6px 20px rgba(34, 197, 94, 0.3);
            }
            .steamlord-btn.danger {
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                border-color: rgba(239, 68, 68, 0.6);
                box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
            }

            /* Injected Buttons on Store Page */
            .steamlord-injected-btn {
                transition: all 0.2s ease;
                border: 1px solid transparent;
            }
            .steamlord-injected-btn:hover {
                transform: scale(1.05);
                filter: brightness(1.2);
                box-shadow: 0 0 15px rgba(102, 192, 244, 0.4);
                border-color: rgba(102, 192, 244, 0.5);
            }
                box-shadow: 0 0 15px rgba(102, 192, 244, 0.4);
                border-color: rgba(102, 192, 244, 0.5);
            }

            /* Restart Banner */
            .steamlord-restart-banner {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 5px 15px;
                background: linear-gradient(90deg, rgba(102, 192, 244, 0.1), rgba(27, 40, 56, 0.8));
                border: 1px solid rgba(102, 192, 244, 0.3);
                border-radius: 4px;
                height: 32px; /* Match typical Steam header button height */
                margin-right: 10px;
                animation: steamlordFadeIn 0.5s ease-out;
            }
            .steamlord-restart-text {
                color: #66c0f4;
                font-size: 12px;
                font-weight: 600;
                white-space: nowrap;
                text-shadow: 0 0 5px rgba(102, 192, 244, 0.3);
            }
            .steamlord-restart-btn-small {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
                border-radius: 4px;
                background: linear-gradient(135deg, #66c0f4 0%, #3b8dbd 100%);
                color: #fff;
                cursor: pointer;
                transition: all 0.3s ease;
                overflow: hidden;
                position: relative;
            }
            .steamlord-restart-btn-small i {
                font-size: 14px;
                transition: transform 0.3s ease;
            }
            .steamlord-restart-btn-small span {
                opacity: 0;
                width: 0;
                white-space: nowrap;
                margin-left: 0;
                transition: all 0.3s ease;
                font-size: 12px;
                font-weight: bold;
            }
            .steamlord-restart-btn-small:hover {
                width: 120px;
                box-shadow: 0 0 10px rgba(102, 192, 244, 0.5);
            }
            .steamlord-restart-btn-small:hover i {
                transform: rotate(180deg);
            }
            .steamlord-restart-btn-small:hover span {
                opacity: 1;
                width: auto;
                margin-left: 8px;
            }

            /* Animated Gradient Background */
            @keyframes steamlord-gradient-anim {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Neon Border Animation */
            @keyframes steamlord-neon-border {
                0% { box-shadow: 0 0 5px #06bfff, 0 0 10px #06bfff, inset 0 0 5px #06bfff; border-color: #06bfff; }
                50% { box-shadow: 0 0 10px #2d73ff, 0 0 20px #2d73ff, inset 0 0 10px #2d73ff; border-color: #2d73ff; }
                100% { box-shadow: 0 0 5px #06bfff, 0 0 10px #06bfff, inset 0 0 5px #06bfff; border-color: #06bfff; }
            }

            .steamlord-floating-banner {
                position: fixed;
                bottom: 40px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 12px 24px;
                border-radius: 8px;
                
                /* Animated Gradient Background */
                background: linear-gradient(270deg, rgba(6,191,255,0.9), rgba(45,115,255,0.9), rgba(6,191,255,0.9));
                background-size: 200% 200%;
                animation: steamlord-gradient-anim 3s ease infinite;

                /* Neon Border Effect */
                border: 2px solid #06bfff;
                animation: steamlord-gradient-anim 3s ease infinite, steamlord-neon-border 2s ease-in-out infinite alternate;
                
                backdrop-filter: blur(5px);
                color: #fff;
                font-family: "Motiva Sans", Sans-serif;
                font-weight: 500;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                overflow: hidden;
                min-width: 300px;
                text-align: center;
            }
            
            .steamlord-floating-banner:hover {
                transform: translateX(-50%) scale(1.05);
                box-shadow: 0 0 20px rgba(6,191,255,0.6), 0 0 40px rgba(45,115,255,0.4);
            }

            /* Minimized Sidebar Styles */
            @keyframes steamlordCrownGlow {
                0%, 100% { filter: drop-shadow(0 0 5px rgba(30, 100, 200, 0.3)); }
                50% { filter: drop-shadow(0 0 10px rgba(30, 150, 255, 0.5)); }
            }

            @keyframes steamlordSlideIn {
                from { transform: translateY(-50%) translateX(100%); opacity: 0; }
                to { transform: translateY(-50%) translateX(0); opacity: 1; }
            }

            @keyframes steamlordPulseBlue {
                0%, 100% { box-shadow: -5px 0 20px rgba(0, 0, 0, 0.5), 0 0 30px rgba(30, 100, 200, 0.3); }
                50% { box-shadow: -8px 0 30px rgba(0, 0, 0, 0.6), 0 0 50px rgba(30, 150, 255, 0.5); }
            }

            .steamlord-minimized-sidebar {
                position: fixed;
                top: 50%;
                right: 0;
                transform: translateY(-50%);
                z-index: 999998;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 15px 12px;
                background: linear-gradient(180deg, rgba(15, 30, 60, 0.98), rgba(10, 25, 50, 0.99));
                border: 2px solid rgba(30, 120, 220, 0.5);
                border-right: none;
                border-radius: 16px 0 0 16px;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                animation: steamlordSlideIn 0.5s ease-out, steamlordPulseBlue 3s ease-in-out infinite;
            }

            .steamlord-minimized-sidebar:hover {
                padding: 18px 15px;
                border-color: rgba(30, 150, 255, 0.8);
                background: linear-gradient(180deg, rgba(20, 40, 80, 0.98), rgba(15, 35, 70, 0.99));
            }

            .steamlord-minimized-sidebar img {
                width: 55px;
                height: auto;
                transition: transform 0.3s ease;
                animation: steamlordCrownGlow 2s ease-in-out infinite;
            }

            .steamlord-minimized-sidebar:hover img {
                transform: scale(1.15) rotate(5deg);
            }

            .steamlord-minimized-sidebar .sidebar-text {
                writing-mode: vertical-rl;
                text-orientation: mixed;
                color: #4da6ff;
                font-size: 11px;
                font-weight: 700;
                margin-top: 10px;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 0 0 15px rgba(77, 166, 255, 0.7);
            }

            /* Settings Sidebar (Left) */
            .steamlord-settings-sidebar {
                position: fixed;
                top: 50%;
                left: 0;
                transform: translateY(-50%);
                z-index: 999998;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 15px 12px;
                background: linear-gradient(180deg, rgba(15, 30, 60, 0.98), rgba(10, 25, 50, 0.99));
                border: 2px solid rgba(30, 120, 220, 0.5);
                border-left: none;
                border-radius: 0 16px 16px 0;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                animation: steamlordSlideIn 0.5s ease-out;
            }

            .steamlord-settings-sidebar:hover {
                padding: 18px 15px;
                border-color: rgba(30, 150, 255, 0.8);
                background: linear-gradient(180deg, rgba(20, 40, 80, 0.98), rgba(15, 35, 70, 0.99));
            }

            /* Settings Tabs */
            .steamlord-tabs-container {
                display: flex;
                gap: 10px;
                margin-bottom: 25px;
                background: rgba(0, 0, 0, 0.2);
                padding: 5px;
                border-radius: 12px;
            }

            .steamlord-tab-btn {
                flex: 1;
                padding: 10px;
                border: none;
                border-radius: 8px;
                background: transparent;
                color: #fff;
                font-weight: 600;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
            }

            .steamlord-tab-btn:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .steamlord-tab-btn.active {
                background: #fff;
                color: #1a2b4b; /* Dark Blue from theme */
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }

            .steamlord-tab-content {
                display: none;
                animation: steamlordFadeIn 0.3s ease-out;
                /* background and border removed for flat look */
                padding: 10px 0;
                min-height: 200px;
            }

            .steamlord-tab-content.active {
                display: block;
            }

            .steamlord-settings-sidebar i {
                font-size: 24px;
                color: #66c0f4;
                filter: drop-shadow(0 0 5px rgba(30, 100, 200, 0.3));
                transition: transform 0.3s ease;
            }

            .steamlord-settings-sidebar:hover i {
                transform: rotate(90deg) scale(1.1);
                filter: drop-shadow(0 0 10px rgba(30, 150, 255, 0.5));
            }

            /* Minimize button in popup */
            .steamlord-minimize-btn {
                position: absolute;
                top: 15px;
                right: 15px;
                width: 36px;
                height: 36px;
                border-radius: 8px;
                background: linear-gradient(135deg, rgba(30, 100, 200, 0.2), rgba(20, 80, 160, 0.1));
                border: 1px solid rgba(30, 120, 220, 0.4);
                color: #4da6ff;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                z-index: 10;
            }

            .steamlord-minimize-btn:hover {
                background: linear-gradient(135deg, rgba(30, 150, 255, 0.4), rgba(20, 100, 200, 0.3));
                border-color: rgba(30, 150, 255, 0.8);
                color: #fff;
                transform: scale(1.1);
                box-shadow: 0 0 20px rgba(30, 150, 255, 0.5);
            }

            /* Warning message style */
            .steamlord-warning-msg {
                background: linear-gradient(135deg, rgba(30, 100, 200, 0.2), rgba(20, 80, 160, 0.15));
                border: 1px solid rgba(30, 120, 220, 0.5);
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                animation: steamlordFadeIn 0.5s ease-out;
            }

            .steamlord-warning-msg i {
                color: #4da6ff;
                font-size: 20px;
            }

            .steamlord-warning-msg span {
                color: #7fc4ff;
                font-size: 14px;
                font-weight: 600;
            }

            /* Crown Logo Animation for Popup */
            @keyframes steamlordCrownFloat {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-8px); }
            }

            .steamlord-crown-logo {
                width: 100px;
                height: auto;
                margin-bottom: 15px;
                animation: steamlordCrownFloat 3s ease-in-out infinite;
            }

            /* Steam-like Toast Notification */
            @keyframes steamlordToastSlideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }

            .steamlord-toast {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 320px;
                background: linear-gradient(145deg, rgba(15, 30, 60, 0.95), rgba(10, 25, 50, 0.98));
                border: 1px solid rgba(102, 192, 244, 0.3);
                border-left: 4px solid #66c0f4;
                border-radius: 6px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.6), 0 0 15px rgba(102, 192, 244, 0.2);
                display: flex;
                flex-direction: column;
                padding: 0;
                gap: 0;
                z-index: 9999999;
                animation: steamlordToastSlideIn 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
                transition: transform 0.3s ease, margin-bottom 0.3s ease, bottom 0.3s ease;
                overflow: hidden;
            }

            .steamlord-toast:hover {
                transform: translateX(-5px);
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(102, 192, 244, 0.3);
                border-color: rgba(102, 192, 244, 0.6);
            }

            .steamlord-toast-body {
                display: flex;
                padding: 12px;
                gap: 12px;
                align-items: center;
            }

            .steamlord-toast-icon {
                width: 55px;
                height: 55px;
                flex-shrink: 0;
                background-size: cover;
                background-position: center;
                border-radius: 6px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .steamlord-toast-icon.fallback {
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, rgba(102, 192, 244, 0.1), rgba(102, 192, 244, 0.05));
                color: #66c0f4;
                font-size: 26px;
            }

            .steamlord-toast-content {
                flex: 1;
                overflow: hidden;
            }

            .steamlord-toast-title {
                color: #fff;
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 2px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-shadow: 0 0 10px rgba(102, 192, 244, 0.3);
            }

            /* Profile Tab Styles */
            .profile-key-card {
                background: linear-gradient(135deg, rgba(30, 100, 200, 0.2), rgba(20, 80, 160, 0.1));
                border: 1px solid rgba(30, 150, 255, 0.3);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            }
            .key-label {
                color: #66c0f4;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 8px;
                font-weight: 600;
            }
            .key-value {
                color: #fff;
                font-family: 'Consolas', monospace;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 1px;
                text-shadow: 0 0 10px rgba(30, 150, 255, 0.5);
            }
            
            .profile-stats-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 15px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-3px);
                background: rgba(255, 255, 255, 0.06);
                border-color: rgba(255, 255, 255, 0.1);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .stat-card i {
                font-size: 20px;
                color: #66c0f4;
                margin-bottom: 4px;
            }
            .stat-value {
                font-size: 18px;
                font-weight: 700;
                color: #fff;
            }
            .stat-label {
                font-size: 11px;
                color: #8b9db5;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            /* Theme Grid */
            .theme-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 10px;
            }
            .theme-card {
                background: rgba(15, 23, 42, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            .theme-card:hover {
                transform: translateY(-2px);
                background: rgba(30, 41, 59, 0.8);
            }
            .theme-card.active {
                border-color: var(--primary-color);
                box-shadow: 0 0 15px var(--primary-shadow);
            }
            .theme-preview {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin: 0 auto 10px auto;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            .theme-name {
                font-size: 13px;
                color: #cbd5e1;
                font-weight: 600;
            }
            
            /* Social Grid */
            .social-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 10px;
            }
            .social-card {
                background: rgba(15, 23, 42, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px 10px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
            }
            .social-card:hover {
                transform: translateY(-3px);
                background: rgba(30, 41, 59, 0.8);
                border-color: var(--primary-color);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .social-icon {
                font-size: 24px;
                transition: all 0.3s ease;
            }
            .social-card:hover .social-icon {
                transform: scale(1.1);
            }
            .social-label {
                font-size: 13px;
                color: #cbd5e1;
                font-weight: 600;
            }

            .steamlord-toast-subtitle {
                color: #66c0f4;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }

            .steamlord-toast-msg {
                color: #c6d4df;
                font-size: 12px;
                line-height: 1.3;
            }

            .steamlord-toast-actions {
                display: flex;
                border-top: 1px solid rgba(255,255,255,0.05);
                background: rgba(0,0,0,0.1);
            }

            .steamlord-toast-btn {
                flex: 1;
                border: none;
                background: transparent;
                color: #b8b6b4;
                padding: 8px 0;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
            }

            .steamlord-toast-btn:hover {
                background: rgba(255,255,255,0.05);
                color: #fff;
            }

            .steamlord-toast-btn.primary {
                color: #66c0f4;
                border-right: 1px solid rgba(255,255,255,0.05);
            }
            
            .steamlord-toast-btn.primary:hover {
                background: linear-gradient(90deg, rgba(102, 192, 244, 0.1), rgba(102, 192, 244, 0.05));
                color: #92d1f7;
            }

            /* Success & Warning Messages - Premium Design */
            .steamlord-success-container {
                text-align: center;
                padding: 15px 10px;
            }
            .steamlord-success-title {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                color: #4ade80;
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 18px;
                text-shadow: 0 0 20px rgba(74, 222, 128, 0.4);
            }
            .steamlord-success-title i {
                font-size: 22px;
                filter: drop-shadow(0 0 8px rgba(74, 222, 128, 0.6));
                animation: successPulse 2s ease-in-out infinite;
            }
            @keyframes successPulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
            }
            .steamlord-warning-note {
                background: transparent;
                padding: 0 20px 5px 20px;
                text-align: center;
                font-size: 13px;
                color: #8b9db5;
                line-height: 1.6;
            }
            .steamlord-warning-note i {
                color: #66c0f4;
                margin-right: 6px;
                font-size: 13px;
            }
            .steamlord-warning-note span {
                color: #8b9db5;
            }
            
            /* Bypass Game Info - Icon Columns Style */
            .steamlord-bypass-success {
                text-align: center;
                padding: 5px 0;
            }
            .steamlord-bypass-success .info-columns {
                display: flex;
                justify-content: center;
                gap: 50px;
                margin-top: 15px;
            }
            .steamlord-bypass-success .info-col {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }
            .steamlord-bypass-success .info-col i {
                font-size: 32px;
                color: #66c0f4;
                filter: drop-shadow(0 0 12px rgba(102, 192, 244, 0.5));
            }
            .steamlord-bypass-success .info-col .label {
                color: #94a3b8;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 500;
            }
            .steamlord-bypass-success .info-col .value {
                color: #fff;
                font-size: 14px;
                font-weight: 600;
            }
        `;
        document.head.appendChild(style);
    }

    const TRANSLATION_PLACEHOLDER = 'translation missing';



    function ensureFontAwesome() {
        if (document.getElementById('steamlord-fontawesome')) return;
        try {
            const link = document.createElement('link');
            link.id = 'steamlord-fontawesome';
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css';
            link.integrity = 'sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==';
            link.crossOrigin = 'anonymous';
            link.referrerPolicy = 'no-referrer';
            document.head.appendChild(link);
        } catch (err) { backendLog('SteamLord: Font Awesome injection failed: ' + err); }
    }

    function ensureTranslationsLoaded(forceRefresh, preferredLanguage) {
        return Promise.resolve({ language: 'en', locales: [], strings: {}, ready: true });
    }

    function translateText(key, fallback) {
        if (!key) return typeof fallback !== 'undefined' ? fallback : '';
        try {
            const store = window.__SteamLordI18n;
            if (store && store.strings && Object.prototype.hasOwnProperty.call(store.strings, key)) {
                const value = store.strings[key];
                if (typeof value === 'string') {
                    const trimmed = value.trim();
                    if (trimmed && trimmed.toLowerCase() !== TRANSLATION_PLACEHOLDER) {
                        return value;
                    }
                }
            }
        } catch (_) { }
        return typeof fallback !== 'undefined' ? fallback : key;
    }

    function t(key, fallback) { return typeof fallback !== 'undefined' ? fallback : key; }
    function lt(text) { return text; }

    ensureTranslationsLoaded(false);
    injectCustomStyles();

    // ═══════════════════════════════════════════════════════════════════════════
    // LICENSE SYSTEM
    // ═══════════════════════════════════════════════════════════════════════════

    let _isLicenseValid = false;
    let _licenseCheckDone = false;
    let _sessionInfo = null;
    let _isPopupMinimized = false;

    function isLicenseValid() {
        return _isLicenseValid;
    }

    function checkLicenseOnStartup() {
        if (typeof Millennium === 'undefined') {
            _licenseCheckDone = true;
            return Promise.resolve(false);
        }

        return Millennium.callServerMethod('steamlord', 'GetSessionInfo', { contentScriptQuery: '' })
            .then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && payload.isLoggedIn) {
                    // Verify session with server
                    return Millennium.callServerMethod('steamlord', 'VerifyLicense', { contentScriptQuery: '' })
                        .then(function (verifyRes) {
                            const verifyPayload = typeof verifyRes === 'string' ? JSON.parse(verifyRes) : verifyRes;
                            if (verifyPayload && verifyPayload.success && verifyPayload.valid) {
                                _isLicenseValid = true;
                                _sessionInfo = {
                                    email: verifyPayload.email,
                                    expiresAt: verifyPayload.expiresAt,
                                    isLifetime: verifyPayload.isLifetime
                                };
                                backendLog('SteamLord: License verified for ' + verifyPayload.email);
                                return true;
                            } else {
                                _isLicenseValid = false;
                                backendLog('SteamLord: License verification failed: ' + (verifyPayload.error || 'Unknown'));
                                return false;
                            }
                        });
                } else {
                    _isLicenseValid = false;
                    return false;
                }
            })
            .catch(function (err) {
                backendLog('SteamLord: License check error: ' + err);
                _isLicenseValid = false;
                return false;
            })
            .finally(function () {
                _licenseCheckDone = true;
            });
    }

    function showMinimizedSidebar() {
        // Remove existing sidebar if any
        const existingSidebar = document.querySelector('.steamlord-minimized-sidebar');
        if (existingSidebar) existingSidebar.remove();

        // Remove login overlay if exists
        const existingOverlay = document.querySelector('.steamlord-login-overlay');
        if (existingOverlay) existingOverlay.remove();

        _isPopupMinimized = true;

        // Save minimized state to localStorage
        try {
            localStorage.setItem('steamlord_popup_minimized', 'true');
        } catch (e) { }

        const sidebar = document.createElement('div');
        sidebar.className = 'steamlord-minimized-sidebar';
        sidebar.title = 'Click to activate SteamLord';

        sidebar.innerHTML = `
            <img id="steamlord-sidebar-logo" alt="SteamLord" style="display: none;">
        `;

        sidebar.onclick = function () {
            _isPopupMinimized = false;
            try {
                localStorage.removeItem('steamlord_popup_minimized');
            } catch (e) { }
            sidebar.remove();
            showLoginPopup();
        };

        document.body.appendChild(sidebar);

        // Load logo via API
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'GetLogoDataUrl', { contentScriptQuery: '' })
                .then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.dataUrl) {
                        const logoImg = document.getElementById('steamlord-sidebar-logo');
                        if (logoImg) {
                            logoImg.src = payload.dataUrl;
                            logoImg.style.display = 'block';
                        }
                    }
                })
                .catch(function (err) {
                    backendLog('SteamLord: Failed to load sidebar logo: ' + err);
                });
        }
    }


    function showLoginPopup(errorMsg, warningMsg) {
        // Remove minimized sidebar if exists
        const existingSidebar = document.querySelector('.steamlord-minimized-sidebar');
        if (existingSidebar) existingSidebar.remove();

        const existing = document.querySelector('.steamlord-login-overlay');
        if (existing) existing.remove();

        _isPopupMinimized = false;
        try {
            localStorage.removeItem('steamlord_popup_minimized');
        } catch (e) { }

        const overlay = document.createElement('div');
        overlay.className = 'steamlord-login-overlay';
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, rgba(5, 15, 35, 0.95), rgba(10, 25, 50, 0.98));
            backdrop-filter: blur(15px);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: steamlordFadeIn 0.4s ease-out;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            position: relative;
            background: linear-gradient(145deg, rgba(15, 35, 70, 0.95), rgba(10, 25, 55, 0.98));
            border: 2px solid rgba(30, 120, 220, 0.4);
            border-radius: 20px;
            padding: 45px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(30, 100, 200, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            animation: steamlordFadeIn 0.5s ease-out;
        `;

        const errorHtml = errorMsg ? `<div id="login-error" style="color: #ff6b6b; font-size: 13px; text-align: center; margin-bottom: 15px; padding: 12px; background: rgba(255, 100, 100, 0.1); border-radius: 8px; border: 1px solid rgba(255, 100, 100, 0.3);">${errorMsg}</div>` : '<div id="login-error"></div>';

        const warningHtml = warningMsg ? `<div class="steamlord-warning-msg"><i class="fa-solid fa-exclamation-triangle"></i><span>${warningMsg}</span></div>` : '';

        modal.innerHTML = `
            <button class="steamlord-minimize-btn" id="steamlord-minimize-btn" title="Minimize">
                <i class="fa-solid fa-minus"></i>
            </button>

            <div style="text-align: center; margin-bottom: 30px;">
                <img id="steamlord-popup-logo" class="steamlord-crown-logo" alt="SteamLord" style="display: none; margin: 0 auto;">
                <h2 style="color: #fff; font-size: 28px; font-weight: 700; margin: 0; text-shadow: 0 0 30px rgba(30, 150, 255, 0.5);">SteamLord</h2>
                <p style="color: #7fc4ff; font-size: 14px; margin-top: 10px; font-weight: 500;">License Activation Required</p>
            </div>

            ${warningHtml}
            ${errorHtml}

            <div style="margin-bottom: 25px;">
                <label style="display: block; color: #7fc4ff; font-size: 13px; margin-bottom: 10px; font-weight: 500;">License Key</label>
                <input type="text" id="steamlord-login-key" placeholder="SL-XXXX-XXXX-XXXX-XXXX" style="
                    width: 100%;
                    padding: 16px 18px;
                    background: linear-gradient(135deg, rgba(30, 60, 100, 0.3), rgba(20, 45, 80, 0.2));
                    border: 2px solid rgba(30, 120, 220, 0.3);
                    border-radius: 10px;
                    color: #fff;
                    font-size: 15px;
                    font-family: monospace;
                    outline: none;
                    transition: all 0.3s ease;
                    box-sizing: border-box;
                " onfocus="this.style.borderColor='rgba(30, 150, 255, 0.8)'; this.style.boxShadow='0 0 20px rgba(30, 150, 255, 0.3)';" onblur="this.style.borderColor='rgba(30, 120, 220, 0.3)'; this.style.boxShadow='none';">
            </div>

            <button id="steamlord-login-btn" style="
                width: 100%;
                padding: 16px 28px;
                background: linear-gradient(135deg, #1e90ff 0%, #0066cc 50%, #1e78d0 100%);
                border: none;
                border-radius: 12px;
                color: #fff;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 6px 25px rgba(30, 100, 200, 0.4);
                text-transform: uppercase;
                letter-spacing: 1px;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 10px 35px rgba(30, 150, 255, 0.5)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 6px 25px rgba(30, 100, 200, 0.4)';">
                <i class="fa-solid fa-crown"></i> Activate License
            </button>

            <div style="text-align: center; margin-top: 25px;">
                <a href="#" id="steamlord-discord-link" style="color: #4da6ff; font-size: 13px; text-decoration: none; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.color='#7fc4ff'; this.style.textShadow='0 0 10px rgba(30, 150, 255, 0.5)';" onmouseout="this.style.color='#4da6ff'; this.style.textShadow='none';">
                    <i class="fa-brands fa-discord"></i> Get a Free Key
                </a>
            </div>
        `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Load logo via API
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'GetLogoDataUrl', { contentScriptQuery: '' })
                .then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.dataUrl) {
                        const logoImg = document.getElementById('steamlord-popup-logo');
                        if (logoImg) {
                            logoImg.src = payload.dataUrl;
                            logoImg.style.display = 'block';
                        }
                    }
                })
                .catch(function (err) {
                    backendLog('SteamLord: Failed to load logo: ' + err);
                });
        }

        // Add minimize button handler
        const minimizeBtn = document.getElementById('steamlord-minimize-btn');
        minimizeBtn.onclick = function (e) {
            e.stopPropagation();
            showMinimizedSidebar();
        };

        // Add login handler
        const loginBtn = document.getElementById('steamlord-login-btn');
        const keyInput = document.getElementById('steamlord-login-key');

        loginBtn.onclick = function () {
            const licenseKey = keyInput.value.trim();

            if (!licenseKey) {
                showLoginError('Please enter your license key');
                return;
            }

            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Activating...';

            Millennium.callServerMethod('steamlord', 'RegisterLicense', {
                licenseKey: licenseKey,
                contentScriptQuery: ''
            }).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success) {
                    _isLicenseValid = true;
                    _isPopupMinimized = false;
                    _sessionInfo = {
                        expiresAt: payload.expiresAt,
                        isLifetime: payload.isLifetime,
                        isFreeKey: payload.isFreeKey,
                        limits: payload.limits
                    };
                    overlay.remove();
                    // Remove sidebar if exists
                    const sidebar = document.querySelector('.steamlord-minimized-sidebar');
                    if (sidebar) sidebar.remove();

                    // Show settings sidebar
                    showSettingsSidebar();

                    showLicenseSuccessToast();
                } else {
                    showLoginError(payload.error || 'Activation failed');
                    loginBtn.disabled = false;
                    loginBtn.innerHTML = '<i class="fa-solid fa-key"></i> Activate License';
                }
            }).catch(function (err) {
                showLoginError('Connection error: ' + err);
                loginBtn.disabled = false;
                loginBtn.innerHTML = '<i class="fa-solid fa-key"></i> Activate License';
            });
        };

        // Enter key support
        keyInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') loginBtn.click();
        });

        // Focus key field
        setTimeout(() => keyInput.focus(), 100);

        // Discord link handler - open externally
        const discordLink = document.getElementById('steamlord-discord-link');
        if (discordLink) {
            discordLink.onclick = function (e) {
                e.preventDefault();
                if (typeof Millennium !== 'undefined') {
                    Millennium.callServerMethod('steamlord', 'OpenExternalUrl', {
                        url: 'https://discord.gg/Uk9MzzHjcr',
                        contentScriptQuery: ''
                    }).catch(function (err) {
                        backendLog('SteamLord: Failed to open Discord: ' + err);
                    });
                }
            };
        }
    }

    function showSettingsSidebar() {
        if (!_isLicenseValid) return;
        if (document.querySelector('.steamlord-settings-sidebar')) return;

        // Load Theme
        Millennium.callServerMethod('steamlord', 'GetTheme', { contentScriptQuery: '' })
            .then(function (res) {
                const p = typeof res === 'string' ? JSON.parse(res) : res;
                if (p && p.success && p.theme) {
                    const t = p.theme;
                    const root = document.documentElement;
                    if (t.primary) root.style.setProperty('--primary-color', t.primary);
                    if (t.gradient_start && t.gradient_end) root.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${t.gradient_start}, ${t.gradient_end})`);
                    if (t.shadow) root.style.setProperty('--primary-shadow', t.shadow);
                    if (t.primary) root.style.setProperty('--text-highlight', t.primary);
                }
            });

        const sidebar = document.createElement('div');
        sidebar.className = 'steamlord-settings-sidebar';
        sidebar.title = 'SteamLord Settings';
        sidebar.innerHTML = '<i class="fa-solid fa-gear"></i>';

        sidebar.onclick = function () {
            showSettingsPopup();
        };

        document.body.appendChild(sidebar);
    }

    function showSettingsPopup() {
        const existing = document.querySelector('.steamlord-settings-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'steamlord-settings-overlay';
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, rgba(5, 15, 35, 0.95), rgba(10, 25, 50, 0.98));
            backdrop-filter: blur(15px);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: steamlordFadeIn 0.4s ease-out;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            position: relative;
            background: linear-gradient(145deg, rgba(15, 35, 70, 0.95), rgba(10, 25, 55, 0.98));
            border: 2px solid rgba(30, 120, 220, 0.4);
            border-radius: 20px;
            padding: 45px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(30, 100, 200, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            animation: steamlordFadeIn 0.5s ease-out;
        `;

        modal.innerHTML = `
            <button class="steamlord-minimize-btn" id="steamlord-settings-close" title="Close">
                <i class="fa-solid fa-times"></i>
            </button>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #fff; font-size: 24px; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(30, 150, 255, 0.5);">SteamLord</h2>
            </div>
            
            <!-- Navigation Tabs -->
            <div class="steamlord-tabs-container">
                <button class="steamlord-tab-btn active" data-tab="settings">Settings</button>
                <button class="steamlord-tab-btn" data-tab="profile">Profile</button>
                <button class="steamlord-tab-btn" data-tab="themes">Themes</button>
                <button class="steamlord-tab-btn" data-tab="about">About</button>
            </div>
            
            <!-- Tab Contents -->
            <div id="tab-settings" class="steamlord-tab-content active" style="padding: 10px 5px;">
                
                <!-- Clear Cache -->
                <div class="steamlord-settings-row" style="display:flex; justify-content:space-between; align-items:center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div class="setting-label" style="display:flex; flex-direction:column; gap:4px;">
                        <div style="display:flex; align-items:center; gap:10px; font-weight:600; font-size:15px; color:#e2e8f0;">
                            <div style="width:32px; height:32px; background:rgba(6,182,212,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center;">
                                <i class="fa-solid fa-broom" style="color:#22d3ee;"></i>
                            </div>
                            <span>Clear Steam Cache</span>
                        </div>
                    </div>
                    <button id="btn-clear-cache" class="steamlord-btn" style="background: linear-gradient(135deg, #06b6d4, #3b82f6); border:none; padding:8px 20px; border-radius:8px; color:white; font-weight:600; font-size:13px; box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2); transition:all 0.3s ease; cursor:pointer;">
                        Clear
                    </button>
                </div>

                <!-- Language -->
                <div class="steamlord-settings-row" style="display:flex; justify-content:space-between; align-items:center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div class="setting-label" style="display:flex; flex-direction:column; gap:4px;">
                        <div style="display:flex; align-items:center; gap:10px; font-weight:600; font-size:15px; color:#e2e8f0;">
                            <div style="width:32px; height:32px; background:rgba(59,130,246,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center;">
                                <i class="fa-solid fa-language" style="color:#60a5fa;"></i>
                            </div>
                            <span>Language</span>
                        </div>
                    </div>
                    <div id="lang-select" style="display:flex; align-items:center; gap:10px; background:rgba(15, 23, 42, 0.6); padding:8px 16px; border-radius:8px; font-size:13px; color:#cbd5e1; cursor:pointer; border:1px solid rgba(59, 130, 246, 0.2); transition:all 0.3s ease;">
                        <span style="font-weight:500;">English</span>
                        <i class="fa-solid fa-chevron-down" style="font-size:10px; opacity:0.7;"></i>
                    </div>
                </div>

                <!-- Restart -->
                <div class="steamlord-settings-row" style="display:flex; justify-content:space-between; align-items:center; padding: 12px 0;">
                    <div class="setting-label" style="display:flex; flex-direction:column; gap:4px;">
                        <div style="display:flex; align-items:center; gap:10px; font-weight:600; font-size:15px; color:#e2e8f0;">
                            <div style="width:32px; height:32px; background:rgba(239,68,68,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center;">
                                <i class="fa-solid fa-power-off" style="color:#f87171;"></i>
                            </div>
                            <span>Restart Steam</span>
                        </div>
                    </div>
                    <button id="btn-restart-steam" class="steamlord-btn" style="background: linear-gradient(135deg, #ef4444, #b91c1c); border:none; padding:8px 20px; border-radius:8px; color:white; font-weight:600; font-size:13px; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); transition:all 0.3s ease; cursor:pointer;">
                        Restart
                    </button>
                </div>
            </div>
            
            <!-- Profile Tab -->
            <div id="tab-profile" class="steamlord-tab-content" style="padding: 10px 5px;">
            </div>

            <!-- Themes Tab -->
            <div id="tab-themes" class="steamlord-tab-content" style="padding: 10px 5px;">
            </div>

            <!-- About Tab -->
            <div id="tab-about" class="steamlord-tab-content" style="padding: 10px 5px;">
            </div>
        `;

        // Helper for consistency
        function getComingSoonContent(title) {
            return `
                <div style="text-align:center; color:#8b9db5; padding:40px 20px;">
                    <i class="fa-solid fa-person-digging" style="margin-bottom:15px; font-size:32px; color:rgba(255,255,255,0.2);"></i>
                    <h3 style="color:#fff; margin:0 0 5px 0; font-size:18px;">${title}</h3>
                    <p style="margin:0; font-size:13px; opacity:0.7;">Coming Soon</p>
                </div>
            `;
        }

        // Tab Switching Logic
        const tabs = modal.querySelectorAll('.steamlord-tab-btn');
        tabs.forEach(tab => {
            tab.onclick = function () {
                // Remove active class from all
                modal.querySelectorAll('.steamlord-tab-btn').forEach(b => b.classList.remove('active'));
                modal.querySelectorAll('.steamlord-tab-content').forEach(c => c.classList.remove('active'));

                // Add active to current
                this.classList.add('active');
                const targetId = 'tab-' + this.getAttribute('data-tab');
                modal.querySelector('#' + targetId).classList.add('active');
            };
        });

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Close button handler
        document.getElementById('steamlord-settings-close').onclick = function () {
            overlay.remove();
        };

        // --- Settings Button Handlers ---

        // 1. Clear Cache
        const clearCacheBtn = document.getElementById('btn-clear-cache');
        if (clearCacheBtn) {
            clearCacheBtn.onclick = function () {
                this.disabled = true;
                this.innerHTML = '<i class="fa-solid fa-sync fa-spin"></i>';

                Millennium.callServerMethod('steamlord', 'ClearSteamCache', { contentScriptQuery: '' })
                    .then(function (res) {
                        const p = typeof res === 'string' ? JSON.parse(res) : res;
                        if (p && p.success) {
                            showSteamLordToast(p.message || 'Cache Cleared', 'success');
                        } else {
                            showSteamLordToast(p.error || 'Failed to clear cache', 'error');
                        }
                    })
                    .catch(err => showSteamLordToast('Error: ' + err, 'error'))
                    .finally(() => {
                        clearCacheBtn.disabled = false;
                        clearCacheBtn.textContent = 'Clear';
                    });
            };
        }

        // 2. Language Selector (Placeholder)
        const langSelect = document.getElementById('lang-select');
        if (langSelect) {
            langSelect.onclick = function () {
                showSteamLordToast('Coming Soon', 'info');
            };
        }

        // 3. Restart Steam
        const restartBtn = document.getElementById('btn-restart-steam');
        if (restartBtn) {
            restartBtn.onclick = function () {
                showSteamLordToast('Restarting Steam...', 'info');
                setTimeout(() => {
                    Millennium.callServerMethod('steamlord', 'RestartSteam', { contentScriptQuery: '' });
                }, 1000);
            };
        }

        // --- Profile Tab Handling ---
        function loadProfileData() {
            const container = document.getElementById('tab-profile');
            if (!container) return;

            container.innerHTML = `<div style="text-align:center; padding: 60px 0; color:#fff;"><i class="fa-solid fa-circle-notch fa-spin" style="font-size:28px; color:#66c0f4; margin-bottom:15px;"></i><div style="font-size:13px; opacity:0.7; font-weight:500;">Loading Profile...</div></div>`;

            Millennium.callServerMethod('steamlord', 'GetProfileData', { contentScriptQuery: '' })
                .then(function (res) {
                    const p = typeof res === 'string' ? JSON.parse(res) : res;
                    if (p && p.success && p.profile) {
                        renderProfileData(p.profile);
                    } else {
                        container.innerHTML = `<div style="text-align:center; padding: 40px; color:#ef4444;"><i class="fa-solid fa-triangle-exclamation" style="font-size:32px; margin-bottom:10px;"></i><br>Failed to load profile data.<br><span style="font-size:12px; opacity:0.7;">${p.error || 'Unknown error'}</span></div>`;
                    }
                })
                .catch(err => {
                    container.innerHTML = `<div style="text-align:center; padding: 40px; color:#ef4444;">Error: ${err}</div>`;
                });
        }

        function renderProfileData(profile) {
            const container = document.getElementById('tab-profile');
            if (!container) return;

            // Parse expiry
            let durationText = 'Unknown';
            if (profile.is_lifetime) {
                durationText = 'Lifetime';
            } else {
                try {
                    const expires = typeof profile.expiry_date === 'number' ? profile.expiry_date : new Date(profile.expiry_date).getTime();
                    if (!isNaN(expires)) {
                        const now = new Date().getTime();
                        const diff = expires - now;
                        if (diff > 0) {
                            const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
                            durationText = `${days} Days`;
                        } else {
                            durationText = 'Expired';
                        }
                    } else { durationText = 'Unknown'; }
                } catch (e) { durationText = 'Unknown'; }
            }

            container.innerHTML = `
                <div style="padding: 10px 5px; animation: steamlordFadeIn 0.3s ease-out;">
                    <div class="profile-key-card">
                        <div class="key-label"><i class="fa-solid fa-key" style="margin-right:5px;"></i> License Key</div>
                        <div class="key-value">${profile.license_key || 'Unknown'}</div>
                    </div>

                    <div class="profile-stats-grid">
                        <div class="stat-card">
                            <i class="fa-solid fa-download"></i>
                            <div class="stat-value">${profile.downloads_count || 0}</div>
                            <div class="stat-label">Downloads</div>
                        </div>
                        <div class="stat-card">
                            <i class="fa-solid fa-wrench"></i>
                            <div class="stat-value">${profile.online_fix_count || 0}</div>
                            <div class="stat-label">Online Fixes</div>
                        </div>
                        <div class="stat-card">
                            <i class="fa-solid fa-shield-halved"></i>
                            <div class="stat-value">${profile.bypass_count || 0}</div>
                            <div class="stat-label">Bypasses</div>
                        </div>
                        <div class="stat-card">
                            <i class="fa-solid fa-hourglass-half"></i>
                            <div class="stat-value" style="font-size:${durationText.length > 8 ? '16px' : '18px'};">${durationText}</div>
                            <div class="stat-label">Duration</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Attach click listener
        const profileTabBtn = modal.querySelector('.steamlord-tab-btn[data-tab="profile"]');
        if (profileTabBtn) {
            profileTabBtn.addEventListener('click', () => {
                const container = document.getElementById('tab-profile');
                if (container && container.innerHTML.trim() === '') {
                    loadProfileData();
                }
            });
        }

        // --- Themes Tab Handling ---
        const themes = [
            { id: 'blue', name: 'Royal Blue', primary: '#3b82f6', start: '#3b82f6', end: '#2563eb', shadow: 'rgba(59, 130, 246, 0.5)' },
            { id: 'red', name: 'Crimson Lord', primary: '#ef4444', start: '#ef4444', end: '#dc2626', shadow: 'rgba(239, 68, 68, 0.5)' },
            { id: 'green', name: 'Toxic Guard', primary: '#22c55e', start: '#22c55e', end: '#16a34a', shadow: 'rgba(34, 197, 94, 0.5)' },
            { id: 'purple', name: 'Void Purple', primary: '#a855f7', start: '#a855f7', end: '#9333ea', shadow: 'rgba(168, 85, 247, 0.5)' },
            { id: 'orange', name: 'Sunset King', primary: '#f97316', start: '#f97316', end: '#ea580c', shadow: 'rgba(249, 115, 22, 0.5)' },
            { id: 'cyan', name: 'Ice Realm', primary: '#06b6d4', start: '#06b6d4', end: '#0891b2', shadow: 'rgba(6, 182, 212, 0.5)' }
        ];

        function renderThemes() {
            const container = document.getElementById('tab-themes');
            if (!container) return;

            let html = '<div class="theme-grid">';
            themes.forEach(t => {
                const isActive = document.documentElement.style.getPropertyValue('--primary-color') === t.primary;
                html += `
                    <div class="theme-card ${isActive ? 'active' : ''}" onclick="window.steamlord.applyTheme('${t.id}')">
                        <div class="theme-preview" style="background: linear-gradient(135deg, ${t.start}, ${t.end});"></div>
                        <div class="theme-name">${t.name}</div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        // Expose applyTheme globally for onclick
        window.steamlord = window.steamlord || {};
        window.steamlord.applyTheme = function (themeId) {
            const theme = themes.find(t => t.id === themeId);
            if (!theme) return;

            // Apply CSS Variables
            const root = document.documentElement;
            root.style.setProperty('--primary-color', theme.primary);
            root.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${theme.start}, ${theme.end})`);
            root.style.setProperty('--primary-shadow', theme.shadow);
            root.style.setProperty('--text-highlight', theme.primary); // Use primary for text highlight too

            // Save to Backend
            Millennium.callServerMethod('steamlord', 'SetTheme', {
                theme_data: JSON.stringify({
                    id: theme.id,
                    primary: theme.primary,
                    gradient_start: theme.start,
                    gradient_end: theme.end,
                    shadow: theme.shadow
                })
            });

            // Re-render UI to update active state
            renderThemes();
        };

        const themesTabBtn = modal.querySelector('.steamlord-tab-btn[data-tab="themes"]');
        if (themesTabBtn) {
            themesTabBtn.addEventListener('click', renderThemes);
        }

        // --- About Tab Handling ---
        function renderAbout() {
            const container = document.getElementById('tab-about');
            if (!container) return;

            const socials = [
                { name: 'Discord', icon: 'fa-discord', color: '#5865F2', url: 'https://discord.gg/Uk9MzzHjcr' },
                { name: 'Facebook', icon: 'fa-facebook', color: '#1877F2', url: 'https://www.facebook.com/' },
                { name: 'YouTube', icon: 'fa-youtube', color: '#FF0000', url: 'https://www.youtube.com/' },
                { name: 'X / Twitter', icon: 'fa-x-twitter', color: '#ffffff', url: 'https://twitter.com/' },
                { name: 'Instagram', icon: 'fa-instagram', color: '#E1306C', url: 'https://www.instagram.com/' },
                { name: 'TikTok', icon: 'fa-tiktok', color: '#ffffff', url: 'https://www.tiktok.com/' }
            ];

            let html = `
                <div style="text-align:center; margin-bottom:20px; color:#cbd5e1; font-size:14px;">
                    Follow us on our social media platforms for updates and support.
                </div>
                <div class="social-grid">
            `;

            socials.forEach(s => {
                html += `
                    <div class="social-card" onclick="Millennium.callServerMethod('steamlord', 'OpenExternalUrl', { url: '${s.url}', contentScriptQuery: '' })">
                        <i class="fa-brands ${s.icon} social-icon" style="color: ${s.color};"></i>
                        <div class="social-label">${s.name}</div>
                    </div>
                `;
            });
            html += '</div>';

            html += `
                <div style="margin-top:25px; text-align:center; padding-top:15px; border-top:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:12px; color:#64748b;">SteamLord v2.0 &copy; 2026</div>
                    <div style="font-size:11px; color:#475569; margin-top:2px;">Developed with <i class="fa-solid fa-heart" style="color:#ef4444; font-size:10px;"></i> by Abdo & Osama</div>
                </div>
            `;

            container.innerHTML = html;
        }

        const aboutTabBtn = modal.querySelector('.steamlord-tab-btn[data-tab="about"]');
        if (aboutTabBtn) {
            aboutTabBtn.addEventListener('click', renderAbout);
        }
    }

    // Helper for toasts
    function showSteamLordToast(msg, type) {
        // types: success, error, info
        const colors = {
            success: 'linear-gradient(135deg, rgba(34, 197, 94, 0.9), rgba(22, 163, 74, 0.9))',
            error: 'linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9))',
            info: 'linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(37, 99, 235, 0.9))'
        };
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: ${colors[type] || colors.info};
            border-radius: 8px;
            padding: 12px 20px;
            color: white;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1000000;
            animation: steamlordFadeIn 0.3s ease-out;
            backdrop-filter: blur(5px);
        `;
        toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i> ${msg}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function showLoginError(msg) {
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
            errorDiv.style.cssText = `
                color: #ef4444;
                font-size: 13px;
                text-align: center;
                margin-bottom: 15px;
                padding: 10px;
                background: rgba(239, 68, 68, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(239, 68, 68, 0.3);
            `;
        }
    }

    function showLicenseSuccessToast() {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.9), rgba(22, 163, 74, 0.9));
            border: 1px solid rgba(34, 197, 94, 0.5);
            border-radius: 10px;
            padding: 16px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            z-index: 100000;
            animation: steamlordFadeIn 0.5s ease-out;
            backdrop-filter: blur(10px);
        `;
        toast.innerHTML = `
            <i class="fa-solid fa-check-circle" style="font-size: 24px; color: #fff;"></i>
            <div>
                <div style="font-weight: 600; color: #fff; margin-bottom: 2px;">License Activated!</div>
                <div style="font-size: 13px; color: rgba(255,255,255,0.8);">Welcome to SteamLord</div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.5s ease';
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    }

    function showLicenseExpiredPopup() {
        showLoginPopup('Your license has expired. Please renew to continue.');
    }

    // Promise that resolves when license check is done
    let _licenseCheckPromise = null;

    function waitForLicenseCheck() {
        if (_licenseCheckDone) {
            return Promise.resolve(_isLicenseValid);
        }

        // Already waiting
        if (_licenseCheckPromise) {
            return _licenseCheckPromise;
        }

        // Create a promise that resolves when check completes
        _licenseCheckPromise = new Promise(function (resolve) {
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds max wait

            function checkDone() {
                attempts++;
                if (_licenseCheckDone) {
                    resolve(_isLicenseValid);
                } else if (attempts >= maxAttempts) {
                    // Timeout - assume not valid
                    resolve(false);
                } else {
                    setTimeout(checkDone, 100);
                }
            }
            checkDone();
        });

        return _licenseCheckPromise;
    }

    function requireLicense() {
        // If license check is done, use cached result
        if (_licenseCheckDone) {
            if (!_isLicenseValid) {
                // Show popup with warning message
                showLoginPopup(null, 'Activation required to use this feature');
                return false;
            }
            return true;
        }

        // License check not done yet - wait briefly
        // Show a loading indicator and wait
        backendLog('SteamLord: Waiting for license check to complete...');

        // For sync compatibility, we give a small grace period
        // If still checking after this, assume valid (optimistic)
        // The actual API call will fail if not valid anyway
        return true;
    }

    function logoutLicense() {
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'Logout', { contentScriptQuery: '' }).then(function () {
                _isLicenseValid = false;
                _sessionInfo = null;

                // Remove settings sidebar
                const settingsSidebar = document.querySelector('.steamlord-settings-sidebar');
                if (settingsSidebar) settingsSidebar.remove();

                showLoginPopup('Logged out successfully');
            });
        }
    }

    function getLicenseInfo() {
        return _sessionInfo;
    }

    // Initialize license check
    function initLicenseSystem() {
        if (typeof Millennium === 'undefined') {
            _licenseCheckDone = true;
            return;
        }

        // Check if popup was previously minimized
        let wasMinimized = false;
        try {
            wasMinimized = localStorage.getItem('steamlord_popup_minimized') === 'true';
        } catch (e) { }

        // Use IsLoggedIn for fast local check first
        Millennium.callServerMethod('steamlord', 'IsLoggedIn', { contentScriptQuery: '' })
            .then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && payload.isLoggedIn) {
                    // User is logged in locally, verify with server
                    return Millennium.callServerMethod('steamlord', 'VerifyLicense', { contentScriptQuery: '' })
                        .then(function (verifyRes) {
                            const verifyPayload = typeof verifyRes === 'string' ? JSON.parse(verifyRes) : verifyRes;
                            if (verifyPayload && verifyPayload.success && verifyPayload.valid) {
                                _isLicenseValid = true;
                                _licenseCheckDone = true;
                                _sessionInfo = {
                                    email: verifyPayload.email,
                                    expiresAt: verifyPayload.expiresAt,
                                    isLifetime: verifyPayload.isLifetime
                                };
                                backendLog('SteamLord: License verified successfully');
                                // Clear minimized state since user is now valid
                                try {
                                    localStorage.removeItem('steamlord_popup_minimized');
                                } catch (e) { }

                                // Show settings sidebar
                                showSettingsSidebar();
                            } else {
                                _isLicenseValid = false;
                                _licenseCheckDone = true;
                                backendLog('SteamLord: Verification failed: ' + (verifyPayload.error || 'Unknown'));
                                // Show popup or sidebar based on previous state
                                if (wasMinimized) {
                                    showMinimizedSidebar();
                                } else {
                                    showLoginPopup(verifyPayload.error || 'Session expired');
                                }
                            }
                        });
                } else {
                    // Not logged in
                    _isLicenseValid = false;
                    _licenseCheckDone = true;
                    // Show popup or sidebar based on previous state
                    if (wasMinimized) {
                        showMinimizedSidebar();
                    } else {
                        showLoginPopup();
                    }
                }
            })
            .catch(function (err) {
                backendLog('SteamLord: License check error: ' + err);
                _isLicenseValid = false;
                _licenseCheckDone = true;
                // Show popup or sidebar based on previous state
                if (wasMinimized) {
                    showMinimizedSidebar();
                } else {
                    showLoginPopup();
                }
            });
    }

    // Start license check
    initLicenseSystem();

    // --- UI HELPERS ---

    function createGlassModal(titleText, contentHtml, buttons) {
        // Remove existing
        const existing = document.querySelector('.steamlord-glass-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'steamlord-glass-overlay';

        const modal = document.createElement('div');
        modal.className = 'steamlord-glass-modal';

        const content = document.createElement('div');
        content.className = 'steamlord-modal-content';

        // Title
        const title = document.createElement('div');
        title.className = 'steamlord-title';
        title.innerHTML = '<i class="fa-brands fa-steam"></i> ' + (titleText || 'SteamLord - Menu');

        // Body
        const body = document.createElement('div');
        body.className = 'steamlord-text';
        if (typeof contentHtml === 'string') {
            body.innerHTML = contentHtml;
        } else {
            body.appendChild(contentHtml);
        }

        // Buttons
        const btnRow = document.createElement('div');
        btnRow.className = 'steamlord-btn-row';

        if (buttons && buttons.length > 0) {
            buttons.forEach(b => {
                const btn = document.createElement('a');
                btn.className = 'steamlord-btn ' + (b.variant || '');
                btn.innerHTML = '<span>' + b.text + '</span>';
                btn.onclick = (e) => {
                    e.preventDefault();
                    if (b.onClick) b.onClick(e);
                    if (b.close !== false) overlay.remove();
                };
                btnRow.appendChild(btn);
            });
        } else {
            // Default close
            const closeBtn = document.createElement('a');
            closeBtn.className = 'steamlord-btn';
            closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
            closeBtn.onclick = (e) => { e.preventDefault(); overlay.remove(); };
            btnRow.appendChild(closeBtn);
        }

        content.appendChild(title);
        content.appendChild(body);
        content.appendChild(btnRow);
        modal.appendChild(content);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        return { overlay, body, btnRow }; // Return refs for dynamic updates
    }

    // --- Replaces standard confirm ---
    function showSteamLordConfirm(message, onYes) {
        createGlassModal('SteamLord - Menu', message, [
            {
                text: lt('Cancel'),
                variant: 'danger',
                onClick: () => { }
            },
            {
                text: lt('OK'),
                variant: 'success',
                onClick: onYes
            }
        ]);
    }

    // --- Replaces standard alert ---
    function showSteamLordAlert(message) {
        createGlassModal('SteamLord - Menu', message, [
            { text: lt('OK'), variant: 'primary' }
        ]);
    }

    // New Online Fix Popup
    function showOnlineFixPopup(appid, gameName) {
        const msg = `
            <div style="margin-bottom: 15px;">
                ${lt('Online Fix Game')}: <strong>${gameName || ''}</strong>
            </div>
            <div style="font-size: 12px; color: #8b9db5; line-height: 1.5; margin-bottom: 8px; text-align: left;">
                Before adding Online Fix: some antivirus tools may flag its files as a false positive and delete/quarantine them. To avoid this, add an Exception/Exclusion for your Steam folder (and any folder containing Online Fix files). If you don't know how, you'll find a full guide in our Discord server.
            </div>
        `;

        createGlassModal('SteamLord - Menu', msg, [
            {
                text: lt('APPLY FIX'),
                variant: 'success',
                close: true,
                onClick: () => {
                    // Pre-book the task to prevent race condition with poller
                    window.steamlord.TaskManager.startTask('fix', appid, () => { });

                    Millennium.callServerMethod('steamlord', 'GetGameInstallPath', { appid, contentScriptQuery: '' }).then(function (res) {
                        const payload = typeof res === 'string' ? JSON.parse(res) : res;
                        if (payload && payload.success && payload.installPath) {
                            Millennium.callServerMethod('steamlord', 'ApplyGameFix', {
                                appid: appid,
                                downloadUrl: 'ignored',
                                installPath: payload.installPath,
                                fixType: 'LordFix',
                                gameName: gameName || '',
                                contentScriptQuery: ''
                            }).then(function (r) {
                                const p = typeof r === 'string' ? JSON.parse(r) : r;
                                if (p && p.success) {
                                    showFixDownloadProgress(appid, 'LordFix', gameName);
                                } else {
                                    window.steamlord.TaskManager.finishTask('fix');
                                    showSteamLordAlert(p.error || 'Failed to start fix');
                                }
                            });
                        } else {
                            window.steamlord.TaskManager.finishTask('fix');
                            showSteamLordAlert(lt('Game install path not found'));
                        }
                    });
                }
            },
            {
                text: lt('REMOVE FIX'),
                variant: 'danger',
                close: true,
                onClick: () => {
                    // Pre-book the task
                    window.steamlord.TaskManager.startTask('fix', appid, () => { });

                    Millennium.callServerMethod('steamlord', 'GetGameInstallPath', { appid, contentScriptQuery: '' }).then(function (res) {
                        const payload = typeof res === 'string' ? JSON.parse(res) : res;
                        if (payload && payload.success && payload.installPath) {
                            Millennium.callServerMethod('steamlord', 'UnFixGame', {
                                appid: appid,
                                installPath: payload.installPath,
                                contentScriptQuery: ''
                            }).then(function (r) {
                                const p = typeof r === 'string' ? JSON.parse(r) : r;
                                if (p && p.success) {
                                    showUnfixProgress(appid);
                                } else {
                                    window.steamlord.TaskManager.finishTask('fix');
                                    showSteamLordAlert(p.error || 'Failed to start unfix');
                                }
                            });
                        } else {
                            window.steamlord.TaskManager.finishTask('fix');
                            showSteamLordAlert(lt('Game install path not found'));
                        }
                    });
                }
            },
            { text: lt('Close') }
        ]);
    }

    function showFixDownloadProgress(appid, fixType, gameName) {
        window.steamlord.TaskManager.startTask('fix', appid, () => {
            let refs = null;
            const displayName = gameName || '';

            function createModal() {
                refs = createGlassModal(
                    'SteamLord - Menu',
                    '<div id="lt-fix-progress-msg">' + lt('Downloading {game} Fix...').replace('{game}', displayName) + '</div>',
                    [{
                        text: lt('Hide'),
                        variant: 'primary',
                        onClick: () => {
                            if (refs && refs.overlay) refs.overlay.remove();
                            window.steamlord.TaskManager.minimize('fix', appid, () => {
                                createModal();
                            });
                        }
                    }]
                );
            }

            createModal();

            const timer = setInterval(() => {
                const active = window.steamlord.TaskManager.active['fix'];
                if (!active || active.appid !== appid) {
                    clearInterval(timer);
                    if (refs && refs.overlay && document.body.contains(refs.overlay)) refs.overlay.remove();
                    return;
                }

                const isMinimized = active.minimized;

                Millennium.callServerMethod('steamlord', 'GetApplyFixStatus', { appid: appid, contentScriptQuery: '' }).then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.state) {
                        const state = payload.state;

                        if (!isMinimized && refs && document.body.contains(refs.overlay)) {
                            const msgEl = document.getElementById('lt-fix-progress-msg');
                            if (state.status === 'downloading') {
                                // FIX: Validate totalBytes
                                const pct = (state.totalBytes > 1000) ? Math.floor((state.bytesRead / state.totalBytes) * 100) : 0;
                                if (msgEl) {
                                    msgEl.innerHTML = `
                                        <div class="steamlord-download-status">
                                            <span class="steamlord-download-text">${lt('Downloading {game} Fix...').replace('{game}', displayName)}</span>
                                            <span class="steamlord-download-percent">${pct}%</span>
                                        </div>
                                        <div class="steamlord-progress-bar-container">
                                            <div class="steamlord-progress-bar-fill" style="width:${pct}%"></div>
                                        </div>
                                    `;
                                }
                            } else if (state.status === 'extracting') {
                                if (msgEl) msgEl.textContent = lt('Extracting...');
                            } else if (state.status === 'done') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('fix');

                                if (msgEl) {
                                    msgEl.innerHTML = `
                                        <div class="steamlord-success-container">
                                            <div class="steamlord-success-title">
                                                <i class="fa-solid fa-circle-check"></i> ${lt('Fix Added Successfully!')}
                                            </div>
                                            <div class="steamlord-warning-note">
                                                <i class="fa-solid fa-circle-info"></i>
                                                <span>Important: Some online fixes may stop working after a game update. If the game doesn't launch or work properly after applying this fix, the fix files likely need updating. Please remove the fix and submit a request on our Discord server - we'll update it for you!</span>
                                            </div>
                                        </div>
                                    `;
                                }
                                // Replace Hide with Close
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn primary';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            } else if (state.status === 'failed') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('fix');

                                const errorMsg = state.error || 'Unknown';
                                if (msgEl) {
                                    if (errorMsg.includes('Upgrade Now') || errorMsg.includes('Premium') || errorMsg.includes('Locked')) {
                                        msgEl.innerHTML = `
                                            <div style="display:flex; flex-direction:column; align-items:center; gap:15px; padding:10px;">
                                                <div style="color:#ef4444; font-weight:bold; font-size:15px;">${lt('Failed: {error}').replace('{error}', errorMsg)}</div>
                                                <a href="https://discord.gg/Uk9MzzHjcr" target="_blank" class="steamlord-btn primary" style="padding:10px 20px; font-size:14px; text-decoration:none;">
                                                    <i class="fa-brands fa-discord" style="margin-right:8px;"></i> ${lt('Upgrade Now')}
                                                </a>
                                            </div>
                                        `;
                                    } else {
                                        msgEl.textContent = lt('Failed: {error}').replace('{error}', errorMsg);
                                    }
                                }
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn danger';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            }
                        } else if (isMinimized) {
                            if (state.status === 'done' || state.status === 'failed') {
                                window.steamlord.TaskManager.restore('fix');
                            }
                        }
                    }
                });

                // Check persistence
                Millennium.callServerMethod('steamlord', 'IsRestartRequired', { contentScriptQuery: '' }).then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.required) {
                        showRestartBanner(true); // true = skip setting flag again
                    }
                });

            }, 500);
        });
    }

    function showRestartBanner(skipSetFlag) {
        if (document.getElementById('steamlord-restart-banner')) return;

        // Set backend flag if not skipping (i.e. first time trigger)
        if (!skipSetFlag) {
            Millennium.callServerMethod('steamlord', 'SetRestartRequired', { contentScriptQuery: '' });
        }

        const container = document.createElement('div');
        container.id = 'steamlord-restart-banner';
        container.className = 'steamlord-floating-banner';

        // Initial Content
        container.innerHTML = `
            <div class="banner-content" style="transition: all 0.3s ease;">
                <i class="fa-solid fa-info-circle" style="margin-right: 8px;"></i>
                ${lt('The Changes will Only Appear After Restarting Steam')}
            </div>
            <div class="banner-hover-content" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0; transform: translateY(20px); transition: all 0.3s ease;">
                <i class="fa-solid fa-power-off" style="margin-right: 8px;"></i>
                ${lt('Restart Steam')}
            </div>
        `;

        // Hover Effects (JS part for content switching)
        container.onmouseenter = () => {
            container.querySelector('.banner-content').style.opacity = '0';
            container.querySelector('.banner-content').style.transform = 'translateY(-20px)';
            container.querySelector('.banner-hover-content').style.opacity = '1';
            container.querySelector('.banner-hover-content').style.transform = 'translateY(0)';
        };

        container.onmouseleave = () => {
            container.querySelector('.banner-content').style.opacity = '1';
            container.querySelector('.banner-content').style.transform = 'translateY(0)';
            container.querySelector('.banner-hover-content').style.opacity = '0';
            container.querySelector('.banner-hover-content').style.transform = 'translateY(20px)';
        };

        // Click Action
        container.onclick = () => {
            Millennium.callServerMethod('steamlord', 'RestartSteam', { contentScriptQuery: '' });
        };

        document.body.appendChild(container);
    }

    function showSuccessRestartModal(title) {
        createGlassModal('SteamLord - Success',
            `
            <div style="text-align: center;">
                <div style="font-size: 16px; font-weight: bold; color: #a4d007; margin-bottom: 10px;">
                    <i class="fa-solid fa-check-circle"></i> ${title}
                </div>
            </div>
            `,
            [
                {
                    text: lt('Restart Steam'),
                    variant: 'primary',
                    onClick: () => {
                        Millennium.callServerMethod('steamlord', 'RestartSteam', { contentScriptQuery: '' });
                    }
                },
                {
                    text: lt('Restart Later'),
                    onClick: () => {
                        showRestartBanner();
                    }
                }
            ]
        );
    }

    function showUnfixProgress(appid) {
        window.steamlord.TaskManager.startTask('fix', appid, () => {
            let refs = null;

            function createModal() {
                refs = createGlassModal(
                    'SteamLord - Menu',
                    '<div id="lt-unfix-progress-msg">' + lt('Working...') + '</div>',
                    [{
                        text: lt('Hide'),
                        variant: 'primary',
                        onClick: () => {
                            if (refs && refs.overlay) refs.overlay.remove();
                            window.steamlord.TaskManager.minimize('fix', appid, () => {
                                createModal();
                            });
                        }
                    }]
                );
            }

            createModal();

            const timer = setInterval(() => {
                const active = window.steamlord.TaskManager.active['fix'];
                if (!active || active.appid !== appid) {
                    clearInterval(timer);
                    if (refs && refs.overlay && document.body.contains(refs.overlay)) refs.overlay.remove();
                    return;
                }

                const isMinimized = active.minimized;

                Millennium.callServerMethod('steamlord', 'GetUnfixStatus', { appid: appid, contentScriptQuery: '' }).then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.state) {
                        const state = payload.state;

                        if (!isMinimized && refs && document.body.contains(refs.overlay)) {
                            const msgEl = document.getElementById('lt-unfix-progress-msg');

                            if (state.status === 'removing') {
                                if (msgEl) msgEl.textContent = state.progress || lt('Removing...');
                            } else if (state.status === 'done') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('fix');

                                if (msgEl) msgEl.textContent = lt('Done! Verifying game files...');
                                setTimeout(function () {
                                    window.location.href = 'steam://validate/' + appid;
                                }, 1000);
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn primary';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            } else if (state.status === 'failed') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('fix');

                                const errorMsg = state.error || 'Unknown';
                                if (msgEl) {
                                    if (errorMsg.includes('Upgrade Now') || errorMsg.includes('Premium')) {
                                        msgEl.innerHTML = `
                                            <div style="display:flex; flex-direction:column; align-items:center; gap:15px; padding:10px;">
                                                <div style="color:#ef4444; font-weight:bold; font-size:15px;">${lt('Failed: {error}').replace('{error}', errorMsg)}</div>
                                                <a href="https://discord.gg/Uk9MzzHjcr" target="_blank" class="steamlord-btn primary" style="padding:10px 20px; font-size:14px; text-decoration:none;">
                                                    <i class="fa-brands fa-discord" style="margin-right:8px;"></i> ${lt('Upgrade Now')}
                                                </a>
                                            </div>
                                        `;
                                    } else {
                                        msgEl.textContent = lt('Failed: {error}').replace('{error}', errorMsg);
                                    }
                                }
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn danger';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            }
                        } else if (isMinimized) {
                            if (state.status === 'done' || state.status === 'failed') {
                                window.steamlord.TaskManager.restore('fix');
                            }
                        }
                    }
                });
            }, 1000);
        });
    }

    function showBypassPopup(appid, gameName) {
        const msg = `
            <div style="margin-bottom: 15px;">
                ${lt('Checking Baypass')}: <strong>${gameName || ''}</strong>
            </div>
            <div style="font-size: 12px; color: #8b9db5; line-height: 1.5; margin-bottom: 8px; text-align: left;">
                Before adding Bypass: some antivirus tools may flag its files as a false positive and delete/quarantine them. To avoid this, add an Exception/Exclusion for your Steam folder (and any folder containing Bypass files). If you don't know how, you'll find a full guide in our Discord server.
            </div>
        `;

        createGlassModal('SteamLord - Menu', msg, [
            {
                text: lt('Bypass Game'),
                variant: 'success',
                close: true,
                onClick: () => {
                    // Pre-book
                    window.steamlord.TaskManager.startTask('bypass', appid, () => { });

                    Millennium.callServerMethod('steamlord', 'GetGameInstallPath', { appid, contentScriptQuery: '' }).then(function (res) {
                        const payload = typeof res === 'string' ? JSON.parse(res) : res;
                        if (payload && payload.success && payload.installPath) {
                            Millennium.callServerMethod('steamlord', 'ApplyBypass', {
                                appid: appid,
                                installPath: payload.installPath,
                                contentScriptQuery: ''
                            }).then(function (r) {
                                const p = typeof r === 'string' ? JSON.parse(r) : r;
                                if (p && p.success) {
                                    showBypassProgress(appid, 'apply', gameName);
                                } else {
                                    window.steamlord.TaskManager.finishTask('bypass');
                                    showSteamLordAlert(p.error || 'Failed to start bypass');
                                }
                            });
                        } else {
                            window.steamlord.TaskManager.finishTask('bypass');
                            showSteamLordAlert(lt('Game install path not found'));
                        }
                    });
                }
            },
            {
                text: lt('Remove Bypass'),
                variant: 'danger',
                close: true,
                onClick: () => {
                    // Pre-book
                    window.steamlord.TaskManager.startTask('bypass', appid, () => { });

                    Millennium.callServerMethod('steamlord', 'GetGameInstallPath', { appid, contentScriptQuery: '' }).then(function (res) {
                        const payload = typeof res === 'string' ? JSON.parse(res) : res;
                        if (payload && payload.success && payload.installPath) {
                            Millennium.callServerMethod('steamlord', 'RemoveBypass', {
                                appid: appid,
                                installPath: payload.installPath,
                                contentScriptQuery: ''
                            }).then(function (r) {
                                const p = typeof r === 'string' ? JSON.parse(r) : r;
                                if (p && p.success) {
                                    showBypassProgress(appid, 'remove', gameName);
                                } else {
                                    window.steamlord.TaskManager.finishTask('bypass');
                                    showSteamLordAlert(p.error || 'Failed to start remove bypass');
                                }
                            });
                        } else {
                            window.steamlord.TaskManager.finishTask('bypass');
                            showSteamLordAlert(lt('Game install path not found'));
                        }
                    });
                }
            },
            { text: lt('Close') }
        ]);
    }

    function showBypassProgress(appid, mode, gameName) {
        window.steamlord.TaskManager.startTask('bypass', appid, () => {
            let refs = null;
            const displayName = gameName || '';

            function createModal() {
                refs = createGlassModal(
                    'SteamLord - Menu',
                    '<div id="lt-bypass-progress-msg">' + lt('Working...') + '</div>',
                    [{
                        text: lt('Hide'),
                        variant: 'primary',
                        onClick: () => {
                            if (refs && refs.overlay) refs.overlay.remove();
                            window.steamlord.TaskManager.minimize('bypass', appid, () => {
                                createModal();
                            });
                        }
                    }]
                );
            }

            createModal();

            const timer = setInterval(() => {
                const active = window.steamlord.TaskManager.active['bypass'];
                if (!active || active.appid !== appid) {
                    clearInterval(timer);
                    if (refs && refs.overlay && document.body.contains(refs.overlay)) refs.overlay.remove();
                    return;
                }

                const isMinimized = active.minimized;
                const method = mode === 'apply' ? 'GetApplyBypassStatus' : 'GetRemoveBypassStatus';

                Millennium.callServerMethod('steamlord', method, { appid: appid, contentScriptQuery: '' }).then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && payload.state) {
                        const state = payload.state;

                        if (!isMinimized && refs && document.body.contains(refs.overlay)) {
                            const msgEl = document.getElementById('lt-bypass-progress-msg');

                            if (state.status === 'downloading') {
                                if (msgEl) {
                                    // FIX: Validate totalBytes
                                    const pct = (state.totalBytes > 1000) ? ((state.bytesRead / state.totalBytes) * 100).toFixed(0) : 0;

                                    msgEl.innerHTML = `
                                        <div class="steamlord-download-status">
                                            <span class="steamlord-download-text">${lt('Downloading {game} Bypass...').replace('{game}', displayName)}</span>
                                            <span class="steamlord-download-percent">${pct}%</span>
                                        </div>
                                        <div class="steamlord-progress-bar-container">
                                            <div class="steamlord-progress-bar-fill" style="width:${pct}%"></div>
                                        </div>
                                    `;
                                }
                            } else if (state.status === 'extracting' || state.status === 'removing') {
                                if (msgEl) msgEl.textContent = state.progress || (state.status === 'extracting' ? lt('Extracting...') : lt('Removing...'));
                            } else if (state.status === 'done') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('bypass');

                                if (mode === 'apply') {
                                    // Show game info if available
                                    if (state.gameInfo && msgEl) {
                                        const info = state.gameInfo;
                                        msgEl.innerHTML = `
                                            <div class="steamlord-bypass-success">
                                                <div class="steamlord-success-title">
                                                    <i class="fa-solid fa-shield-check"></i> ${lt('Bypass Added Successfully!')}
                                                </div>
                                                <div class="info-columns">
                                                    <div class="info-col">
                                                        <i class="fa-brands fa-steam"></i>
                                                        <span class="label">Run From</span>
                                                        <span class="value">${info.work_on || 'Steam'}</span>
                                                    </div>
                                                    ${info.launcher && info.launcher !== 'None' ? `
                                                    <div class="info-col">
                                                        <i class="fa-solid fa-rocket"></i>
                                                        <span class="label">Requires</span>
                                                        <span class="value">${info.launcher}</span>
                                                    </div>` : ''}
                                                </div>
                                            </div>
                                        `;
                                    } else if (msgEl) {
                                        msgEl.innerHTML = `
                                            <div class="steamlord-success-container">
                                                <div class="steamlord-success-title">
                                                    <i class="fa-solid fa-shield-check"></i> ${lt('Bypass Added Successfully!')}
                                                </div>
                                            </div>
                                        `;
                                    }
                                } else {
                                    // Remove mode
                                    if (msgEl) msgEl.textContent = lt('Done! Verifying game files...');
                                    setTimeout(function () {
                                        window.location.href = 'steam://validate/' + appid;
                                    }, 1000);
                                }
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn primary';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            } else if (state.status === 'failed') {
                                clearInterval(timer);
                                window.steamlord.TaskManager.finishTask('bypass');

                                const errorMsg = state.error || 'Unknown';
                                if (msgEl) {
                                    if (errorMsg.includes('Upgrade Now') || errorMsg.includes('Premium')) {
                                        msgEl.innerHTML = `
                                            <div style="display:flex; flex-direction:column; align-items:center; gap:15px; padding:10px;">
                                                <div style="color:#ef4444; font-weight:bold; font-size:15px;">${lt('Failed: {error}').replace('{error}', errorMsg)}</div>
                                                <a href="https://discord.gg/Uk9MzzHjcr" target="_blank" class="steamlord-btn primary" style="padding:10px 20px; font-size:14px; text-decoration:none;">
                                                    <i class="fa-brands fa-discord" style="margin-right:8px;"></i> ${lt('Upgrade Now')}
                                                </a>
                                            </div>
                                        `;
                                    } else {
                                        msgEl.textContent = lt('Failed: {error}').replace('{error}', errorMsg);
                                    }
                                }
                                refs.btnRow.innerHTML = '';
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn danger';
                                closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                                closeBtn.onclick = () => refs.overlay.remove();
                                refs.btnRow.appendChild(closeBtn);
                            }
                        } else if (isMinimized) {
                            if (state.status === 'done' || state.status === 'failed') {
                                window.steamlord.TaskManager.restore('bypass');
                            }
                        }
                    }
                });
            }, 1000);
        });
    }

    function showAddGameModal(appid, gameName) {
        window.steamlord.TaskManager.startTask('game', appid, () => {
            let refs = null;
            let polling = true;
            const displayName = gameName || lt('game');

            function createModal() {
                refs = createGlassModal(
                    'SteamLord - Menu',
                    '<div id="steamlord-add-body">' + lt('Adding {game}...').replace('{game}', displayName) + '</div>',
                    [{
                        text: lt('Hide'),
                        variant: 'primary',
                        onClick: () => {
                            if (refs && refs.overlay) refs.overlay.remove();
                            // Register restore callback
                            window.steamlord.TaskManager.minimize('game', appid, () => {
                                createModal(); // Re-create when restored
                            });
                        }
                    }]
                );
            }

            createModal();

            const timer = setInterval(() => {
                // Check if we are still the active task
                const active = window.steamlord.TaskManager.active['game'];
                if (!active || active.appid !== appid) {
                    clearInterval(timer);
                    if (refs && refs.overlay && document.body.contains(refs.overlay)) refs.overlay.remove();
                    return;
                }

                const isMinimized = active.minimized;

                Millennium.callServerMethod('steamlord', 'SteamLordAddStatus', { appid, contentScriptQuery: '' }).then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    const st = payload && payload.state ? payload.state : {};

                    // Handle Modal Updates if visible
                    if (!isMinimized && refs && document.body.contains(refs.overlay)) {
                        const bodyEl = document.getElementById('steamlord-add-body');

                        if (st.status === 'done') {
                            clearInterval(timer);
                            window.steamlord.TaskManager.finishTask('game');

                            // Reuse existing modal if visible
                            if (bodyEl) {
                                bodyEl.innerHTML = `
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold; color: #a4d007; margin-bottom: 10px;">
                                            <i class="fa-solid fa-check-circle"></i> ${lt('Game Has Been Added Successfully')}
                                        </div>
                                    </div>
                                `;

                                // Update buttons
                                refs.btnRow.innerHTML = '';

                                // Restart Steam Button
                                const restartBtn = document.createElement('a');
                                restartBtn.className = 'steamlord-btn primary';
                                restartBtn.innerHTML = '<span>' + lt('Restart Steam') + '</span>';
                                restartBtn.onclick = () => {
                                    Millennium.callServerMethod('steamlord', 'RestartSteam', { contentScriptQuery: '' });
                                    refs.overlay.remove();
                                };
                                refs.btnRow.appendChild(restartBtn);

                                // Restart Later/Close Button
                                const closeBtn = document.createElement('a');
                                closeBtn.className = 'steamlord-btn';
                                closeBtn.innerHTML = '<span>' + lt('Restart Later') + '</span>';
                                closeBtn.onclick = () => {
                                    refs.overlay.remove();
                                    showRestartBanner();
                                };
                                refs.btnRow.appendChild(closeBtn);
                            } else {
                                // Fallback if somehow not available (e.g. glitch)
                                refs.overlay.remove();
                                showSuccessRestartModal(lt('Game Has Been Added Successfully'));
                            }
                            addSteamLordButton();
                        } else if (st.status === 'failed') {
                            clearInterval(timer);
                            window.steamlord.TaskManager.finishTask('game');

                            const errorMsg = st.error || 'Unknown error';
                            if (bodyEl) {
                                if (errorMsg.includes('Upgrade Now') || errorMsg.includes('Premium')) {
                                    bodyEl.innerHTML = `
                                        <div style="display:flex; flex-direction:column; align-items:center; gap:15px; padding:10px;">
                                            <div style="color:#ef4444; font-weight:bold; font-size:15px;">${errorMsg}</div>
                                            <a href="https://discord.gg/Uk9MzzHjcr" target="_blank" class="steamlord-btn primary" style="padding:10px 20px; font-size:14px; text-decoration:none;">
                                                <i class="fa-brands fa-discord" style="margin-right:8px;"></i> ${lt('Upgrade Now')}
                                            </a>
                                        </div>
                                    `;
                                } else {
                                    bodyEl.textContent = errorMsg;
                                }
                            }
                            refs.btnRow.innerHTML = '';
                            const closeBtn = document.createElement('a');
                            closeBtn.className = 'steamlord-btn danger';
                            closeBtn.innerHTML = '<span>' + lt('Close') + '</span>';
                            closeBtn.onclick = () => refs.overlay.remove();
                            refs.btnRow.appendChild(closeBtn);
                        }
                        else if (st.status === 'downloading') {
                            if (bodyEl) {
                                // FIX: Validate totalBytes to prevent astronomical percentages
                                const pct = (st.totalBytes > 1000) ? ((st.bytesRead / st.totalBytes) * 100).toFixed(0) : 0;

                                bodyEl.innerHTML = `
                                    <div class="steamlord-download-status">
                                        <span class="steamlord-download-text">${lt('Adding {game}...').replace('{game}', displayName)}</span>
                                        <span class="steamlord-download-percent">${pct}%</span>
                                    </div>
                                    <div class="steamlord-progress-bar-container">
                                        <div class="steamlord-progress-bar-fill" style="width:${pct}%"></div>
                                    </div>
                                `;
                            }
                        }
                        else if (st.status) {
                            if (bodyEl) bodyEl.textContent = lt('Adding {game}...').replace('{game}', displayName) + ' (' + st.status + ')';
                        }
                    } else if (isMinimized) {
                        // Update Dock Icon (Optional: maybe spinning border or badge?)
                        // For now we just keep the loop running so it doesn't die
                        if (st.status === 'done' || st.status === 'failed') {
                            // If it finishes while minimized, we should probably notify user?
                            // For simplicty, bring back modal to show result
                            window.steamlord.TaskManager.restore('game');
                        }
                    }
                });
            }, 1000);
        });
    }

    // Retry wrapper for API calls
    function callWithRetry(methodName, params, maxRetries) {
        maxRetries = maxRetries || 3;
        return new Promise(function (resolve, reject) {
            var attempts = 0;
            function attempt() {
                attempts++;
                Millennium.callServerMethod('steamlord', methodName, params)
                    .then(resolve)
                    .catch(function (err) {
                        if (attempts < maxRetries) {
                            setTimeout(attempt, 1000 * attempts);
                        } else {
                            reject(err);
                        }
                    });
            }
            attempt();
        });
    }

    function addSteamLordButton() {
        // Try multiple containers (SteamDB, Steam native)
        var steamdbContainer = document.querySelector('.steamdb-buttons') ||
            document.querySelector('[data-steamdb-buttons]') ||
            document.querySelector('.apphub_OtherSiteInfo');

        // Fallback: Create our own container if none exists
        if (!steamdbContainer) {
            var purchaseArea = document.querySelector('.game_area_purchase_game') ||
                document.querySelector('.game_purchase_action') ||
                document.querySelector('.game_area_purchase');
            if (purchaseArea && purchaseArea.parentNode) {
                steamdbContainer = document.createElement('div');
                steamdbContainer.className = 'steamlord-buttons-container';
                steamdbContainer.style.cssText = 'display:flex; gap:5px; margin:10px 0; flex-wrap:wrap;';
                purchaseArea.parentNode.insertBefore(steamdbContainer, purchaseArea);
            }
        }

        if (!steamdbContainer) return false;

        var match = window.location.href.match(/https:\/\/store\.steampowered\.com\/app\/(\d+)/) || window.location.href.match(/https:\/\/steamcommunity\.com\/app\/(\d+)/);
        var appid = match ? parseInt(match[1], 10) : NaN;
        if (isNaN(appid)) return false;

        if (typeof Millennium !== 'undefined') {
            callWithRetry('SteamLordFound', { appid: appid, contentScriptQuery: '' }, 3).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                const exists = payload && payload.success && payload.exists;

                const existingButtons = document.querySelectorAll('.steamlord-injected-btn');
                existingButtons.forEach(btn => btn.remove());

                if (exists) {
                    // 1. In Library
                    const libBtn = createButton(lt('In Library'), 'fa-book', function (e) {
                        e.preventDefault();
                        // Try to navigate
                        window.location.href = 'steam://nav/games/details/' + appid;

                        // Show modal
                        createGlassModal('SteamLord',
                            `
                            <div style="text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #c94a4a; margin-bottom: 10px;">
                                    ${lt('Game Not Found in Library')}
                                </div>
                                <div style="color: #c5c6c7;">
                                    ${lt('Restart Steam Until The Changes Appear')}
                                </div>
                            </div>
                            `,
                            [{ text: lt('Close') }]
                        );
                    });
                    steamdbContainer.appendChild(libBtn);

                    // 2. Remove Game
                    const removeBtn = createButton(lt('Remove Game'), 'fa-trash', function (e) {
                        e.preventDefault();
                        if (!requireLicense()) return; // License check
                        showSteamLordConfirm(lt('Are you sure you want to remove this game?'), function () {
                            Millennium.callServerMethod('steamlord', 'SteamLordDelete', { appid, contentScriptQuery: '' }).then(function (r) {
                                const p = typeof r === 'string' ? JSON.parse(r) : r;
                                if (p && p.success) {
                                    showSuccessRestartModal(lt('Game has Been Removed Successfully'));
                                    addSteamLordButton();
                                } else {
                                    showSteamLordAlert(lt('Failed to remove game.'));
                                }
                            });
                        });
                    });
                    steamdbContainer.appendChild(removeBtn);

                    // 3. Online Fix
                    const fixBtn = createButton(lt('Online Fix'), 'fa-wrench', function (e) {
                        e.preventDefault();
                        if (!requireLicense()) return; // License check
                        const gameNameEl = document.querySelector('.apphub_AppName') || document.querySelector('#appHubAppName');
                        const gameName = gameNameEl ? gameNameEl.textContent.trim() : 'Unknown';
                        showOnlineFixPopup(appid, gameName);
                    });
                    steamdbContainer.appendChild(fixBtn);

                    // 4. Baypass
                    const bypassBtn = createButton(lt('Baypass'), 'fa-shield-halved', function (e) {
                        e.preventDefault();
                        if (!requireLicense()) return; // License check
                        const gameNameEl = document.querySelector('.apphub_AppName') || document.querySelector('#appHubAppName');
                        const gameName = gameNameEl ? gameNameEl.textContent.trim() : 'Unknown';
                        showBypassPopup(appid, gameName);
                    });
                    steamdbContainer.appendChild(bypassBtn);

                } else {
                    const addBtn = createButton(lt('Add'), 'fa-plus', function (e) {
                        e.preventDefault();
                        if (!requireLicense()) return; // License check

                        // Get Game Name
                        const gameNameEl = document.querySelector('.apphub_AppName') || document.querySelector('#appHubAppName');
                        const gameName = gameNameEl ? gameNameEl.textContent.trim() : '';

                        // Pre-book the task to prevent multiple concurrent downloads
                        window.steamlord.TaskManager.startTask('game', appid, () => {
                            Millennium.callServerMethod('steamlord', 'SteamLordAdd', { appid, contentScriptQuery: '' });
                            showAddGameModal(appid, gameName);
                        });
                    });
                    steamdbContainer.appendChild(addBtn);
                }
            }).catch(function (err) {
                backendLog('SteamLord: SteamLordFound failed after retries: ' + err);
            });
        }
        return true;
    }

    function createButton(text, iconClass, onClick) {
        const btn = document.createElement('a');
        btn.className = 'btnv6_blue_hoverfade btn_medium steamlord-injected-btn';
        btn.href = '#';
        btn.style.marginLeft = '5px';
        btn.innerHTML = '<span><i class="fa-solid ' + iconClass + '" style="margin-right:5px;"></i>' + text + '</span>';
        btn.onclick = onClick;
        return btn;
    }

    ensureFontAwesome();

    // --------------------------------------------------------------------------
    // STEAMLORD UI STYLES & TASK MANAGER
    // --------------------------------------------------------------------------
    (function injectStyles() {
        const styleId = 'steamlord-styles-v2';
        if (document.getElementById(styleId)) return;
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .steamlord-dock-container {
                position: fixed;
                right: 0;
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                flex-direction: column;
                gap: 0;
                z-index: 99999;
                pointer-events: none;
            }
            .steamlord-dock-item {
                width: 60px;
                padding: 15px 10px;
                background: linear-gradient(135deg, rgba(23, 32, 45, 0.98), rgba(30, 42, 60, 0.95));
                border: 1px solid rgba(102, 192, 244, 0.4);
                border-right: none;
                border-radius: 12px 0 0 12px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                gap: 8px;
                color: #66c0f4;
                cursor: pointer;
                position: relative;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                backdrop-filter: blur(10px);
                box-shadow: -4px 0 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
                pointer-events: auto;
                margin-bottom: 5px;
            }
            .steamlord-dock-item:hover {
                width: 70px;
                border-color: #66c0f4;
                box-shadow: -4px 0 30px rgba(102, 192, 244, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                background: linear-gradient(135deg, rgba(30, 42, 60, 0.98), rgba(40, 55, 75, 0.95));
            }
            .steamlord-dock-item i {
                font-size: 24px;
                text-shadow: 0 0 12px rgba(102, 192, 244, 0.6);
            }
            .steamlord-dock-badge {
                position: absolute;
                top: 5px;
                right: 5px;
                background: linear-gradient(135deg, #66c0f4, #4a9eda);
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 2px solid #17202d;
                animation: steamlordPulse 1.5s ease-in-out infinite;
                box-shadow: 0 0 8px rgba(102, 192, 244, 0.8);
            }
            @keyframes steamlordPulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.2); opacity: 0.8; }
            }
            .steamlord-dock-queue-badge {
                position: absolute;
                bottom: 8px;
                left: 8px;
                background: linear-gradient(135deg, #f59e0b, #d97706);
                min-width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #17202d;
                font-size: 9px;
                font-weight: bold;
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0 4px;
            }
            .steamlord-progress-bar-container {
                width: 100%;
                height: 8px;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 4px;
                margin-top: 12px;
                overflow: hidden;
                border: 1px solid rgba(102, 192, 244, 0.2);
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
            }
            .steamlord-progress-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #4a9eda, #66c0f4, #8ed3fc, #66c0f4, #4a9eda);
                background-size: 200% 100%;
                width: 0%;
                transition: width 0.3s ease;
                box-shadow: 0 0 15px rgba(102, 192, 244, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                animation: steamlordProgressGlow 2s linear infinite;
            }
            @keyframes steamlordProgressGlow {
                0% { background-position: 0% 50%; }
                100% { background-position: 200% 50%; }
            }
            .steamlord-download-status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            .steamlord-download-text {
                color: #c5c6c7;
                font-size: 14px;
            }
            .steamlord-download-percent {
                color: #66c0f4;
                font-size: 18px;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(102, 192, 244, 0.5);
            }
            .steamlord-queue-info {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 12px;
                padding: 8px 12px;
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 6px;
                font-size: 12px;
                color: #f59e0b;
            }
            .steamlord-queue-info i {
                font-size: 14px;
            }
        `;
        document.head.appendChild(style);
    })();

    // Task Manager (No Queue - Single Task Only)
    window.steamlord = window.steamlord || {};
    window.steamlord.TaskManager = {
        active: {
            'game': null, // { appid, minimized, restoreFn }
            'fix': null,
            'bypass': null
        },
        ignoreList: [], // { type, appid, timestamp }

        addToIgnore: function (type, appid) {
            this.ignoreList.push({ type, appid, timestamp: Date.now() });
            // Keep list small
            if (this.ignoreList.length > 20) this.ignoreList.shift();
        },

        shouldIgnore: function (type, appid) {
            // Ignore if in list and added less than 30 seconds ago
            // This formatting prevents the backend from restoring a just-finished task
            const found = this.ignoreList.find(x => x.type === type && x.appid === appid);
            if (found && (Date.now() - found.timestamp < 30000)) {
                return true;
            }
            return false;
        },

        startTask: function (type, appid, startFn) {
            // Check if truly active (not null and not finished)
            if (this.active[type] && this.active[type].appid) {
                // If same AppID, allow resume/restore UI
                if (this.active[type].appid === appid) {
                    this.active[type].minimized = false;
                    startFn();
                    this.renderDock();
                    return true;
                }

                // Different AppID - show busy message
                const typeLabels = { 'game': lt('game download'), 'fix': lt('fix'), 'bypass': lt('bypass') };
                showSteamLordAlert(lt('Download in progress. Please wait for the current {type} to finish.').replace('{type}', typeLabels[type] || type));
                return false;
            }
            // Start locally
            this.active[type] = { appid, minimized: false };
            startFn();
            this.renderDock(); // Update dock state
            return true;
        },

        finishTask: function (type) {
            if (this.active[type]) {
                this.addToIgnore(type, this.active[type].appid);
            }
            this.active[type] = null;
            this.renderDock();
        },

        minimize: function (type, appid, restoreFn) {
            if (this.active[type] && this.active[type].appid === appid) {
                this.active[type].minimized = true;
                this.active[type].restoreFn = restoreFn;
                this.renderDock();
            }
        },

        restore: function (type) {
            if (this.active[type] && this.active[type].minimized) {
                this.active[type].minimized = false;
                if (this.active[type].restoreFn) this.active[type].restoreFn();
                this.active[type].restoreFn = null;
                this.renderDock();
            }
        },

        renderDock: function () {
            let container = document.querySelector('.steamlord-dock-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'steamlord-dock-container';
                document.body.appendChild(container);
            }

            container.innerHTML = '';

            let hasItems = false;
            const types = ['game', 'fix', 'bypass'];
            const icons = { 'game': 'fa-download', 'fix': 'fa-wrench', 'bypass': 'fa-shield-halved' };
            const titles = { 'game': lt('Game Download'), 'fix': lt('Online Fix'), 'bypass': lt('Bypass') };

            types.forEach(type => {
                if (this.active[type] && this.active[type].minimized && this.active[type].appid) {
                    hasItems = true;
                    const item = document.createElement('div');
                    item.className = 'steamlord-dock-item';
                    item.title = titles[type] + ' - ' + lt('Click to Show');

                    const icon = icons[type];

                    item.innerHTML = `
                        <i class="fa-solid ${icon}"></i>
                        <span class="steamlord-dock-badge"></span>
                    `;
                    item.onclick = () => this.restore(type);
                    container.appendChild(item);
                }
            });

            // Hide container if empty
            if (!hasItems) {
                container.style.display = 'none';
            } else {
                container.style.display = 'flex';
            }
        }
    };

    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    ensureFontAwesome();

    // Improved Observer: watches multiple containers
    var observerDebounceTimer = null;
    var observer = new MutationObserver(function (mutations) {
        // Debounce to prevent excessive calls
        if (observerDebounceTimer) clearTimeout(observerDebounceTimer);
        observerDebounceTimer = setTimeout(function () {
            var hasContainer = document.querySelector('.steamdb-buttons') ||
                document.querySelector('.apphub_OtherSiteInfo') ||
                document.querySelector('.game_area_purchase_game') ||
                document.querySelector('.steamlord-buttons-container');
            var hasButtons = document.querySelector('.steamlord-injected-btn');

            if (hasContainer && !hasButtons) {
                addSteamLordButton();
            }
        }, 100);
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Safety interval: backup check for first 10 seconds
    var safetyChecks = 0;
    var safetyInterval = setInterval(function () {
        safetyChecks++;
        var hasButtons = document.querySelector('.steamlord-injected-btn');
        if (!hasButtons) {
            addSteamLordButton();
        }
        if (safetyChecks >= 5 || hasButtons) {
            clearInterval(safetyInterval);
        }
    }, 2000);

    // Initial call on page load
    setTimeout(function () {
        if (!document.querySelector('.steamlord-injected-btn')) {
            addSteamLordButton();
        }
    }, 500);

    function showNotification(title, message, iconUrl) {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.background = 'rgba(23, 32, 45, 0.95)';
        toast.style.border = '1px solid rgba(102, 192, 244, 0.3)';
        toast.style.borderRadius = '8px';
        toast.style.padding = '15px';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '15px';
        toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
        toast.style.zIndex = '100000';
        toast.style.minWidth = '300px';
        toast.style.animation = 'steamlordFadeIn 0.5s ease-out';
        toast.style.backdropFilter = 'blur(10px)';

        let iconHtml = '';
        if (iconUrl) {
            iconHtml = `<img src="${iconUrl}" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;">`;
        } else {
            iconHtml = `<i class="fa-brands fa-steam" style="font-size: 30px; color: #66c0f4;"></i>`;
        }

        toast.innerHTML = `
            ${iconHtml}
            <div style="flex: 1;">
                <div style="font-weight: bold; color: #fff; margin-bottom: 4px;">${title}</div>
                <div style="font-size: 13px; color: #c5c6c7;">${message}</div>
            </div>
            <div style="cursor: pointer; color: #666;" onclick="this.parentElement.remove()">
                <i class="fa-solid fa-xmark"></i>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 10 seconds
        setTimeout(() => {
            if (document.body.contains(toast)) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(10px)';
                toast.style.transition = 'all 0.5s ease';
                setTimeout(() => toast.remove(), 500);
            }
        }, 10000);
    }

    function checkRequestedGames() {
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'CheckAvailableRequestedGames', { contentScriptQuery: '' }).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && Array.isArray(payload.games)) {
                    payload.games.forEach(game => {
                        // Fetch icon if possible, for now use default or try to get it
                        // We can try to construct a steam CDN url if we had the hash, but we don't.
                        // We'll use a generic icon or try to fetch from store API in frontend?
                        // Actually, let's just use the default icon or if backend provided one.
                        // Backend provided 'name'.

                        // Try to get header image
                        const iconUrl = `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/header.jpg`;

                        showNotification(
                            game.name,
                            lt('Game is Available for Add Now'),
                            iconUrl
                        );
                    });
                }
            });
        }
    }

    function startGlobalPoll() {
        // 1. Try to inject SteamLord buttons if on Store page
        addSteamLordButton();

        // 2. Check for Restart Banner Persistence (Global)
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'IsRestartRequired', { contentScriptQuery: '' }).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && payload.required) {
                    showRestartBanner(true); // true = skip setting flag again
                }
            });

            // 3. Check for active downloads and restore dock
            checkActiveDownloadsFromBackend();
        }

        setTimeout(startGlobalPoll, 1000);
    }

    function checkActiveDownloadsFromBackend() {
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'GetActiveDownloads', { contentScriptQuery: '' }).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && payload.active) {
                    const activeGroups = payload.active;

                    // Iterate over types: game, fix, bypass
                    Object.keys(activeGroups).forEach(type => {
                        const items = activeGroups[type];
                        if (Array.isArray(items)) {
                            items.forEach(item => {
                                const appid = item.appid;
                                // If not currently tracking this task
                                if (!window.steamlord.TaskManager.active[type] || window.steamlord.TaskManager.active[type].appid !== appid) {
                                    // Check if we should ignore (just finished)
                                    if (window.steamlord.TaskManager.shouldIgnore(type, appid)) {
                                        return;
                                    }

                                    // Restore it as minimized
                                    window.steamlord.TaskManager.active[type] = {
                                        appid: appid,
                                        minimized: true,
                                        restoreFn: createRestoreFn(type, appid)
                                    };
                                }
                            });
                        }
                    });

                    // Render dock to show the restored items
                    window.steamlord.TaskManager.renderDock();
                }
            });
        }
    }

    function createRestoreFn(type, appid) {
        // Helper to recreate the correct restore function based on type
        return function () {
            if (type === 'game') showAddGameModal(appid);
            if (type === 'fix') showFixDownloadProgress(appid, 'fix');
            if (type === 'bypass') showBypassProgress(appid, 'apply'); // Assume apply for restored sessions
        };
    }

    function checkPendingAddedGames() {
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'GetPendingAddedGames', { contentScriptQuery: '' }).then(function (res) {
                const payload = typeof res === 'string' ? JSON.parse(res) : res;
                if (payload && payload.success && Array.isArray(payload.games) && payload.games.length > 0) {

                    const listHtml = payload.games.map(g =>
                        `<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px; padding:8px; background:rgba(0,0,0,0.3); border-radius:8px;">
                            <i class="fa-solid fa-check-circle" style="color:#4caf50; font-size:16px;"></i>
                            <span style="color:#fff; font-weight:500;">${g.name}</span>
                         </div>`
                    ).join('');

                    const modalHtml = `
                        <div class="steamlord-glass-overlay">
                            <div class="steamlord-glass-modal" style="min-width:450px;">
                                <div class="steamlord-modal-content">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <h3 style="margin:0; color:#fff; font-size:20px;">
                                            <i class="fa-solid fa-layer-group" style="color:#66c0f4; margin-right:10px;"></i>
                                            ${lt('Games Added Successfully')}
                                        </h3>

                                    </div>
                                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin:10px 0;">
                                        <div style="color:#ccc; margin-bottom:10px; font-size:14px;">
                                            ${lt('Games That Have Been Added')}
                                        </div>
                                        <div style="max-height:250px; overflow-y:auto; padding-right:5px;">
                                            ${listHtml}
                                        </div>
                                    </div>
                                    <div style="display:flex; justify-content:flex-end; gap:10px;">
                                        <a href="steam://nav/games" class="steamlord-btn" style="background:rgba(255,255,255,0.1); margin-right:auto;" onclick="this.closest('.steamlord-glass-overlay').remove();">
                                            <i class="fa-solid fa-gamepad" style="margin-right:5px;"></i> ${lt('Go to Library')}
                                        </a>
                                        <a href="#" class="steamlord-btn primary" onclick="this.closest('.steamlord-glass-overlay').remove(); return false;">
                                            ${lt('Close')}
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;

                    const range = document.createRange();
                    const frag = range.createContextualFragment(modalHtml);
                    document.body.appendChild(frag);
                }
            });
        }
    }

    // Check for games added in previous session
    setTimeout(checkPendingAddedGames, 1000);

    // Check for availability of requested games
    function checkRequestedGames() {
        if (typeof Millennium !== 'undefined') {
            Millennium.callServerMethod('steamlord', 'CheckAvailableRequestedGames', { contentScriptQuery: '' })
                .then(function (res) {
                    const payload = typeof res === 'string' ? JSON.parse(res) : res;
                    if (payload && payload.success && Array.isArray(payload.games)) {
                        payload.games.forEach(game => {
                            // game object has { appid, name }
                            // Try to get header image
                            const iconUrl = `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/header.jpg`;

                            showAvailableGameNotification(game.appid, game.name || `Game ${game.appid}`, iconUrl);
                        });
                    }
                })
                .catch(function (err) {
                    console.error('[SteamLord] Failed to check requested games:', err);
                });
        }
    }

    // Start the global poll loop
    startGlobalPoll();

    // Run availability check shortly after load (faster speed)
    setTimeout(checkRequestedGames, 1000);


    // --- NOTIFICATION HANDLER FOR REQUESTED GAMES (COMPACT) ---
    function showAvailableGameNotification(appid, gameName) {
        // Stacking logic: Count existing toasts
        const existingToasts = document.querySelectorAll('.steamlord-toast');
        const stackIndex = existingToasts.length;
        const bottomOffset = 20 + (stackIndex * 80); // reduced height 80px per toast

        const toast = document.createElement('div');
        toast.className = 'steamlord-toast';
        toast.style.bottom = bottomOffset + 'px';
        toast.style.minHeight = 'auto';
        toast.style.cursor = 'pointer'; // Make it clickable

        // Simplified content, no buttons
        toast.innerHTML = `
            <div class="steamlord-toast-body" style="padding: 12px 16px; flex-direction:column; align-items:flex-start; gap:4px;">
                <div class="steamlord-toast-content" style="width:100%">
                    <div class="steamlord-toast-subtitle" style="color:#66c0f4; font-size:10px; font-weight:bold; letter-spacing:1px;">AVAILABLE NOW</div>
                    <div class="steamlord-toast-title" style="font-size:14px; margin:0; line-height:1.2;">${gameName}</div>
                    <div class="steamlord-toast-msg" style="font-size:11px; opacity:0.6; margin-top:2px;">Click to dismiss</div>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Click to dismiss
        toast.onclick = function () {
            removeToast(toast);
        };

        // Auto remove after 60 seconds
        setTimeout(() => {
            if (document.body.contains(toast)) {
                removeToast(toast);
            }
        }, 60000);

        // Sound
        try {
            const audio = new Audio('https://steamloopback.host/sounds/beeps_01.wav');
            audio.volume = 0.4;
            audio.play().catch(e => { });
        } catch (e) { }
    }

    function removeToast(toast) {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => {
            if (document.body.contains(toast)) toast.remove();
            repositionToasts();
        }, 300);
    }

    function repositionToasts() {
        const toasts = document.querySelectorAll('.steamlord-toast');
        toasts.forEach((t, index) => {
            const newBottom = 20 + (index * 80);
            t.style.bottom = newBottom + 'px';
        });
    }

    window.steamlord = window.steamlord || {};
    window.steamlord.GameAvailable = function (payloadStr) {
        try {
            const payload = typeof payloadStr === 'string' ? JSON.parse(payloadStr) : payloadStr;
            const appid = payload.appid;

            // Fetch game name from Steam API if possible
            fetch(`https://store.steampowered.com/api/appdetails?appids=${appid}&filters=basic`)
                .then(r => r.json())
                .then(data => {
                    let gameName = `Game ${appid}`;
                    if (data && data[appid] && data[appid].success && data[appid].data) {
                        gameName = data[appid].data.name;
                    }
                    // Call without image url
                    showAvailableGameNotification(appid, gameName);
                })
                .catch(() => {
                    showAvailableGameNotification(appid, `Game ${appid}`);
                });
        } catch (e) {
            console.error('GameAvailable error', e);
        }
    };

})();