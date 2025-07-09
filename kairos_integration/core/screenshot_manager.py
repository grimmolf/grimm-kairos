"""
Chart Screenshot Manager for TradingView Automation

Specialized screenshot capture and management for trading charts
with annotation, comparison, and documentation features.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import time

# Add grimm-kairos to path
kairos_path = Path(__file__).parent.parent.parent.parent / "grimm-kairos"
if kairos_path.exists():
    sys.path.insert(0, str(kairos_path))

try:
    from tv.core import ConfigManager, ModernBrowserManager
    from tv.utils import CSSSelectors, TimingUtils
    KAIROS_AVAILABLE = True
except ImportError:
    KAIROS_AVAILABLE = False
    logging.warning("Grimm-kairos not available. Please ensure it's installed and in the Python path.")

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ImageOps import expand
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available. Install with: pip install Pillow")

from .auth_manager import GrimmAuthManager

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotConfiguration:
    """Configuration for screenshot capture."""
    strategy_name: str
    ticker: str = "MNQ1!"
    timeframe: str = "1h"
    chart_style: str = "candles"  # candles, bars, line, area
    theme: str = "dark"  # dark, light
    indicators_visible: bool = True
    drawings_visible: bool = True
    volume_visible: bool = True
    capture_full_page: bool = False
    annotation_enabled: bool = True
    annotation_text: Optional[str] = None
    output_format: str = "png"  # png, jpg
    quality: int = 95
    resize_width: Optional[int] = None
    resize_height: Optional[int] = None


@dataclass
class ScreenshotResult:
    """Result of screenshot capture operation."""
    success: bool
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    capture_time: Optional[datetime] = None
    file_size: int = 0


class ChartScreenshotManager:
    """
    Advanced chart screenshot management for TradingView.
    
    Features:
    - High-quality chart capture
    - Multiple chart styles and themes
    - Automatic annotation
    - Thumbnail generation
    - Metadata extraction
    - Batch processing
    - Screenshot comparison
    """
    
    def __init__(self,
                 auth_manager: GrimmAuthManager,
                 kairos_config: Optional[Dict[str, Any]] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize screenshot manager.
        
        Args:
            auth_manager: Authenticated GrimmAuthManager instance
            kairos_config: Kairos configuration overrides
            output_dir: Directory for screenshot output
        """
        if not KAIROS_AVAILABLE:
            raise ImportError("Grimm-kairos is required for screenshot functionality")
            
        self.auth_manager = auth_manager
        self.output_dir = Path(output_dir or "./screenshots")
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup Kairos configuration
        self.config = ConfigManager()
        if kairos_config:
            for key, value in kairos_config.items():
                self.config.set(key, value)
                
        self._configure_defaults()
        
        # Initialize components
        self.browser_manager = None
        self.selectors = CSSSelectors()
        
        # Screenshot settings
        self.default_dimensions = (1920, 1080)
        self.thumbnail_size = (400, 300)
        
    def _configure_defaults(self) -> None:
        """Configure default settings for screenshot capture."""
        defaults = {
            'web_browser': 'chrome',
            'run_in_background': False,
            'wait_time': 30,
            'window_size': '1920,1080'
        }
        
        for key, value in defaults.items():
            if not self.config.has(key):
                self.config.set(key, value)
                
    async def initialize(self) -> bool:
        """Initialize screenshot manager components."""
        try:
            self.browser_manager = ModernBrowserManager(self.config)
            
            if not self.auth_manager.is_authenticated():
                logger.error("Authentication required for screenshot capture")
                return False
                
            logger.info("Screenshot manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize screenshot manager: {e}")
            return False
            
    async def capture_chart_screenshot(self, config: ScreenshotConfiguration) -> ScreenshotResult:
        """
        Capture a single chart screenshot with full configuration.
        
        Args:
            config: Screenshot configuration
            
        Returns:
            Screenshot result with file path and metadata
        """
        if not await self.initialize():
            return ScreenshotResult(success=False, error_message="Initialization failed")
            
        start_time = datetime.now()
        
        try:
            browser = self.browser_manager.create_browser()
            
            try:
                # Navigate to TradingView chart
                await self._navigate_to_chart(browser, config)
                
                # Login if needed
                await self._ensure_logged_in(browser)
                
                # Configure chart appearance
                await self._configure_chart_style(browser, config)
                
                # Wait for chart to fully load
                await self._wait_for_chart_load(browser)
                
                # Capture screenshot
                screenshot_path = await self._capture_screenshot(browser, config)
                
                if not screenshot_path:
                    return ScreenshotResult(success=False, error_message="Screenshot capture failed")
                    
                # Generate thumbnail
                thumbnail_path = await self._generate_thumbnail(screenshot_path, config)
                
                # Add annotations if enabled
                if config.annotation_enabled:
                    await self._add_annotations(screenshot_path, config)
                    
                # Extract metadata
                metadata = await self._extract_chart_metadata(browser, config)
                
                # Get file size
                file_size = Path(screenshot_path).stat().st_size if Path(screenshot_path).exists() else 0
                
                return ScreenshotResult(
                    success=True,
                    file_path=screenshot_path,
                    thumbnail_path=thumbnail_path,
                    metadata=metadata,
                    capture_time=start_time,
                    file_size=file_size
                )
                
            finally:
                self.browser_manager.destroy_browser(browser)
                
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return ScreenshotResult(
                success=False,
                error_message=str(e),
                capture_time=start_time
            )
            
    async def _navigate_to_chart(self, browser, config: ScreenshotConfiguration) -> None:
        """Navigate to TradingView chart with specified configuration."""
        # Build URL with parameters
        url_params = {
            'symbol': config.ticker,
            'interval': config.timeframe,
            'style': '1' if config.chart_style == 'candles' else '0',
            'theme': config.theme
        }
        
        # Construct URL
        base_url = "https://www.tradingview.com/chart/"
        url = f"{base_url}?symbol={url_params['symbol']}&interval={url_params['interval']}"
        
        browser.get(url)
        await asyncio.sleep(self.config.get('wait_time', 30))
        
    async def _ensure_logged_in(self, browser) -> None:
        """Ensure user is logged into TradingView."""
        try:
            # Check for login button
            login_selectors = [
                "[data-name='header-user-menu-sign-in']",
                ".tv-header__user-menu-sign-in"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = browser.find_element("css selector", selector)
                    if login_btn.is_displayed():
                        await self._perform_google_login(browser)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Login check failed: {e}")
            
    async def _perform_google_login(self, browser) -> None:
        """Perform Google OAuth login."""
        try:
            login_btn = browser.find_element("css selector", "[data-name='header-user-menu-sign-in']")
            login_btn.click()
            await asyncio.sleep(2)
            
            google_btn = browser.find_element("css selector", "[data-name='google']")
            google_btn.click()
            await asyncio.sleep(10)  # Wait for OAuth flow
            
        except Exception as e:
            logger.error(f"Google login failed: {e}")
            
    async def _configure_chart_style(self, browser, config: ScreenshotConfiguration) -> None:
        """Configure chart style and appearance."""
        try:
            # Set chart style
            if config.chart_style != "candles":
                style_btn = browser.find_element("css selector", "[data-name='chart-style-selector']")
                style_btn.click()
                await asyncio.sleep(1)
                
                style_option = browser.find_element("css selector", f"[data-name='{config.chart_style}']")
                style_option.click()
                await asyncio.sleep(1)
                
            # Set theme
            if config.theme == "light":
                theme_btn = browser.find_element("css selector", "[data-name='theme-toggle']")
                theme_btn.click()
                await asyncio.sleep(1)
                
            # Configure indicators visibility
            if not config.indicators_visible:
                indicators_btn = browser.find_element("css selector", "[data-name='hide-indicators']")
                indicators_btn.click()
                await asyncio.sleep(1)
                
            # Configure volume visibility
            if not config.volume_visible:
                volume_btn = browser.find_element("css selector", "[data-name='hide-volume']")
                volume_btn.click()
                await asyncio.sleep(1)
                
            # Configure drawings visibility
            if not config.drawings_visible:
                drawings_btn = browser.find_element("css selector", "[data-name='hide-drawings']")
                drawings_btn.click()
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.warning(f"Chart style configuration failed: {e}")
            
    async def _wait_for_chart_load(self, browser) -> None:
        """Wait for chart to fully load."""
        try:
            # Wait for chart canvas to be present
            timeout = 60
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    chart_canvas = browser.find_element("css selector", "canvas[data-name='main-series-canvas']")
                    if chart_canvas.is_displayed():
                        # Additional wait for data to load
                        await asyncio.sleep(5)
                        break
                except:
                    pass
                    
                await asyncio.sleep(2)
                
            # Wait for any loading indicators to disappear
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.warning(f"Chart load wait failed: {e}")
            
    async def _capture_screenshot(self, browser, config: ScreenshotConfiguration) -> Optional[str]:
        """Capture the actual screenshot."""
        try:
            # Create output directory for strategy
            strategy_dir = self.output_dir / config.strategy_name
            strategy_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{config.ticker}_{config.timeframe}_{timestamp}.{config.output_format}"
            screenshot_path = strategy_dir / filename
            
            # Capture screenshot
            if config.capture_full_page:
                # Full page screenshot
                original_size = browser.get_window_size()
                browser.set_window_size(1920, 3000)  # Tall window for full page
                await asyncio.sleep(2)
                
                browser.save_screenshot(str(screenshot_path))
                
                # Restore original size
                browser.set_window_size(original_size['width'], original_size['height'])
            else:
                # Standard screenshot
                browser.save_screenshot(str(screenshot_path))
                
            # Resize if requested
            if config.resize_width or config.resize_height:
                await self._resize_image(screenshot_path, config.resize_width, config.resize_height)
                
            logger.info(f"Screenshot captured: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
            
    async def _generate_thumbnail(self, screenshot_path: str, config: ScreenshotConfiguration) -> Optional[str]:
        """Generate thumbnail from screenshot."""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, skipping thumbnail generation")
            return None
            
        try:
            # Create thumbnail path
            screenshot_file = Path(screenshot_path)
            thumbnail_path = screenshot_file.parent / f"thumb_{screenshot_file.name}"
            
            # Open and resize image
            with Image.open(screenshot_path) as img:
                # Calculate thumbnail size maintaining aspect ratio
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                img.save(str(thumbnail_path), quality=config.quality)
                
            logger.info(f"Thumbnail generated: {thumbnail_path}")
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None
            
    async def _add_annotations(self, screenshot_path: str, config: ScreenshotConfiguration) -> None:
        """Add annotations to screenshot."""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, skipping annotations")
            return
            
        try:
            with Image.open(screenshot_path) as img:
                draw = ImageDraw.Draw(img)
                
                # Try to load a font
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                    
                # Add strategy name annotation
                strategy_text = f"Strategy: {config.strategy_name}"
                draw.text((20, 20), strategy_text, fill="white", font=font)
                
                # Add ticker and timeframe
                chart_info = f"{config.ticker} - {config.timeframe}"
                draw.text((20, 60), chart_info, fill="white", font=font)
                
                # Add timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                draw.text((20, 100), f"Captured: {timestamp}", fill="white", font=font)
                
                # Add custom annotation if provided
                if config.annotation_text:
                    # Position at bottom of image
                    img_width, img_height = img.size
                    draw.text((20, img_height - 80), config.annotation_text, fill="white", font=font)
                    
                # Save annotated image
                img.save(screenshot_path, quality=config.quality)
                
            logger.info("Annotations added to screenshot")
            
        except Exception as e:
            logger.error(f"Annotation failed: {e}")
            
    async def _resize_image(self, image_path: str, width: Optional[int], height: Optional[int]) -> None:
        """Resize image to specified dimensions."""
        if not PIL_AVAILABLE:
            return
            
        try:
            with Image.open(image_path) as img:
                if width and height:
                    # Resize to exact dimensions
                    resized = img.resize((width, height), Image.Resampling.LANCZOS)
                elif width:
                    # Resize maintaining aspect ratio based on width
                    ratio = width / img.width
                    new_height = int(img.height * ratio)
                    resized = img.resize((width, new_height), Image.Resampling.LANCZOS)
                elif height:
                    # Resize maintaining aspect ratio based on height
                    ratio = height / img.height
                    new_width = int(img.width * ratio)
                    resized = img.resize((new_width, height), Image.Resampling.LANCZOS)
                else:
                    return
                    
                resized.save(image_path)
                
        except Exception as e:
            logger.error(f"Image resize failed: {e}")
            
    async def _extract_chart_metadata(self, browser, config: ScreenshotConfiguration) -> Dict[str, Any]:
        """Extract metadata from chart."""
        try:
            metadata = {
                'strategy_name': config.strategy_name,
                'ticker': config.ticker,
                'timeframe': config.timeframe,
                'chart_style': config.chart_style,
                'theme': config.theme,
                'capture_timestamp': datetime.now().isoformat(),
                'url': browser.current_url
            }
            
            # Try to extract additional chart information
            try:
                # Current price
                price_elem = browser.find_element("css selector", "[data-name='legend-source-item'] .js-symbol-last")
                if price_elem:
                    metadata['current_price'] = price_elem.text.strip()
                    
                # Price change
                change_elem = browser.find_element("css selector", "[data-name='legend-source-item'] .js-symbol-change")
                if change_elem:
                    metadata['price_change'] = change_elem.text.strip()
                    
                # Volume
                volume_elem = browser.find_element("css selector", "[data-name='legend-source-item'] .js-symbol-volume")
                if volume_elem:
                    metadata['volume'] = volume_elem.text.strip()
                    
            except:
                pass  # Metadata extraction is optional
                
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {'error': str(e)}
            
    async def capture_strategy_screenshots(self, 
                                         strategy_name: str,
                                         tickers: Optional[List[str]] = None,
                                         timeframes: Optional[List[str]] = None) -> List[ScreenshotResult]:
        """
        Capture screenshots for multiple ticker/timeframe combinations.
        
        Args:
            strategy_name: Name of the strategy
            tickers: List of tickers (default: ["MNQ1!"])
            timeframes: List of timeframes (default: ["5m", "1h", "4h", "1d"])
            
        Returns:
            List of screenshot results
        """
        tickers = tickers or ["MNQ1!"]
        timeframes = timeframes or ["5m", "1h", "4h", "1d"]
        
        results = []
        
        for ticker in tickers:
            for timeframe in timeframes:
                config = ScreenshotConfiguration(
                    strategy_name=strategy_name,
                    ticker=ticker,
                    timeframe=timeframe,
                    annotation_enabled=True,
                    annotation_text=f"Setup: {strategy_name}"
                )
                
                result = await self.capture_chart_screenshot(config)
                results.append(result)
                
                # Small delay between captures
                await asyncio.sleep(2)
                
        return results
        
    async def create_comparison_image(self, screenshot_paths: List[str], output_path: str) -> bool:
        """Create a comparison image from multiple screenshots."""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, cannot create comparison image")
            return False
            
        try:
            images = []
            for path in screenshot_paths:
                if Path(path).exists():
                    images.append(Image.open(path))
                    
            if not images:
                return False
                
            # Calculate grid layout
            num_images = len(images)
            cols = 2 if num_images > 1 else 1
            rows = (num_images + cols - 1) // cols
            
            # Resize all images to same size
            target_size = (800, 600)
            resized_images = [img.resize(target_size, Image.Resampling.LANCZOS) for img in images]
            
            # Create combined image
            total_width = target_size[0] * cols
            total_height = target_size[1] * rows
            combined = Image.new('RGB', (total_width, total_height), 'white')
            
            # Paste images
            for i, img in enumerate(resized_images):
                x = (i % cols) * target_size[0]
                y = (i // cols) * target_size[1]
                combined.paste(img, (x, y))
                
            # Save combined image
            combined.save(output_path, quality=95)
            
            # Close images
            for img in images:
                img.close()
                
            logger.info(f"Comparison image created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Comparison image creation failed: {e}")
            return False


# Factory function
def create_screenshot_manager(auth_manager: GrimmAuthManager,
                            config: Optional[Dict[str, Any]] = None) -> ChartScreenshotManager:
    """Create and configure a screenshot manager instance."""
    return ChartScreenshotManager(auth_manager, config)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        # Create auth manager and authenticate
        auth = GrimmAuthManager()
        if not auth.authenticate():
            print("Authentication failed")
            return
            
        # Create screenshot manager
        screenshot_manager = ChartScreenshotManager(auth)
        
        # Capture strategy screenshots
        results = await screenshot_manager.capture_strategy_screenshots(
            strategy_name="Example Strategy",
            tickers=["MNQ1!"],
            timeframes=["1h", "4h"]
        )
        
        successful = [r for r in results if r.success]
        print(f"Captured {len(successful)}/{len(results)} screenshots successfully")
        
        # Create comparison if multiple screenshots
        if len(successful) > 1:
            screenshot_paths = [r.file_path for r in successful]
            comparison_path = "./screenshots/comparison.png"
            await screenshot_manager.create_comparison_image(screenshot_paths, comparison_path)
            print(f"Comparison image created: {comparison_path}")
        
    asyncio.run(main())