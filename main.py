import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.clock import Clock
from android.storage import app_storage_path  # type: ignore
from android.runnable import run_on_ui_thread  # type: ignore
from jnius import autoclass  # type: ignore

# Android classes
CookieManager = autoclass('android.webkit.CookieManager')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
WebSettings = autoclass('android.webkit.WebSettings')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
LinearLayout = autoclass('android.widget.LinearLayout')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

# Colors
SPOTIFY_GREEN = get_color_from_hex('#1DB954')
SPOTIFY_BLACK = get_color_from_hex('#121212')
SPOTIFY_DARK = get_color_from_hex('#181818')
SPOTIFY_GRAY = get_color_from_hex('#282828')
SPOTIFY_LIGHT = get_color_from_hex('#B3B3B3')
WHITE = get_color_from_hex('#FFFFFF')

COOKIES_FILE = os.path.join(app_storage_path(), 'spotify_cookies.json')
SPOTIFY_URL = 'https://open.spotify.com'


def load_cookies():
    try:
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def save_cookies(cookie_text):
    try:
        with open(COOKIES_FILE, 'w') as f:
            json.dump({'raw': cookie_text}, f)
        return True
    except Exception:
        return False


def parse_netscape_cookies(raw):
    cookies = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#') and 'HttpOnly' not in line:
            continue
        if line.startswith('#HttpOnly_'):
            line = line.replace('#HttpOnly_', '', 1)
        parts = line.split('\t')
        if len(parts) >= 7:
            domain, _, path, secure, _, name, value = parts[:7]
            cookies.append({
                'domain': domain,
                'path': path,
                'secure': secure.upper() == 'TRUE',
                'name': name,
                'value': value
            })
    return cookies


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = WHITE
        self.bold = True
        self.font_size = dp(15)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*SPOTIFY_GREEN)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(25)])


class CookieScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        with root.canvas.before:
            Color(*SPOTIFY_BLACK)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)

        container = BoxLayout(
            orientation='vertical',
            padding=[dp(28), dp(60), dp(28), dp(40)],
            spacing=dp(20),
            size_hint=(1, 1)
        )

        # Logo area
        logo_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(6))
        logo_label = Label(
            text='[b]SPOTIFI[/b]',
            markup=True,
            font_size=dp(32),
            color=SPOTIFY_GREEN,
            halign='center',
            size_hint_y=None,
            height=dp(44)
        )
        sub_label = Label(
            text='Paste your Netscape cookies below',
            font_size=dp(13),
            color=SPOTIFY_LIGHT,
            halign='center',
            size_hint_y=None,
            height=dp(22)
        )
        logo_box.add_widget(logo_label)
        logo_box.add_widget(sub_label)
        container.add_widget(logo_box)

        # Cookie input
        input_wrapper = BoxLayout(orientation='vertical', size_hint_y=1, spacing=dp(8))
        input_label = Label(
            text='Cookie Data',
            font_size=dp(12),
            color=SPOTIFY_GREEN,
            halign='left',
            size_hint_y=None,
            height=dp(18),
            text_size=(Window.width - dp(56), None)
        )
        self.cookie_input = TextInput(
            hint_text='# Netscape HTTP Cookie File\n.spotify.com\tTRUE\t/ ...',
            hint_text_color=get_color_from_hex('#555555'),
            background_color=get_color_from_hex('#1E1E1E'),
            foreground_color=WHITE,
            cursor_color=SPOTIFY_GREEN,
            font_size=dp(11),
            padding=[dp(14), dp(12)],
            multiline=True,
            size_hint_y=1
        )
        input_wrapper.add_widget(input_label)
        input_wrapper.add_widget(self.cookie_input)
        container.add_widget(input_wrapper)

        # Status label
        self.status_label = Label(
            text='',
            font_size=dp(12),
            color=SPOTIFY_GREEN,
            halign='center',
            size_hint_y=None,
            height=dp(20)
        )
        container.add_widget(self.status_label)

        # Load button
        btn = RoundedButton(
            text='LOAD SPOTIFY',
            size_hint_y=None,
            height=dp(52)
        )
        btn.bind(on_press=self.on_load)
        container.add_widget(btn)

        root.add_widget(container)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.parent.pos if self.parent else (0, 0)
        self.bg_rect.size = self.parent.size if self.parent else Window.size

    def on_load(self, *args):
        raw = self.cookie_input.text.strip()
        if not raw:
            self.status_label.text = 'Paste your cookies first.'
            self.status_label.color = get_color_from_hex('#FF4444')
            return
        cookies = parse_netscape_cookies(raw)
        if not cookies:
            self.status_label.text = 'Could not parse cookies. Check format.'
            self.status_label.color = get_color_from_hex('#FF4444')
            return
        save_cookies(raw)
        self.status_label.text = f'Loaded {len(cookies)} cookies. Opening...'
        self.status_label.color = SPOTIFY_GREEN
        Clock.schedule_once(lambda dt: self.launch_player(raw), 0.6)

    def launch_player(self, raw):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'player'
        app.root.get_screen('player').load_with_cookies(raw)


class PlayerScreen(Screen):
    webview = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            Color(*SPOTIFY_BLACK)
            Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.add_widget(self.layout)

    @run_on_ui_thread
    def load_with_cookies(self, raw_cookies):
        activity = PythonActivity.mActivity
        self.webview = WebView(activity)

        settings = self.webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setLoadWithOverviewMode(True)
        settings.setUseWideViewPort(True)
        settings.setMediaPlaybackRequiresUserGesture(False)
        settings.setCacheMode(WebSettings.LOAD_DEFAULT)
        settings.setUserAgentString(
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Mobile Safari/537.36'
        )

        cm = CookieManager.getInstance()
        cm.setAcceptCookie(True)
        cm.setAcceptThirdPartyCookies(self.webview, True)

        # Inject cookies
        cookies = parse_netscape_cookies(raw_cookies)
        for c in cookies:
            domain = c['domain']
            if not domain.startswith('.'):
                domain = '.' + domain
            cookie_str = f"{c['name']}={c['value']}; Domain={domain}; Path={c['path']}"
            cm.setCookie(f"https://open.spotify.com", cookie_str)
        cm.flush()

        self.webview.setWebViewClient(WebViewClient())

        params = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
        activity.addContentView(self.webview, params)

        self.webview.loadUrl(SPOTIFY_URL)


class SpotifiApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#121212')
        sm = ScreenManager()

        cookie_screen = CookieScreen(name='cookie')
        player_screen = PlayerScreen(name='player')

        sm.add_widget(cookie_screen)
        sm.add_widget(player_screen)

        # Check saved cookies
        saved = load_cookies()
        if saved and saved.get('raw'):
            cookie_screen.cookie_input.text = saved['raw']
            sm.current = 'cookie'

        return sm


if __name__ == '__main__':
    SpotifiApp().run()
