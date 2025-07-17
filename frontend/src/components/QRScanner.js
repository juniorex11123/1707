import React, { useState, useEffect, useRef } from 'react';
import QrScanner from 'qr-scanner';

function QRScanner({ onScan, loading, disabled }) {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [isProcessing, setIsProcessing] = useState(false);
  const [cooldownTimer, setCooldownTimer] = useState(0);
  const [lastScannedCode, setLastScannedCode] = useState(null);
  const [lastScanTime, setLastScanTime] = useState(0);
  const [autoStartEnabled, setAutoStartEnabled] = useState(true);
  const videoRef = useRef(null);
  const qrScannerRef = useRef(null);
  const cooldownIntervalRef = useRef(null);
  const isProcessingRef = useRef(false);
  const lastScannedCodeRef = useRef(null);

  useEffect(() => {
    // Automatically start scanning when component mounts
    if (autoStartEnabled && !disabled) {
      startScanning();
    }
    
    return () => {
      stopScanning();
      if (cooldownIntervalRef.current) {
        clearInterval(cooldownIntervalRef.current);
      }
    };
  }, []);

  // Sync refs with state
  useEffect(() => {
    isProcessingRef.current = isProcessing;
  }, [isProcessing]);

  useEffect(() => {
    lastScannedCodeRef.current = lastScannedCode;
  }, [lastScannedCode]);

  const startCooldown = () => {
    // Stop scanning immediately after detecting QR code
    if (qrScannerRef.current) {
      qrScannerRef.current.stop();
    }
    
    setCooldownTimer(5);
    setIsProcessing(true);
    isProcessingRef.current = true;
    
    if (cooldownIntervalRef.current) {
      clearInterval(cooldownIntervalRef.current);
    }
    
    cooldownIntervalRef.current = setInterval(() => {
      setCooldownTimer(prev => {
        if (prev <= 1) {
          clearInterval(cooldownIntervalRef.current);
          setIsProcessing(false);
          isProcessingRef.current = false;
          setLastScannedCode(null);
          lastScannedCodeRef.current = null;
          
          // Automatically restart scanning after cooldown if auto-start is enabled
          if (autoStartEnabled && !disabled) {
            setTimeout(() => {
              startScanning();
            }, 100); // Shorter delay to ensure immediate restart
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const startScanning = async () => {
    try {
      setError(null);
      setIsScanning(true);

      if (qrScannerRef.current) {
        qrScannerRef.current.destroy();
      }

      const qrScanner = new QrScanner(
        videoRef.current,
        (result) => {
          if (result && result.data) {
            const currentTime = Date.now();
            
            console.log('QR Code detected:', result.data);
            
            // Prevent rapid successive scans (minimum 1 second between scans)
            if (currentTime - lastScanTime < 1000) {
              console.log('Too rapid scanning, ignoring...');
              return;
            }
            
            // Prevent scanning the same code during processing
            if (lastScannedCodeRef.current === result.data && isProcessingRef.current) {
              console.log('Same code detected during cooldown, ignoring...');
              return;
            }
            
            // Prevent multiple scans during processing
            if (isProcessingRef.current || loading) {
              console.log('Processing in progress, ignoring scan...');
              return;
            }
            
            setLastScanTime(currentTime);
            setLastScannedCode(result.data);
            lastScannedCodeRef.current = result.data;
            
            // Call the scan handler
            onScan(result.data);
            
            // Start cooldown which will stop the scanner
            startCooldown();
          }
        },
        {
          onDecodeError: (err) => {
            // Ignore decode errors as they're common during scanning
            // console.log('Decode error (normal during scanning):', err);
          },
          preferredCamera: facingMode,
          highlightScanRegion: true,
          highlightCodeOutline: true,
          returnDetailedScanResult: true,
          maxScansPerSecond: 2, // Limit scan frequency
        }
      );

      qrScannerRef.current = qrScanner;
      await qrScanner.start();

    } catch (err) {
      console.error('Error starting QR scanner:', err);
      setError('Nie można uzyskać dostępu do kamery. Sprawdź uprawnienia.');
      setIsScanning(false);
    }
  };

  const stopScanning = () => {
    if (qrScannerRef.current) {
      qrScannerRef.current.destroy();
      qrScannerRef.current = null;
    }
    setIsScanning(false);
    if (cooldownIntervalRef.current) {
      clearInterval(cooldownIntervalRef.current);
      setCooldownTimer(0);
      setIsProcessing(false);
      isProcessingRef.current = false;
    }
    setLastScannedCode(null);
    lastScannedCodeRef.current = null;
  };

  const toggleCamera = async () => {
    if (isProcessing) {
      setError('Nie można przełączyć kamery podczas przetwarzania');
      return;
    }

    const newFacingMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(newFacingMode);
    
    if (qrScannerRef.current) {
      try {
        await qrScannerRef.current.setCamera(newFacingMode);
      } catch (err) {
        console.error('Error switching camera:', err);
        setError('Nie można przełączyć kamery');
      }
    }
  };

  const handleStartStop = () => {
    if (isProcessing) {
      return; // Don't allow starting/stopping during processing
    }
    
    if (isScanning) {
      stopScanning();
      setAutoStartEnabled(false); // Disable auto-start when manually stopped
    } else {
      setAutoStartEnabled(true); // Enable auto-start when manually started
      startScanning();
    }
  };

  useEffect(() => {
    if (isScanning && !isProcessing && facingMode) {
      startScanning();
    }
  }, [facingMode]);

  return (
    <div className="qr-scanner-container">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 text-red-800 hover:text-red-900"
          >
            ✕
          </button>
        </div>
      )}

      {/* Cooldown Timer */}
      {cooldownTimer > 0 && (
        <div className="bg-orange-100 border border-orange-400 text-orange-700 px-4 py-3 rounded mb-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">
              Kod został zeskanowany! Automatyczne ponowne uruchomienie za {cooldownTimer} sekund
            </span>
          </div>
        </div>
      )}

      <div className="relative">
        <video
          ref={videoRef}
          className="qr-scanner-video w-full h-64 object-cover rounded-lg"
          style={{ display: (isScanning || isProcessing) ? 'block' : 'none' }}
        />
        
        {!isScanning && !isProcessing && (
          <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
              </svg>
              <p className="text-gray-500">Kamera nie jest aktywna</p>
            </div>
          </div>
        )}

        {/* Processing Overlay */}
        {(loading || isProcessing) && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center rounded-lg">
            <div className="text-center text-white">
              <div className="spinner border-4 border-gray-300 border-t-blue-500 rounded-full w-8 h-8 animate-spin mx-auto mb-2"></div>
              <p className="text-sm font-medium">
                {isProcessing ? `Automatyczne uruchomienie za ${cooldownTimer}s` : 'Przetwarzanie...'}
              </p>
            </div>
          </div>
        )}

        {/* Scan Region Indicator */}
        {(isScanning || isProcessing) && !loading && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-green-500"></div>
            <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-green-500"></div>
            <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-green-500"></div>
            <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-green-500"></div>
            
            {/* Center crosshair */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="w-6 h-6 border-2 border-green-500 bg-green-500/20 rounded"></div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleStartStop}
          disabled={disabled || isProcessing}
          className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
            isScanning
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isProcessing ? `Automatyczne uruchomienie za ${cooldownTimer}s` : (isScanning ? 'Zatrzymaj' : 'Uruchom skaner')}
        </button>

        {isScanning && (
          <button
            onClick={toggleCamera}
            disabled={disabled || isProcessing}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Przełącz kamerę"
          >
            📷
          </button>
        )}
      </div>

      <div className="mt-2 text-sm text-gray-600">
        <p>• Kamera: {facingMode === 'environment' ? 'Tylna' : 'Przednia'}</p>
        <p>• Skaner automatycznie uruchamia się po załadowaniu</p>
        <p>• Automatyczne ponowne uruchomienie po 5 sekundach</p>
        <p>• ⚡ Ulepszona stabilność - brak bugów podczas skanowania</p>
        {isProcessing && (
          <p className="text-orange-600 font-medium">
            • ⏳ Odliczanie: {cooldownTimer} sekund do ponownego uruchomienia
          </p>
        )}
        {!isScanning && !isProcessing && (
          <p className="text-blue-600 font-medium">
            • 🔄 Automatyczne uruchamianie: {autoStartEnabled ? 'Włączone' : 'Wyłączone'}
          </p>
        )}
      </div>
    </div>
  );
}

export default QRScanner;