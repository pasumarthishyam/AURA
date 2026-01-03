"""
Offline State Manager - Manages offline mode with auto-detection.
Enables AURA to work seamlessly without internet connection.
"""
import socket
import logging

logger = logging.getLogger("AURA.OfflineState")


class OfflineState:
    """
    Singleton managing offline mode state globally.
    
    Features:
    - Manual offline toggle (user forced)
    - Auto-detection of network availability
    - Quick network checks with caching
    """
    _manual_offline: bool = False  # User forced offline
    _auto_detect: bool = True      # Auto-detection enabled
    _last_check_result: bool = True
    _check_interval: int = 30      # Seconds between network checks
    
    @classmethod
    def is_offline(cls) -> bool:
        """
        Check if in offline mode.
        Returns True if manually set offline OR network unavailable.
        """
        if cls._manual_offline:
            return True
        if cls._auto_detect:
            return not cls._check_network()
        return False
    
    @classmethod
    def set_manual_offline(cls, enabled: bool) -> None:
        """Force offline mode on/off."""
        cls._manual_offline = enabled
        mode = "OFFLINE" if enabled else "AUTO"
        logger.info(f"Manual offline mode set to: {enabled} (mode: {mode})")
    
    @classmethod
    def set_auto_detect(cls, enabled: bool) -> None:
        """Enable/disable auto-detection."""
        cls._auto_detect = enabled
        logger.info(f"Auto-detect set to: {enabled}")
    
    @classmethod
    def _check_network(cls) -> bool:
        """
        Quick network connectivity check.
        Tries to connect to reliable DNS servers.
        """
        try:
            # Try Google DNS (very reliable)
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            cls._last_check_result = True
            return True
        except OSError:
            pass
        
        try:
            # Fallback to Cloudflare DNS
            socket.create_connection(("1.1.1.1", 53), timeout=2)
            cls._last_check_result = True
            return True
        except OSError:
            pass
        
        cls._last_check_result = False
        return False
    
    @classmethod
    def get_status(cls) -> dict:
        """Get full status for API responses."""
        network_available = cls._check_network()
        return {
            "offline_mode": cls.is_offline(),
            "manual_offline": cls._manual_offline,
            "auto_detect": cls._auto_detect,
            "network_available": network_available
        }
    
    @classmethod
    def get_mode_description(cls) -> str:
        """Get human-readable mode description."""
        if cls._manual_offline:
            return "Offline (Manual)"
        if not cls._check_network():
            return "Offline (No Internet)"
        return "Online"
