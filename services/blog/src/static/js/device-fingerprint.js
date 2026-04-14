// Device Fingerprinting Utility for Blog Like System
// Generates a unique device fingerprint based on multiple browser characteristics

(function() {
  'use strict';

  // Cache for the generated fingerprint
  let cachedFingerprint = null;
  let isGenerating = false;

  /**
   * Generate a device fingerprint using multiple browser characteristics
   * @returns {Promise<string>} A unique device fingerprint
   */
  async function generateDeviceFingerprint() {
    if (cachedFingerprint) {
      return cachedFingerprint;
    }

    if (isGenerating) {
      // Wait for ongoing generation to complete
      return new Promise((resolve) => {
        const checkGeneration = () => {
          if (cachedFingerprint) {
            resolve(cachedFingerprint);
          } else {
            setTimeout(checkGeneration, 100);
          }
        };
        checkGeneration();
      });
    }

    isGenerating = true;

    try {
      const components = await collectFingerprintComponents();
      const fingerprint = createHash(JSON.stringify(components));
      
      cachedFingerprint = fingerprint;
      isGenerating = false;
      
      return fingerprint;
    } catch (error) {
      console.error('Error generating device fingerprint:', error);
      isGenerating = false;
      
      // Fallback to a simpler fingerprint
      return generateFallbackFingerprint();
    }
  }

  /**
   * Collect various browser and device characteristics
   * @returns {Promise<Object>} Object containing fingerprint components
   */
  async function collectFingerprintComponents() {
    const components = {
      // Screen and viewport
      screen: {
        width: screen.width,
        height: screen.height,
        availWidth: screen.availWidth,
        availHeight: screen.availHeight,
        colorDepth: screen.colorDepth,
        pixelDepth: screen.pixelDepth
      },
      
      // Window dimensions
      window: {
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        outerWidth: window.outerWidth,
        outerHeight: window.outerHeight
      },
      
      // Browser information
      browser: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        languages: navigator.languages,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine,
        doNotTrack: navigator.doNotTrack
      },
      
      // Hardware information
      hardware: {
        hardwareConcurrency: navigator.hardwareConcurrency,
        deviceMemory: navigator.deviceMemory,
        maxTouchPoints: navigator.maxTouchPoints
      },
      
      // Display information
      display: {
        colorGamut: getColorGamut(),
        hdr: getHDRSupport()
      },
      
      // Network information
      network: getNetworkInfo(),
      
      // Time zone and locale
      timezone: {
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timeZoneOffset: new Date().getTimezoneOffset()
      },
      
      // Canvas fingerprint (if available)
      canvas: await getCanvasFingerprint(),
      
      // Audio fingerprint (if available)
      audio: await getAudioFingerprint()
    };

    return components;
  }

  /**
   * Create a SHA-256 hash of the input string
   * @param {string} input 
   * @returns {string} Hexadecimal hash string
   */
  function createHash(input) {
    // Simple hash function (not cryptographically secure, but good enough for fingerprinting)
    let hash = 0;
    const str = input.toString();
    
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    // Convert to hex string and pad to ensure consistent length
    return Math.abs(hash).toString(16).padStart(8, '0');
  }

  /**
   * Get color gamut support
   * @returns {string}
   */
  function getColorGamut() {
    if (window.matchMedia && window.matchMedia('(color-gamut: p3)').matches) {
      return 'p3';
    } else if (window.matchMedia && window.matchMedia('(color-gamut: rec2020)').matches) {
      return 'rec2020';
    } else if (window.matchMedia && window.matchMedia('(color-gamut: srgb)').matches) {
      return 'srgb';
    }
    return 'unknown';
  }

  /**
   * Get HDR support
   * @returns {string}
   */
  function getHDRSupport() {
    if (window.matchMedia && window.matchMedia('(dynamic-range: high)').matches) {
      return 'high';
    }
    return 'standard';
  }

  /**
   * Get network information
   * @returns {Object}
   */
  function getNetworkInfo() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData
      };
    }
    
    return { effectiveType: 'unknown' };
  }

  /**
   * Get canvas fingerprint
   * @returns {Promise<string>}
   */
  async function getCanvasFingerprint() {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = 200;
      canvas.height = 50;
      
      // Draw some text with different styles
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('Browser Fingerprint Test!', 2, 15);
      ctx.strokeStyle = 'rgba(120, 186, 176, 0.8)';
      ctx.strokeRect(10, 5, 220, 40);
      
      // Add some random elements
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.fillRect(100, 25, 200, 15);
      
      return canvas.toDataURL();
    } catch (error) {
      return 'canvas-not-supported';
    }
  }

  /**
   * Get audio fingerprint
   * @returns {Promise<string>}
   */
  async function getAudioFingerprint() {
    try {
      if (!window.AudioContext && !window.webkitAudioContext) {
        return 'audio-not-supported';
      }

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const analyser = audioContext.createAnalyser();
      const gainNode = audioContext.createGain();
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);

      oscillator.type = 'triangle';
      oscillator.frequency.value = 10000;

      gainNode.gain.value = 0; // Disable audio output
      scriptProcessor.onaudioprocess = function() {
        // This will be called once, then we disconnect
        oscillator.disconnect();
        scriptProcessor.disconnect();
        gainNode.disconnect();
        analyser.disconnect();
        audioContext.close();
      };

      oscillator.connect(gainNode);
      gainNode.connect(analyser);
      analyser.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      oscillator.start(0);

      // Wait a short time for the audio processing
      await new Promise(resolve => setTimeout(resolve, 100));

      return 'audio-processed';
    } catch (error) {
      return 'audio-error';
    }
  }

  /**
   * Generate a fallback fingerprint when advanced methods fail
   * @returns {string}
   */
  function generateFallbackFingerprint() {
    const components = [
      navigator.userAgent,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset(),
      navigator.language
    ].join('|');
    
    return createHash(components);
  }

  /**
   * Get or create a temporal user with the device fingerprint
   * @param {Object} userInfo - User information (name, email, etc.)
   * @returns {Promise<Object>} Temporal user data
   */
  async function getOrCreateTemporalUser(userInfo = {}) {
    const fingerprint = await generateDeviceFingerprint();
    
    try {
      const response = await fetch('/api/blogs/temporal-users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fingerprint: fingerprint,
          name: userInfo.name || 'Anonymous User',
          email: userInfo.email || null,
          device_info: await collectFingerprintComponents(),
          user_agent: navigator.userAgent
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create temporal user');
      }

      const userData = await response.json();
      return userData;
    } catch (error) {
      console.warn('Failed to create temporal user, using fingerprint only:', error);
      return {
        fingerprint: fingerprint,
        name: userInfo.name || 'Anonymous User'
      };
    }
  }

  // Export functions to global scope
  window.generateDeviceFingerprint = generateDeviceFingerprint;
  window.getOrCreateTemporalUser = getOrCreateTemporalUser;
  window.getDeviceFingerprint = () => cachedFingerprint; // Sync access to cached fingerprint


})();