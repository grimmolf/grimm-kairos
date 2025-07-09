"""
CSS Selectors for TradingView automation
Extracted from tv.py for better maintainability and updates
"""

from typing import Dict, Optional


class CSSSelectors:
    """
    Centralized CSS selectors for TradingView elements
    Makes it easier to update selectors when TradingView UI changes
    """
    
    # Core selectors from original tv.py
    SELECTORS = {
        # General
        'btn_confirm': 'div[data-name=confirm-dialog] button[name=yes]',
        
        # Cookies
        'btn_accept_all_cookies': 'button[class^="acceptAll"]',
        'btn_manage_cookies': 'button[class^="managePreferences"]',
        'input_accept_performance_analytics_cookies': 'label[for="id_Performance/Analytics-cookies"]',
        'input_accept_advertising_cookies': 'label[for="id_Advertising-cookies"]',
        'btn_save_preferences': 'button[class^="savePreferences"]',
        
        # Account
        'account': 'button.tv-header__user-menu-button--logged',
        'username': 'a[data-name="header-user-menu-profile"] span[class^="username"]',
        'account_level': 'a[data-name="header-user-menu-profile"] span[class^="badge"] span',
        'anonymous_account': 'button.tv-header__user-menu-button--anonymous',
        'anonymous_signin': 'button[data-name="header-user-menu-sign-in"]',
        'show_email_and_username': 'span.js-show-email',
        'input_username': 'input[id="id_username"]',
        'input_password': 'input[id="id_password"]',
        'input_2fa': 'input[id="id_code"]',
        'btn_login_by_email': 'button[name="Email"]',
        'captcha': 'div[class^="recaptchaContainer"]',
        'input_captcha': 'div.recaptcha-checkbox-checkmark',
        
        # Study error/loading
        'study_error': 'div[class*="dataProblemLow"]',
        'study_loading': 'span[class^="loaderItem"]',
        
        # Timeframe
        'btn_timeframe': '#header-toolbar-intervals > button > div',
        'options_timeframe': 'div[data-role="menuitem"] > span > span',
        
        # Watchlist / ticker
        'btn_watchlist_menu': 'button[data-name="base"]',
        'btn_watchlist_menu_menu': 'button[data-name="watchlists-button"]',
        'open_watchlist_submenu': 'div[data-name="active-watchlist-menu"]',
        'options_watchlist': 'div[data-name="watchlists-dialog"] div[id^="list-item"] div[class^="title"]',
        'input_watchlist_add_symbol': 'div[data-name="add-symbol-button"] > span',
        'btn_input_symbol': 'button[id="header-toolbar-symbol-search"]',
        'dlg_symbol_search_input': 'div[data-name="symbol-search-items-dialog"] input[data-role="search"]',
        'input_symbol': 'div[id="header-toolbar-symbol-search"] div',
        'asset': 'div[data-name="legend-series-item"] div[data-name="legend-source-title"]:nth-child(1)',
        'dlg_close_watchlist': 'div[data-name="watchlists-dialog"] button[class*="close"]',
        
        # Alerts - Core functionality
        'btn_alert_menu': 'div[data-name="alerts-settings-button"]',
        'item_clear_alerts': '#overlap-manager-root div[data-name=menu-inner] div:nth-child(4)',
        'item_clear_inactive_alerts': '#overlap-manager-root div[data-name=menu-inner] div:nth-child(3)',
        'item_restart_inactive_alerts': '#overlap-manager-root div[data-name=menu-inner] div:nth-child(1)',
        'btn_dlg_clear_alerts_confirm': 'div[data-name=confirm-dialog] button[name=yes]',
        'item_alerts': 'table.alert-list > tbody > tr.alert-item',
        'alerts_counter': 'div.widgetbar-widget-alerts_manage div[class*="label-"]',
        'btn_search_alert': 'div.widgetbar-page.active:has(div[data-name="alert-sort-button"]) div.widgetbar-widgetbody div[class^="right"] > div:nth-child(1)',
        'input_search_alert': 'input[data-role="search"]',
        'btn_delete_alert': 'div.widgetbar-widgetbody div[class^=body] div[class^=itemBody] div[class^=overlay] div[role=button]:nth-child(3)',
        'btn_create_alert': '#header-toolbar-alerts',
        'dlg_alert': 'div[data-name="alerts-create-edit-dialog"]',
        'btn_create_alert_from_alert_menu': 'div[data-name="set-alert-button"]',
        'btn_alert_cancel': 'div.tv-dialog__close.js-dialog__close',
        
        # Alert Creation Dialog
        'dlg_create_alert_first_row_first_item': 'div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(1) div[class^="select"] span[role="button"]',
        'dlg_create_alert_options': 'div[data-name="popup-menu-container"] div[role="option"] div > span',
        'exists_dlg_create_alert_first_row_second_item': 'div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(1) > div:nth-child(2)',
        'dlg_create_alert_first_row_second_item': 'div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(1) > div:nth-child(2) span[role="button"]',
        'dlg_create_alert_second_row': 'div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(2) div[class^="select"] span[role="button"]',
        'inputs_and_selects_create_alert_3rd_row_and_above': 'div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(3) input, div[data-name="alerts-create-edit-dialog"] div[class^="content"] > div:nth-child(1) div[class^="fieldsColumn"] > div:nth-child(3) div[class^="select"] > span[role="button"]',
        
        # Alert Expiration
        'dlg_create_alert_expiration_value': 'button[aria-controls="alert-editor-expiration-popup"] span[class^="content"]',
        'dlg_create_alert_expiration_button': 'button[aria-controls="alert-editor-expiration-popup"]',
        'dlg_create_alert_open_ended_checkbox': '#unexpired-date',
        'dlg_create_alert_expiration_confirmation_button': 'div[data-name^="popup-menu-container"] > div >div > div > button',
        'dlg_create_alert_expiration_date': 'div[data-name^="popup-menu-container"] div[class^="picker"] input',
        'dlg_create_alert_expiration_time': 'div[data-name^="popup-menu-container"] div[class^="time"] input',
        'dlg_create_alert_notifications_button': 'button[id="alert-dialog-tabs__notifications"]',
        
        # Alert Notifications
        'dlg_create_alert_notifications_notify_on_app_checkbox': 'input[data-name="notify-on-app"]',
        'dlg_create_alert_notifications_show_popup_checkbox': 'input[data-name="show-popup"]',
        'dlg_create_alert_notifications_send_email_checkbox': 'input[data-name="send-email"]',
        'dlg_create_alert_notifications_webhook_checkbox': 'input[data-name="webhook"]',
        'dlg_create_alert_notifications_play_sound_checkbox': 'input[data-name="play-sound"]',
        'dlg_create_alert_notifications_email_to_sms_checkbox': 'input[data-name="send-email-to-sms"]',
        'dlg_create_alert_notifications_webhook_text': 'input[id="webhook-url"]',
        'dlg_create_alert_notifications_sound_ringtone_button': 'div[class*="selectGroup"] span[role="button"]:nth-child(1)',
        'dlg_create_alert_notifications_sound_ringtone_options': 'div[data-name="popup-menu-container"] div[role="option"] div[class^="title"]',
        'dlg_create_alert_notifications_sound_duration_button': 'div[class*="selectGroup"] span[role="button"]:nth-child(2)',
        'dlg_create_alert_notifications_sound_duration_options': 'div[data-name="popup-menu-container"] div[role="option"] > span >span',
        
        # Alert Name and Message
        'dlg_create_alert_name': '#alert-name',
        'dlg_create_alert_message': '#alert-message',
        
        # Alert Submit
        'btn_dlg_create_alert_submit': 'div[data-name="alerts-create-edit-dialog"] button[data-name="submit"]',
        
        # Alert Warnings
        'btn_create_alert_warning_continue_anyway_got_it': 'div[data-name="alerts-trigger-warning-dialog-pine-repainting"] label[class^="checkbox"]',
        'btn_create_alert_warning_continue_anyway': 'div[data-name="alerts-trigger-warning-dialog-pine-repainting"] button[name="continue"]',
        'btn_alerts': 'button[data-name="alerts"]',
        
        # Data Window and Object Tree
        'btn_object_tree_and_data_window': 'button[data-name="object_tree"]',
        'btn_data_window': 'button[id="data-window"]',
        'btn_data_window_active': 'button[id="data-window"][tabindex="0"]',
        'btn_watchlist': 'button[data-name="base"]',
        'div_existing_watchlist_items': 'div[data-name="watchlists-dialog"] div[data-role="list-item"]',
        'div_watchlist_item': 'div[data-symbol-full]',
        'div_watchlist_item_by_symbol': 'div[data-symbol-full="{}"]',
        
        # User Menu
        'signout': 'div[data-name="header-user-menu-sign-out"]',
        'btn_screenshot': '#header-toolbar-screenshot',
        'btn_twitter_url': 'div[data-name="tweet-chart-image"]',
        'btn_image_url': 'div[data-name="open-image-in-new-tab"]',
        'img_chart': 'img[class="tv-snapshot-image"]',
        'btn_watchlist_sort_symbol': 'div.widgetbar-widget-watchlist span[data-column-type="short_name"]',
        'btn_close_watchlists_dialog': 'button[data-name="close"]',
        
        # Screeners
        'select_screener': 'div[data-name="screener-filter-sets"] span',
        'options_screeners': 'div.tv-screener-popup div.tv-dropdown-behavior__item div.tv-screener-popup__item',
        'input_screener_search': 'div.tv-screener-table__search-query.js-search-query.tv-screener-table__search-query--without-description > input',
        'screener_table_ticker_name_column': 'div.tv-screener-sticky-header-wrapper th[data-field="name"] div.js-head-title',
        'screener_table_sort_element': 'div[data-field="name"] span.tv-screener-table__sort--asc',
        'screener_total_matches': 'div.tv-screener-table__field-value--total',
        
        # Stock Screeners
        'select_stock_screener': 'div[data-name="screener-topbar-screen-title"] > div > h1',
        'options_stock_screeners': 'div[data-name="popup-menu-container"] > div > div > div[class^="item"] > span[class^="labelRow"] > span[class^="label"] > div[class^="label"] > div[class^="title"] > div[class^="title"]',
        'btn_stock_screener_search': 'button[class^="searchButton"]',
        'btn_stock_screener_close_search': 'span[title="Clear and close"]',
        'input_stock_screener_search': 'input[placeholder="Search"]',
        'btn_stock_sorting_options': 'button[class^="searchButton"] + div > div',
        'options_stock_sorting': 'div[data-name="popup-menu-container"] > div > div > div[class^="item"]',
        'stock_screener_table_row': 'tr.listRow',
        'stock_screener_table_sort_element': 'button[aria-label="Change sort"]',
        'stock_screener_total_matches': 'button[aria-label="Change sort"] + span',
        
        # Strategy Tester
        'tab_strategy_tester': '#footer-chart-panel div[data-name=backtesting]',
        'tab_strategy_tester_inactive': 'btn[data-name="backtesting"][data-active="false"]',
        'tab_strategy_tester_performance_summary': 'button[id="Performance Summary"][aria-selected="false"]',
        'btn_strategy_dialog': '.deep-history > div > div > div > div > button',
        'strategy_id': '#bottom-area > div.bottom-widgetbar-content.backtesting div[data-strategy-title]',
        
        # Performance Overview
        'performance_overview_net_profit': 'div[class^="container-"] > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_net_profit_percentage': 'div[class^="container-"] > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)',
        'performance_overview_total_closed_trades': 'div[class^="container-"] > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_percent_profitable': 'div[class^="container-"] > div:nth-child(3) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_profit_factor': 'div[class^="container-"] > div:nth-child(4) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_max_drawdown': 'div[class^="container-"] > div:nth-child(5) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_max_drawdown_percentage': 'div[class^="container-"] > div:nth-child(5) > div:nth-child(2) > div:nth-child(2)',
        'performance_overview_avg_trade': 'div[class^="container-"] > div:nth-child(6) > div:nth-child(2) > div:nth-child(1)',
        'performance_overview_avg_trade_percentage': 'div[class^="container-"] > div:nth-child(6) > div:nth-child(2) > div:nth-child(2)',
        'performance_overview_avg_bars_in_trade': 'div[class^="container-"] > div:nth-child(7) > div:nth-child(2) > div:nth-child(1)',
        
        # Performance Summary
        'performance_summary_net_profit': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div:nth-child(1)',
        'performance_summary_net_profit_percentage': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div:nth-child(2)',
        'performance_summary_total_closed_trades': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(13) > td:nth-child(2) > div > div',
        'performance_summary_percent_profitable': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(17) > td:nth-child(2) > div > div',
        'performance_summary_profit_factor': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(9) > td:nth-child(2) > div > div',
        'performance_summary_max_drawdown': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(5) > td:nth-child(2) > div > div:nth-child(1)',
        'performance_summary_max_drawdown_percentage': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(5) > td:nth-child(2) > div > div:nth-child(2)',
        'performance_summary_avg_trade': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(18) > td:nth-child(2) > div > div:nth-child(1)',
        'performance_summary_avg_trade_percentage': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(18) > td:nth-child(2) > div > div:nth-child(2)',
        'performance_summary_avg_bars_in_trade': 'div[class^="report"] > div > div > table > tbody > tr:nth-child(24) > td:nth-child(2) > div > div',
        
        # Indicator Dialog
        'indicator_dialog_tab_inputs': 'div[data-name="indicator-properties-dialog"] #inputs',
        'indicator_dialog_tab_properties': 'div[data-name="indicator-properties-dialog"] #properties',
        'indicator_dialog_tab_cells': 'div[data-name="indicator-properties-dialog"] div[class^="cell-"]',
        'indicator_dialog_tab_cell': 'div[data-name="indicator-properties-dialog"] div[class^="cell-"]:nth-child({})',
        'indicator_dialog_titles': 'div[data-name="indicator-properties-dialog"] div[class*="first"] > div',
        'indicator_dialog_select_options': 'div[role="listbox"] div[role="option"] span span',
        'btn_indicator_dialog_ok': 'div[data-name="indicator-properties-dialog"] button[name="submit"]',
        
        # Chart Elements
        'active_chart_asset': 'div.chart-container.active div.pane-legend-line.main div.pane-legend-title__description > div',
        'active_chart_interval': 'div[id="header-toolbar-intervals"] button[class*="isActive"] > div > div',
        'chart_container': 'div.chart-widget > div.chart-markup-table',
        'btn_user_menu': 'button.tv-header__user-menu-button--logged',
        'btn_logout': 'button[data-name="header-user-menu-sign-out"]',
        'active_widget_bar': 'div.widgetbar-page.active',
        'price_axis': 'div[class="price-axis"] div[data-name="currency-unit-label-wrapper"] div[class^="price-axis-currency-label-text"]',
        'chart_error_message': 'div.active > div.chart-container-border div[class^=errorCard__message]',
    }
    
    # Class-based selectors
    CLASS_SELECTORS = {
        'form_create_alert': 'js-alert-form',
        'rows_screener_result': 'tv-screener-table__result-row',
    }
    
    # XPath selectors (use sparingly)
    XPATH_SELECTORS = {
        'data_window_indicator': '//div[@class="widgetbar-widget widgetbar-widget-object_tree"]/div/div/div[2]/div/div/div/span[starts-with(text(), "{}")]',
    }
    
    @classmethod
    def get(cls, selector_name: str, **kwargs) -> Optional[str]:
        """
        Get a CSS selector by name with optional formatting
        
        Args:
            selector_name: Name of the selector
            **kwargs: Format arguments for dynamic selectors
            
        Returns:
            Formatted CSS selector or None if not found
        """
        selector = cls.SELECTORS.get(selector_name)
        if selector and kwargs:
            try:
                return selector.format(**kwargs)
            except (KeyError, ValueError):
                return selector
        return selector
    
    @classmethod
    def get_class(cls, class_name: str) -> Optional[str]:
        """Get a class selector by name"""
        return cls.CLASS_SELECTORS.get(class_name)
    
    @classmethod
    def get_xpath(cls, xpath_name: str, **kwargs) -> Optional[str]:
        """Get an XPath selector by name with optional formatting"""
        xpath = cls.XPATH_SELECTORS.get(xpath_name)
        if xpath and kwargs:
            try:
                return xpath.format(**kwargs)
            except (KeyError, ValueError):
                return xpath
        return xpath
    
    @classmethod
    def get_all_alert_selectors(cls) -> Dict[str, str]:
        """Get all alert-related selectors"""
        return {
            key: value for key, value in cls.SELECTORS.items() 
            if 'alert' in key.lower()
        }
    
    @classmethod
    def get_all_strategy_selectors(cls) -> Dict[str, str]:
        """Get all strategy tester related selectors"""
        return {
            key: value for key, value in cls.SELECTORS.items() 
            if 'strategy' in key.lower() or 'performance' in key.lower()
        }
    
    @classmethod
    def update_selector(cls, name: str, new_value: str) -> None:
        """Update a selector (useful for handling TradingView UI changes)"""
        cls.SELECTORS[name] = new_value
    
    @classmethod
    def add_selector(cls, name: str, value: str) -> None:
        """Add a new selector"""
        cls.SELECTORS[name] = value