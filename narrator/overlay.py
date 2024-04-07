import Cocoa
import Quartz
import objc
import multiprocessing
import threading
import atexit

class SubtitleOverlay:
    """
    A class that creates a transparent overlay window to display subtitles.
    """

    class _OverlayProcess:
        """
        An internal class that runs the overlay window in a separate process.
        """

        def __init__(self):
            self._parent_conn, self._child_conn = multiprocessing.Pipe()
            self._overlay_process = multiprocessing.Process(target=self._run_overlay, args=(self._child_conn,))
            self._overlay_process.start()
            atexit.register(self.dispose)

        def _run_overlay(self, pipe):
            """
            The main function that runs the overlay window in a separate process.
            """
            app = Cocoa.NSApplication.sharedApplication()
            app.preventWindowOrdering()
            app.setActivationPolicy_(Cocoa.NSApplicationActivationPolicyAccessory)

            screen_rect = Cocoa.NSScreen.mainScreen().frame()
            window = self._create_window(screen_rect)
            text_field = self._create_text_field(screen_rect)
            window.contentView().addSubview_(text_field)

            def listen_for_commands():
                while True:
                    if pipe.poll():
                        command = pipe.recv()
                        if command['action'] in ['set', 'clear']:
                            Cocoa.NSOperationQueue.mainQueue().addOperationWithBlock_(
                                lambda: self._update_text_field(text_field, window, screen_rect, command)
                            )
                        if command['action'] == 'quit':
                            app.terminate_(None)
                            break

            command_thread = threading.Thread(target=listen_for_commands)
            command_thread.start()

            app.setActivationPolicy_(Cocoa.NSApplicationActivationPolicyProhibited)
            app.run()
            command_thread.join()

        def _create_window(self, screen_rect):
            """
            Creates the transparent overlay window.
            """
            window_rect = Cocoa.NSMakeRect(0, 30, screen_rect.size.width, 100)
            window = TransparentWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                window_rect,
                Cocoa.NSWindowStyleMaskBorderless,  # Ensures no title bar is present
                Cocoa.NSBackingStoreBuffered,
                False
            )
            return window

        def _create_text_field(self, screen_rect):
            """
            Creates the text field for displaying subtitles.
            """
            text_view_frame = Cocoa.NSMakeRect(20, 5, screen_rect.size.width - 40, 90)
            text_view = Cocoa.NSTextView.alloc().initWithFrame_(text_view_frame)
            text_view.setVerticallyResizable_(True)
            text_view.setHorizontallyResizable_(False)
            text_view.setMaxSize_(Cocoa.NSMakeSize(screen_rect.size.width - 40, float('inf')))
            text_view.setMinSize_(Cocoa.NSMakeSize(screen_rect.size.width - 40, 30))
            text_view.setTextColor_(Cocoa.NSColor.whiteColor())
            text_view.setFont_(Cocoa.NSFont.boldSystemFontOfSize_(30))
            text_view.setDrawsBackground_(False)
            text_view.setEditable_(False)
            text_view.setSelectable_(False)
            text_view.setTextContainerInset_(Cocoa.NSSize(0, 0))

            text_container = text_view.textContainer()
            text_container.setWidthTracksTextView_(True)
            text_container.setContainerSize_(Cocoa.NSMakeSize(screen_rect.size.width - 40, float('inf')))

            text_view.setAlignment_(Cocoa.NSTextAlignmentCenter)
            return text_view

        def _update_text_field(self, text_view, window, screen_rect, command):
            """
            Updates the text field with the provided subtitle text and styling.
            """
            text = command.get('text', "")
            text_color_name = command.get('text_color', 'white')
            font_size = command.get('font_size', 30)
            font_name = command.get('font', 'Helvetica')
            shadow_color_name = command.get('shadow_color', 'black')
            shadow_offset = command.get('shadow_offset', (5.0, -5.0))
            shadow_blur_radius = command.get('shadow_blur_radius', 3)
            shadow_alpha = min(max(command.get('shadow_alpha', 1.0), 0.0), 1.0)  # Clamped between 0.0 and 1.0
            font_alpha = min(max(command.get('font_alpha', 1.0), 0.0), 1.0)  # Clamped between 0.0 and 1.0

            text_color = self._color_from_name(text_color_name, Cocoa.NSColor.whiteColor()).colorWithAlphaComponent_(font_alpha)
            font = self._safe_font_named(font_name, font_size)
            shadow_color = self._color_from_name(shadow_color_name, Cocoa.NSColor.blackColor()).colorWithAlphaComponent_(shadow_alpha)
            shadow_offset_size = Cocoa.NSMakeSize(*shadow_offset)

            text_shadow = Cocoa.NSShadow.alloc().init()
            text_shadow.setShadowColor_(shadow_color)
            text_shadow.setShadowOffset_(shadow_offset_size)
            text_shadow.setShadowBlurRadius_(shadow_blur_radius)

            attributes = {
                Cocoa.NSFontAttributeName: font,
                Cocoa.NSShadowAttributeName: text_shadow,
                Cocoa.NSForegroundColorAttributeName: text_color
            }

            attributed_string = Cocoa.NSAttributedString.alloc().initWithString_attributes_(text, attributes)
            text_storage = text_view.textStorage()
            range_all = Cocoa.NSMakeRange(0, text_storage.length())
            text_storage.replaceCharactersInRange_withAttributedString_(range_all, attributed_string)

            if text:
                layout_manager = text_view.layoutManager()
                text_container = text_view.textContainer()
                text_container.setContainerSize_(Cocoa.NSMakeSize(screen_rect.size.width - 40, float('inf')))
                layout_manager.glyphRangeForTextContainer_(text_container)
                text_bounds = layout_manager.usedRectForTextContainer_(text_container)
                new_height = min(text_bounds.size.height + 10, screen_rect.size.height / 3)
                window_frame = Cocoa.NSMakeRect(0, 30, screen_rect.size.width, new_height)
                window.setFrame_display_animate_(window_frame, True, False)
                text_view.setFrame_(Cocoa.NSMakeRect(20, 5, screen_rect.size.width - 40, new_height - 10))

        def _safe_font_named(self, font_name, font_size):
            """
            Returns a font with the specified name and size, or a default font if the specified font is not available.
            """
            font = Cocoa.NSFont.fontWithName_size_(font_name, font_size)
            if font is None:
                return Cocoa.NSFont.systemFontOfSize_(font_size)
            return font

        def _color_from_name(self, color_name, default_color):
            """
            Returns a color with the specified name, or a default color if the specified color is not available.
            """
            if hasattr(Cocoa.NSColor, f"{color_name}Color"):
                return getattr(Cocoa.NSColor, f"{color_name}Color")()
            return default_color

        def dispose(self):
            """
            Disposes of the overlay process and window.
            """
            if self._overlay_process.is_alive():
                self._parent_conn.send({'action': 'quit'})
                self._overlay_process.join(timeout=5)
                if self._overlay_process.is_alive():
                    self._overlay_process.terminate()

    def __init__(self):
        self._overlay_process = self._OverlayProcess()

    def setSubtitle(self, text, text_color='white', font_size=30, font='Helvetica', shadow_color='black', shadow_offset=(5.0, -5.0), shadow_blur_radius=3, shadow_alpha=1.0, font_alpha=1.0):
        """
        Sets the subtitle text and styling.
        """
        self._overlay_process._parent_conn.send({
            'action': 'set',
            'text': text,
            'text_color': text_color,
            'font_size': font_size,
            'font': font,
            'shadow_color': shadow_color,
            'shadow_offset': shadow_offset,
            'shadow_blur_radius': shadow_blur_radius,
            'shadow_alpha': shadow_alpha,
            'font_alpha': font_alpha
        })

    def clearSubtitle(self):
        """
        Clears the subtitle text.
        """
        self._overlay_process._parent_conn.send({'action': 'clear'})

    def dispose(self):
        """
        Disposes of the overlay process and window.
        """
        self._overlay_process.dispose()

class TransparentWindow(Cocoa.NSWindow):
    """
    A custom NSWindow subclass that creates a transparent window.
    """

    def initWithContentRect_styleMask_backing_defer_(self, contentRect, styleMask, backing, defer):
        super_init = objc.super(TransparentWindow, self).initWithContentRect_styleMask_backing_defer_
        self = super_init(contentRect, Cocoa.NSWindowStyleMaskBorderless, backing, defer)
        if self:
            self.setLevel_(Quartz.kCGScreenSaverWindowLevel)
            self.orderOut_(self)
            self.orderFront_(None)
            self.resignKeyWindow()
            self.resignMainWindow()
            self.setOpaque_(False)
            self.setBackgroundColor_(Cocoa.NSColor.clearColor())
            self.setIgnoresMouseEvents_(True)
            self.hidesOnDeactivate = False
            self.setHasShadow_(True)
            self.setCollectionBehavior_(Quartz.NSWindowCollectionBehaviorCanJoinAllSpaces | Quartz.NSWindowCollectionBehaviorStationary)
            self.setIgnoresMouseEvents_(True)
        return self

    def canBecomeKeyWindow_(self, keyWindow):
        return False

if __name__ == '__main__':
    # The same testing block as provided, with modifications to include the new parameters
    overlay = SubtitleOverlay()
    overlay.setSubtitle("This is a test\nwith multiple lines\nof text.", font_size=44)
    import time
    time.sleep(1)
    overlay.setSubtitle("Customized text", text_color='red', font_size=44, font='Arial', shadow_color='yellow', shadow_offset=(4.0, -4.0), shadow_blur_radius=3, shadow_alpha=1.0, font_alpha=0.8)
    time.sleep(5)
    overlay.clearSubtitle()
    time.sleep(5)
    overlay.dispose()